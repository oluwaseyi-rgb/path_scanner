#!/usr/bin/env python3
"""
Path Scanner - Active path/directory discovery tool
Author: Built for Oluwaseyi's bug bounty recon workflow

Scans a target domain against a wordlist to discover active/valid paths
(directories, files, endpoints) using concurrent HTTP requests.

Usage:
    python3 path_scanner.py -u https://target.com -w wordlist.txt
    python3 path_scanner.py -u https://target.com -w wordlist.txt -t 20 -o results.txt
    python3 path_scanner.py -u https://target.com -w wordlist.txt -x php,html,bak
"""

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("[!] Missing dependency. Install with: pip install requests --break-system-packages")
    sys.exit(1)

# Suppress SSL warnings for targets with self-signed/invalid certs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_wordlist(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return [line.strip().lstrip("/") for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print(f"[!] Wordlist not found: {path}")
        sys.exit(1)


def build_paths(words, extensions):
    paths = set(words)
    if extensions:
        for w in words:
            for ext in extensions:
                paths.add(f"{w}.{ext.lstrip('.')}")
    return sorted(paths)


def check_path(base_url, path, timeout, headers, follow_redirects):
    url = urljoin(base_url + "/", path)
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers=headers,
            verify=False,
            allow_redirects=follow_redirects,
        )
        return (url, resp.status_code, len(resp.content))
    except requests.exceptions.RequestException:
        return None


def scan(base_url, words, threads, timeout, exclude_codes, extensions, headers, follow_redirects):
    paths = build_paths(words, extensions)
    total = len(paths)
    found = []

    print(f"[*] Target: {base_url}")
    print(f"[*] Wordlist entries (incl. extensions): {total}")
    print(f"[*] Threads: {threads}\n")

    start = time.time()
    completed = 0

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(check_path, base_url, p, timeout, headers, follow_redirects): p
            for p in paths
        }

        for future in as_completed(futures):
            completed += 1
            result = future.result()
            if result:
                url, status, size = result
                if status not in exclude_codes:
                    found.append((url, status, size))
                    print(f"[{status}] {url}  ({size} bytes)")

            if completed % 200 == 0 or completed == total:
                sys.stdout.write(f"\r[*] Progress: {completed}/{total}")
                sys.stdout.flush()

    elapsed = time.time() - start
    print(f"\n\n[*] Scan complete in {elapsed:.1f}s — {len(found)} active path(s) found.")
    return found


def main():
    parser = argparse.ArgumentParser(description="Active path/directory scanner")
    parser.add_argument("-u", "--url", required=True, help="Target base URL, e.g. https://target.com")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file")
    parser.add_argument("-t", "--threads", type=int, default=15, help="Number of concurrent threads (default: 15)")
    parser.add_argument("--timeout", type=float, default=5.0, help="Request timeout in seconds (default: 5)")
    parser.add_argument(
        "-e", "--exclude", default="404",
        help="Comma-separated status codes to exclude (default: 404)"
    )
    parser.add_argument(
        "-x", "--extensions", default="",
        help="Comma-separated extensions to append to each word, e.g. php,html,bak"
    )
    parser.add_argument("-o", "--output", help="File to save discovered paths")
    parser.add_argument(
        "-a", "--user-agent",
        default="Mozilla/5.0 (compatible; PathScanner/1.0)",
        help="Custom User-Agent header"
    )
    parser.add_argument(
        "--follow-redirects", action="store_true",
        help="Follow HTTP redirects (default: off, so 3xx are shown as-is)"
    )
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    exclude_codes = {int(c.strip()) for c in args.exclude.split(",") if c.strip()}
    extensions = [e.strip() for e in args.extensions.split(",") if e.strip()]
    headers = {"User-Agent": args.user_agent}

    words = load_wordlist(args.wordlist)

    found = scan(
        base_url, words, args.threads, args.timeout,
        exclude_codes, extensions, headers, args.follow_redirects
    )

    if args.output:
        with open(args.output, "w") as f:
            for url, status, size in sorted(found, key=lambda x: x[1]):
                f.write(f"[{status}] {url} ({size} bytes)\n")
        print(f"[*] Results saved to {args.output}")


if __name__ == "__main__":
    main()

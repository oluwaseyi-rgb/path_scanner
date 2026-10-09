# PathHound

**A fast, multithreaded web path and directory discovery tool for recon and bug bounty work.**

PathHound takes a target URL and a list of endpoints, requests each one concurrently, and reports which paths actually respond. It can also append file extensions to every entry, filter out unwanted status codes, and save results to a file.

---

## Important: You Need Your Own Endpoint List

PathHound **does not ship with a built-in wordlist**. The scanner is only as good as the endpoints you give it, so you must supply a custom wordlist with the `-w` flag on every run.

- The wordlist is a plain text file with **one path per line**
- Lines starting with `#` are ignored as comments
- Leading slashes are stripped automatically (`/admin` and `admin` are treated the same)
- Build lists tailored to your target: known API routes, framework-specific paths, endpoints found in JavaScript files, Wayback Machine URLs, or entries from public lists like SecLists

Example `endpoints.txt`:

```
# common paths
admin
login
api/v1/users
api/v2/health
.git/config
backup
config.json
```

---

## Features

- **Concurrent scanning**: configurable thread count (default 15)
- **Extension fuzzing**: append extensions like `php`, `html`, `bak` to every wordlist entry
- **Status code filtering**: hide noise such as 404s (or any codes you choose)
- **Redirect control**: 3xx responses are shown as-is by default, with an option to follow them
- **Custom User-Agent**: set your own header string
- **Self-signed certificate friendly**: SSL verification is disabled so internal and staging targets still work
- **Live progress counter** and scan timing
- **Save results** to a file, sorted by status code

---

## Requirements

- Python 3.7+
- `requests`

```bash
pip install requests
```

---

## Usage

```bash
python3 path_scanner.py -u https://target.com -w endpoints.txt
```

### Options

| Flag | Description | Default |
|---|---|---|
| `-u`, `--url` | Target base URL (required) | none |
| `-w`, `--wordlist` | Path to your custom endpoint list (required) | none |
| `-t`, `--threads` | Number of concurrent threads | `15` |
| `--timeout` | Request timeout in seconds | `5` |
| `-e`, `--exclude` | Comma-separated status codes to hide | `404` |
| `-x`, `--extensions` | Comma-separated extensions to append to each word | none |
| `-o`, `--output` | File to save discovered paths | none |
| `-a`, `--user-agent` | Custom User-Agent header | `Mozilla/5.0 (compatible; PathScanner/1.0)` |
| `--follow-redirects` | Follow HTTP redirects | off |

### Examples

Basic scan:

```bash
python3 path_scanner.py -u https://target.com -w endpoints.txt
```

Faster scan, saving results:

```bash
python3 path_scanner.py -u https://target.com -w endpoints.txt -t 30 -o results.txt
```

Try file extensions on every entry:

```bash
python3 path_scanner.py -u https://target.com -w endpoints.txt -x php,html,bak
```

Hide multiple status codes:

```bash
python3 path_scanner.py -u https://target.com -w endpoints.txt -e 404,403,500
```

---

## Example Output

```
[*] Target: https://target.com
[*] Wordlist entries (incl. extensions): 42
[*] Threads: 15

[200] https://target.com/login  (4821 bytes)
[301] https://target.com/admin  (0 bytes)
[403] https://target.com/backup  (199 bytes)
[*] Progress: 42/42

[*] Scan complete in 3.4s — 3 active path(s) found.
```

---

## Reading the Results

| Status | Typically means |
|---|---|
| `200` | Path exists and is accessible |
| `301` / `302` | Path exists but redirects (often to a login page or trailing-slash version) |
| `401` / `403` | Path exists but access is restricted, which is worth a closer look |
| `500` | Server error triggered, which can indicate interesting behavior |

Some sites return `200` for every request (a "soft 404"). If you see suspiciously many hits with identical byte sizes, filter by size or exclude that status code.

---

## Limitations

- Only checks paths from your wordlist, so it does not crawl or discover links on its own
- Uses GET requests only
- Very high thread counts can trigger rate limiting or WAF blocks, so tune `-t` to the target
- Failed or timed-out requests are skipped silently

---

## Legal & Ethical Use

Only scan systems you own or have explicit authorization to test, such as targets within the scope of a bug bounty program. Always follow the program's rules on rate limits and allowed testing. Unauthorized scanning may be illegal. The author is not responsible for misuse of this tool.

---

## Author

**Oladunni Oluwaseyi**
GitHub: [@oluwaseyi-rgb](https://github.com/oluwaseyi-rgb)
LinkedIn: [Oluwaseyi Oladunni](https://www.linkedin.com/in/oluwaseyi-oladunni-6a42b1407)

---

## License

Released under the MIT License.

## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - NaN and Infinity Bypassing Bounds Checks
**Vulnerability:** Input validation logic allowed non-finite floats (`float('nan')`, `float('inf')`) to bypass bounds checking (e.g., `< MIN_PRICE`, `> MAX_QUANTITY`) since comparisons involving NaN often return False in Python. This could lead to infinite quantities or NaN prices being passed to API endpoints.
**Learning:** Standard comparison operators (`<`, `>`, `<=`, `>=`) are insufficient for validating float inputs because they do not protect against IEEE 754 non-finite values (NaN and Infinity), which fail comparisons silently.
**Prevention:** Always use `math.isfinite()` when validating numeric float inputs from untrusted sources before applying bounds checks.

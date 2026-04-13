## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - NaN Bypass Vulnerability in Boundary Checks
**Vulnerability:** Input validation boundaries in `src/validation.py` could be bypassed using `float('nan')` or `float('inf')` values for quantities, prices, stop prices, and percentages.
**Learning:** Python's floating-point operations treat `NaN` carefully. Any inequality comparison involving `NaN` (e.g., `NaN > MAX_QUANTITY` or `NaN <= 0`) evaluates to `False`. Thus, `NaN` easily evades `if value > MAX` and `if value < MIN` validations, flowing into the application logic unexpectedly.
**Prevention:** Always validate floating-point inputs to ensure they are finite numbers by using `math.isfinite(value)` before performing boundary checks.

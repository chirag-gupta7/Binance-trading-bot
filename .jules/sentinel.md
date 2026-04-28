## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.
## 2024-05-24 - Input Validation Bypass via NaN/Inf
**Vulnerability:** Input validation boundaries (e.g., minimum and maximum bounds for quantity, price, percentage, etc.) could be bypassed by passing `float('nan')` or `float('inf')` values. Comparisons like `qty <= 0` evaluate to `False` for `nan`, bypassing the check entirely.
**Learning:** Python's floating-point handling treats `nan` differently in comparisons, meaning simple bounds checks aren't sufficient if `nan` isn't explicitly rejected. This allows invalid inputs to flow to the API or subsequent layers.
**Prevention:** Use `math.isfinite()` immediately after casting user input to a float, before performing any range bounds checks.

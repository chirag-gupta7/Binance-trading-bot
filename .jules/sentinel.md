## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - Python Float NaN and Infinity Bypassing Bounds Checks
**Vulnerability:** Input validation for floats (quantities, prices, percentages) failed to catch `float('nan')` and `float('inf')`. Because Python's `NaN` returns `False` for any standard comparison operator (`<`, `>`, `<=`, `>=`), bounds checking (e.g., `qty < MIN_QUANTITY` or `qty > MAX_QUANTITY`) is entirely bypassed if the input evaluates to `NaN`.
**Learning:** Checking bounds using less than and greater than operators on unvalidated floats allows unexpected non-numeric values like `NaN` and `Inf` to pass through validators.
**Prevention:** Explicitly check for `NaN` and `Inf` using `math.isnan()` and `math.isinf()` early in validation routines before proceeding to bounds checking.

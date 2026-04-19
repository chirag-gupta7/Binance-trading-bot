## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - Input Validation Bypass via Non-Finite Floats
**Vulnerability:** Numerical input validation (e.g., in `validate_quantity`, `validate_price`, `validate_percentage`, and `validate_stop_price`) was vulnerable to bypass using `float('nan')` or `float('inf')`. Since `nan < value` or `nan > value` always evaluate to `False`, `nan` could bypass range bounds checking.
**Learning:** Python's floating-point handling allows `NaN` and `Infinity` inputs, which can bypass simple comparison operators like `<`, `<=`, `>`, `>=` used in bounds validation logic.
**Prevention:** Always use `math.isfinite(value)` on numerical user inputs before performing bounds checking to explicitly reject `NaN` and `Infinity` values.

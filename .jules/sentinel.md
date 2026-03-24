## 2026-03-24 - NaN Input Validation Bypass
**Vulnerability:** A logic bypass vulnerability was identified in numeric validation functions where casting strings like 'nan' to `float` resulted in `float('nan')`. Any comparison operators (`<`, `>`, `<=`, `>=`) performed against `NaN` evaluate to `False`, allowing bounds checks like `value <= 0` or `value > MAX` to be fully bypassed.
**Learning:** Python's floating-point type correctly implements IEEE 754 logic for `NaN`. Standard numerical comparison operators alone are insufficient to secure a range constraint. Input values must explicitly be checked to ensure they are standard numbers.
**Prevention:** Use `math.isnan(value)` and `math.isinf(value)` to explicitly filter out `NaN` and `Infinity` immediately after casting to `float`, and prior to any standard numerical comparisons.

## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

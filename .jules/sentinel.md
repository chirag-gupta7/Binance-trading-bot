## 2026-04-06 - Input Validation Bypass via float('nan') and float('inf')
**Vulnerability:** Numerical inputs parsed with `float()` in Python can accept special string values like `"nan"` and `"inf"`. These values bypass basic boundary checks (e.g., `val <= 0`, `val > MAX_VAL`) because comparisons involving NaN always return `False`. This allowed invalid quantities and prices to pass validation and be sent to external APIs or used in calculations.
**Learning:** Checking for positive values (`val <= 0`) or maximum limits (`val > MAX`) is insufficient for float inputs in Python, as special IEEE 754 float values behave counter-intuitively in comparisons.
**Prevention:** Always use `math.isfinite(val)` after parsing float inputs to explicitly reject NaN and Infinity before performing any logical boundary or range checks.

## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

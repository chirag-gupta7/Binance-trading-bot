## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.
## 2024-05-23 - [Input Validation Bypass via NaN/Inf]
**Vulnerability:** In Python, passing `float('nan')` or `float('inf')` to validation methods bypassed boundary checks (e.g., `< MIN` or `> MAX`) because comparisons with `nan` always return `False`. This could allow out-of-bounds orders or malicious input to bypass safety checks.
**Learning:** Standard typecasting to `float()` combined with boundary checks is insufficient in Python because of special IEEE 754 float values (`nan` and `inf`). This is a unique vulnerability pattern that must be explicitly checked.
**Prevention:** Always use `math.isnan()` and `math.isinf()` alongside typecasting and boundary checks when validating numerical inputs from untrusted sources.

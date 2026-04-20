## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.
## 2024-05-24 - Input Validation Bypass via float('nan') / float('inf')
**Vulnerability:** Input validation boundaries could be bypassed using Python `float('nan')` or `float('inf')` values due to how they are evaluated in comparison operations (e.g. `nan > 0` returns `False`).
**Learning:** Checking bounds `value <= 0` or `value > MAX` is insufficient for `float` input in Python since `NaN` evaluates to `False` for basic greater-than or less-than comparisons, successfully bypassing maximum constraints or logic checks.
**Prevention:** Always validate that numerical values are finite (`math.isfinite(value)`) before applying boundary limits, ensuring `NaN` and `Infinity` are rejected explicitly.

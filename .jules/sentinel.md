## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-09 - Validation Bypass via Floating-Point NaN
**Vulnerability:** Input validation for numeric boundaries (min/max) could be bypassed by supplying `NaN` values, as `NaN` comparisons always return `False`.
**Learning:** Relying purely on `<` or `>` comparison checks for float values is insufficient if the language permits `NaN` or `Infinity`, which sidestep logical bounds.
**Prevention:** Always validate numeric types with `math.isfinite()` immediately after type coercion, before performing boundary checks.

## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-04 - NaN Input Validation Bypass
**Vulnerability:** Input validation functions for numerical values (e.g. quantity, price) relied on inequality checks (e.g. `qty <= 0`) which silently evaluate to `False` for `float('nan')`, effectively bypassing minimum and maximum bounds checking.
**Learning:** Python's floating-point comparison semantics allow `NaN` to bypass standard boundary constraints because `NaN < x` and `NaN > x` are both `False`.
**Prevention:** Always use `math.isfinite()` on floating-point user inputs to proactively reject `NaN` and `Inf` before performing boundary checks.

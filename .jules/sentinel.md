## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2026-04-17 - Bypassing bounds validation with NaN/Infinity
**Vulnerability:** Input validation utilizing standard boundary checking (e.g., `qty <= 0` or `qty > MAX`) allows passing `float('nan')` and `float('inf')`. Python's `float()` function allows `NaN` and `Infinity` parsing from string types. `NaN` comparisons return `False`, which essentially bypasses the length or boundary validation.
**Learning:** Checking for positive values or upper limits fails against `NaN` as `NaN < limit` and `NaN > limit` both evaluates to `False`. Thus these values evade detection and get passed to other routines like calculations or downstream APIs causing exceptions, infinite loops, or unexpected trading behaviors.
**Prevention:** Use `math.isnan()` and `math.isinf()`, or just `math.isfinite()`, to reject these specific inputs prior to standard comparison constraints.

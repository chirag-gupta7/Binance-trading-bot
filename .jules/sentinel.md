## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2026-04-08 - Bypassing Range Checks via float('nan')
**Vulnerability:** In `src/validation.py`, standard numerical validations (e.g., `< 0`, `> MAX_QUANTITY`) could be trivially bypassed by passing `float('nan')` since comparing `nan` via `<`, `<=`, `>`, or `>=` always evaluates to `False`. This potentially allowed invalid sizes, negative quantities, or invalid percentages into the trading system.
**Learning:** `float('nan')` behavior allows variables to silently fail limit-bound checks without raising an exception or triggering a standard check condition.
**Prevention:** Always validate floating-point bounds or sizes with `math.isfinite()` prior to range/bound assertions to properly detect and reject Inf and NaN float inputs.

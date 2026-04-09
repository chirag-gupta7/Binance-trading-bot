## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.
## 2026-04-09 - [Input Validation Bypass via NaN/Inf]
**Vulnerability:** Python `float()` accepts 'nan', 'inf', and '-inf' strings. These values bypass numeric bound checks (e.g., `nan > 100` evaluates to `False`), allowing invalid inputs to bypass constraints.
**Learning:** Checking bounds using `<` and `>` is insufficient when inputs are untrusted and parsed using `float()`. Bypassing this could lead to API rejections or unexpected mathematical errors downstream in the bot.
**Prevention:** Always use `math.isfinite()` on user-supplied numbers right after `float()` casting to ensure the number is valid and within expected mathematical constraints before performing limit checks.

## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-25 - NaN and Inf Validation Bypass in Python
**Vulnerability:** Python's `float('nan')` bypasses standard inequality checks (`<= 0`, `< MIN`, `> MAX` all evaluate to `False`). This allowed invalid float representations to bypass bounds checking in `src/validation.py`, potentially sending invalid parameters to the exchange.
**Learning:** Standard comparison operators are insufficient for verifying float bounds in Python due to IEEE 754 NaN behavior.
**Prevention:** Always use `math.isfinite(value)` or `math.isnan(value)` to explicitly validate float inputs before performing bounds checking.

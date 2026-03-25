## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2026-03-25 - NaN Validation Bypass
**Vulnerability:** A vulnerability existed in input validation where floating-point numbers containing `NaN` (Not a Number) or `Infinity` bypassed the min/max numerical bounds checks because comparisons like `nan <= 0` or `nan > 100` always evaluate to `False` in Python.
**Learning:** Relying solely on numerical comparison operators (`<`, `>`, `<=`, `>=`) is insufficient for validating untrusted floating-point inputs, as `NaN` and `Infinity` can pass through these checks unchallenged and cause undefined behavior downstream.
**Prevention:** When parsing and validating user-provided floating-point numbers, explicitly check for `NaN` and `Infinity` using `math.isnan()` and `math.isinf()` before applying any bounds checks.

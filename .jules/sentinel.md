## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - Input Validation Bypass (float('nan') and float('inf'))
**Vulnerability:** The bot allowed the Python special float values `nan` and `inf` to bypass traditional greater-than/less-than boundary checks in input validation (e.g. `qty <= 0`). Since `nan > 10` is `False`, and `nan <= 0` is also `False`, it skipped through boundary constraints intended to cap inputs.
**Learning:** Python's built-in bounds checking operators return `False` when comparing numbers against `nan` values, leading to silent constraint bypass for fields parsing float inputs.
**Prevention:** Explicitly use `math.isfinite(val)` to check numeric parameters in validation logic before performing any bounds or constraint checking on user inputs.

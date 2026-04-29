## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - Input Validation Float Bounds Checking Bypass
**Vulnerability:** Input validation logic in `src/validation.py` uses `float()` conversion which permits 'nan' and 'inf' string values. Specifically, 'nan' bypasses subsequent > and < bounds checks because any comparison with 'nan' evaluates to False, allowing invalid quantities and prices to be passed to the API.
**Learning:** Relying solely on `float()` conversion and standard comparison operators is insufficient for bounding numerical inputs, as special IEEE 754 float values ('nan', 'inf') circumvent standard algebraic comparison logic.
**Prevention:** After casting inputs to float, explicitly check that the resulting values are finite using `math.isfinite(val)` before proceeding with range validations.

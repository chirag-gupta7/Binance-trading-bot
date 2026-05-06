## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.
## 2024-05-24 - Input Validation Bypass (NaN/Inf)
**Vulnerability:** The custom input validation logic in src/validation.py used standard relational operators (e.g., <=, <) to enforce boundaries. Because float comparisons with float('nan') evaluate to False, attackers could bypass size limitations (e.g., maximum quantities or minimum prices) by injecting nan or inf values.
**Learning:** Mathematical validation requires explicit checks for finite values; boundary comparison operators alone do not catch infinite or not-a-number anomalies in floating point input.
**Prevention:** Always use math.isfinite() immediately after casting an input to float to ensure the value is a valid numeric scalar before checking boundary conditions.

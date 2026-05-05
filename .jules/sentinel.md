## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - NaN/Inf Bounds Checking Bypass in Input Validation
**Vulnerability:** Input validation functions in `src/validation.py` used `float()` conversion followed by simple comparison operators (`<`, `>`, `<=`) for bounds checking. Because any comparison with `float('nan')` evaluates to `False`, `nan` inputs bypassed all min/max and positivity checks.
**Learning:** Python's `float()` accepts string representations of 'nan', 'inf', and '-inf'. Simple numerical boundary checks are insufficient because `nan < MIN` and `nan > MAX` are both `False`.
**Prevention:** Always use `math.isfinite()` to validate that a parsed float is a real number before applying numerical boundary checks or using it in further logic.

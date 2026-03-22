## 2024-05-25 - Python Float NaN/Inf Validation Bypass
**Vulnerability:** Python's `float('nan')` and `float('inf')` values bypass standard numeric inequality checks (e.g., `> 0`, `< MAX_QUANTITY`). This allowed validation functions to pass these values, potentially causing unexpected behavior or security issues down the line.
**Learning:** Always explicitly check for `NaN` and `Infinity` using `math.isnan()` and `math.isinf()` when validating numeric inputs that are converted to floats, as they behave unpredictably in inequality expressions.
**Prevention:** Implement explicit `math.isnan()` and `math.isinf()` checks early in validation logic for all float inputs.

## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

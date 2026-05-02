## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2026-05-02 - Floating Point Validation Bypass Prevention (NaN/Inf)
**Vulnerability:** In `src/validation.py`, input validation logic allowed bypassing minimum and maximum boundary checks when floating point values like `NaN` (Not a Number) were passed. Since comparisons like `nan < 0` evaluate to `False`, the checks were completely evaded.
**Learning:** Using basic comparators (`<`, `>`, `<=`, `>=`) against variables cast to floats is insufficient when the inputs can be `NaN` or `Infinity`, which are valid float representations in Python.
**Prevention:** Always use `math.isfinite(value)` after casting to float in input validation to ensure the parsed value is a regular number before performing bounds checking.

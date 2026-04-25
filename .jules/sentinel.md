## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2026-04-25 - Python Float Validation Bypass via NaN/Inf
**Vulnerability:** In `src/validation.py`, bounds checking (e.g. `qty <= 0`) for user inputs was bypassed when values like `float('nan')` or `float('inf')` were passed. In Python, comparisons with `nan` generally evaluate to `False`, skipping standard range validation checks.
**Learning:** Standard boundary checks (`<`, `>`, `<=`, `>=`) are insufficient for comprehensive float validation in Python because they do not account for Not-a-Number (`nan`) or Infinity (`inf`). This allows malicious inputs to bypass validation entirely.
**Prevention:** Always use `math.isfinite()` when validating float inputs to guarantee that the value is a valid real number before performing boundary logic checks.

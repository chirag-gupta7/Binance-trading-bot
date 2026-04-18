## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-29 - Input Validation Bypass via NaN/Infinity
**Vulnerability:** The input validation logic in `src/validation.py` for floats (quantities, prices, percentages) failed to check for non-finite values (like `NaN` or `Infinity`). Because Python evaluates comparisons with `NaN` (e.g., `nan <= 0`, `nan < min_value`) as `False`, an attacker could pass `float('nan')` to bypass all boundary checks.
**Learning:** Checking types and casting to `float` is insufficient when dealing with untrusted float input in Python. `float('nan')` and `float('inf')` are valid floats but break boundary logic.
**Prevention:** Always use `math.isfinite(value)` on parsed float inputs before performing boundary limit checks to ensure the value is a real, bounded number.

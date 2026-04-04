## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - Input Validation Bypass via NaN/Inf (Float Parsing)
**Vulnerability:** The input validation logic for numerical parameters (quantity, price, stop price, percentage) used `float()` parsing which successfully converts strings like `"nan"`, `"inf"`, or `"-inf"` into valid floats. `NaN` breaks arithmetic comparisons (e.g., `nan <= 0` is `False`), effectively bypassing minimum and maximum boundary checks.
**Learning:** Checking bounds on numbers is insufficient if the input can be parsed as `NaN` or `Inf`. Python's `float()` accommodates these special values, which can lead to logical bypasses in security or financial constraints.
**Prevention:** Always validate that parsed numerical inputs are finite using `math.isfinite()` before executing business logic checks. For instance, `if not math.isfinite(val): raise ValueError("Value must be finite")`.

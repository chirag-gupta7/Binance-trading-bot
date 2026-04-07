## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-11-04 - Input Validation Bypass via NaN/Infinity
**Vulnerability:** Input validation for float values in `src/validation.py` (e.g., quantities, prices) used `float()` which successfully parses 'nan' and 'inf' string inputs, bypassing numeric range checks (e.g., `if qty <= 0` evaluates to False for NaN).
**Learning:** Python's built-in `float()` function accepts special string values like 'nan', 'inf', and '-inf'. This can lead to unexpected behavior and bypass security checks that assume valid, finite numeric inputs, potentially causing downstream errors or logic flaws.
**Prevention:** Always use `math.isfinite()` alongside `float()` when converting and validating external string inputs intended to be standard numeric values, ensuring they are not NaN or Infinity.

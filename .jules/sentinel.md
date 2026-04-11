## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-18 - Validation Bypass via NaN/Inf
**Vulnerability:** Input validation bypassed constraints using `float('nan')` or `float('inf')` values. Python floats allow for special cases like NaN or Inf. Because `float(value)` parses strings like `"nan"` correctly, comparing `nan > max` evaluates to False, bypassing bound checks in methods like `validate_quantity`, `validate_price`, `validate_stop_price`, and `validate_percentage`.
**Learning:** `float(val)` will happily accept `"nan"`, `"inf"`, and `"-inf"`. Bound checking like `qty <= 0` and `qty > OrderValidator.MAX_QUANTITY` will always return `False` when `qty` is `NaN`. This effectively allows validation bypass when passing `NaN` for bounds-checked parameters.
**Prevention:** Always validate that parsed floating point numbers are actually finite using `math.isfinite(val)` before performing logical boundary tests.

## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2026-04-15 - Input Validation Bypass via NaN/Infinity
**Vulnerability:** The application allowed users to bypass security limits (like maximum order quantity and maximum price) by supplying `NaN` or `Inf` as inputs. Python's `float()` successfully parses strings like `"NaN"` or `"Inf"`, and the standard `<` or `>` operators fail to block `NaN`.
**Learning:** Standard comparison operators are insufficient for verifying float boundaries because comparisons involving `NaN` generally evaluate to `False` (e.g. `float('nan') > 1000000` is `False`, allowing the limit check to pass).
**Prevention:** Always use `math.isfinite()` on numeric inputs, especially when validating boundaries, to prevent non-finite bypasses.

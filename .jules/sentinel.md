## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-20 - [Input Validation Bounds Checking Bypass via NaN]
**Vulnerability:** Numerical inputs (`quantity`, `price`, `stop_price`, `percentage`) in `src/validation.py` were not checked for `NaN` (Not a Number). Since `NaN < MIN` and `NaN > MAX` both evaluate to `False` in Python, this allowed `NaN` values to bypass bounds checking constraints completely and be accepted as valid inputs. `inf` and `-inf` also caused issues (either bypassing checks or causing unexpected exceptions).
**Learning:** Comparing against limits isn't sufficient for numerical validation in Python if the input type can be a float. `float('nan')` breaks standard relational operators, potentially leading to downstream calculation errors or crashes when passed to APIs.
**Prevention:** Always use `math.isfinite()` when validating float inputs to ensure they are standard numbers before applying range or bounds checking.

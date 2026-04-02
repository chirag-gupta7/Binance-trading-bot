## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-06-03 - NaN and Infinity Validation Bypass
**Vulnerability:** The input validation logic used `float()` which successfully parses `float('nan')` and `float('inf')`. When checking bounds like `qty < MIN` or `qty > MAX`, comparisons involving `NaN` evaluate to `False`, thereby bypassing the validation checks completely.
**Learning:** Python's built-in `float()` parser will happily parse NaN and Inf strings/types. Standard inequality bounds checks fail securely (in terms of evaluating to False) but this means NaN values are considered "valid" in logic where only bounded real numbers are expected, leading to unpredictable downstream behavior.
**Prevention:** Whenever parsing user input or external data into a floating-point number, immediately check if the value is finite using `math.isfinite(value)` before proceeding with any bounds checks or business logic.

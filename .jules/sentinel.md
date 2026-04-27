## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - NaN Bounds Checking Bypass
**Vulnerability:** Input validation logic for quantities, prices, and percentages failed to handle `float('nan')` and `float('inf')` values. `nan` bypassing `qty <= 0` or bounds checking like `qty < MIN` because comparisons with `nan` are always false, allowing `nan` to be returned as a valid quantity.
**Learning:** `float(quantity)` does not inherently reject non-finite numbers such as `nan` and `inf` which can lead to unexpected behaviors or errors later down the chain.
**Prevention:** Explicitly use `math.isfinite()` when parsing floating-point input before applying bound checks or assuming it represents a concrete value.

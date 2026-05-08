## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - Input Validation Bypass via NaN/Infinity
**Vulnerability:** Numerical input validation in `src/validation.py` (e.g., `validate_quantity`, `validate_price`) could be bypassed by passing `float('nan')`. Standard float comparisons (like `<` or `>`) involving NaN always return `False`, allowing NaN values to bypass minimum and maximum bounds checking.
**Learning:** When validating numerical inputs in Python, casting to `float` does not prevent `NaN` or `Infinity` (`Inf`). These special float values can subvert bounds checking logic and propagate downstream, potentially leading to logic errors or unexpected behavior in the application or API layer.
**Prevention:** Always use `math.isfinite()` to strictly ensure that float inputs are regular, finite numbers before performing bounds checking or using the values.

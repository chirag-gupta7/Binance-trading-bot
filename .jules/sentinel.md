## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-01 - [Validation Bypass via NaN/Infinity in Float Conversions]
**Vulnerability:** Python float bounds checking (e.g., `<` and `>`) returns `False` when comparing with `float('nan')`, which bypasses minimum and maximum constraints in validation functions like `validate_quantity` and `validate_price`.
**Learning:** Standard comparison operators are insufficient for verifying numeric inputs if the value can be evaluated to `NaN`. This allows unexpected negative infinities or `NaN`s to propagate to external API calls.
**Prevention:** Always use `math.isfinite()` after casting strings to floats and before performing bounds checking to explicitly reject `NaN` and `Infinity`.

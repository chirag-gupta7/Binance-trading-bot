## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-25 - Python Float bounds checking bypass via NaN and Infinity
**Vulnerability:** Input validation logic for quantities, prices, etc. accepted strings that could be parsed by `float()`, which includes 'nan' and 'inf'. Because comparisons with `float('nan')` always evaluate to `False` (e.g. `float('nan') < 0` is `False` and `float('nan') > MAX_VALUE` is `False`), the values could bypass min/max boundary checks.
**Learning:** Checking bounds using `<` and `>` is insufficient when the variable might be `NaN` or `Infinity`, because standard logic statements won't trigger for these edge cases.
**Prevention:** Always explicitly check for finite numbers when validating user-supplied floats, specifically using `math.isnan()` and `math.isinf()`.

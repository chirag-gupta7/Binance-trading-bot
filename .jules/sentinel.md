## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-25 - NaN and Inf Bounds Checking Bypass
**Vulnerability:** The application was not rejecting `NaN` and `Inf` float values in its order validation logic. This allowed these values to bypass typical numerical bounds checking (like `value > 0`), which could lead to malformed orders being processed by downstream systems or the API.
**Learning:** `float('nan')` and `float('inf')` do not behave like standard numbers in comparisons. For example, `float('nan') > 0` evaluates to `False`, bypassing upper limit checks if logic is not explicitly checking for it.
**Prevention:** When validating numerical inputs (like quantity or price) that come from user input or external APIs, always use `math.isnan()` and `math.isinf()` (or similar library functions) to explicitly reject these special float values before performing bounds checking.

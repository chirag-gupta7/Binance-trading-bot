## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2026-04-21 - NaN and Infinity Validation Bypass in Input Parsing
**Vulnerability:** Input validation functions parsing floats (`float()`) allowed `NaN` (Not a Number) and `Infinity` inputs. Python comparisons with `NaN` (e.g., `NaN < MIN`, `NaN > MAX`) always return `False`, which completely bypassed the bounds checking and min/max constraints, potentially allowing malicious or anomalous inputs to be passed to the backend API.
**Learning:** Checking bounds is insufficient for floats because `NaN` behaves uniquely in Python. A separate finiteness check is required to ensure standard arithmetic and bounds operations behave securely.
**Prevention:** Always use `math.isfinite(value)` alongside type casting (`float()`) and bounds checking when validating numerical inputs from untrusted or external sources.

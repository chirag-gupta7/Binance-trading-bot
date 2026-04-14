## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-18 - [NaN Validation Bypass in Order Amounts]
**Vulnerability:** The input validation for `quantity`, `price`, `stop_price`, and `percentage` in `src/validation.py` incorrectly accepted `float('nan')` inputs. `nan` values circumvented the standard bounds checking operations (`nan <= 0`, `nan < MIN`, `nan > MAX` all evaluate to False), allowing malformed inputs to pass through to the Binance API.
**Learning:** Checking bounds using standard comparison operators (`<`, `>`, `<=`, `>=`) against `float` types is inadequate when special IEEE 754 floats such as NaN are introduced, as NaN comparisons evaluate to False. Relying solely on these operators introduces bypass vulnerabilities.
**Prevention:** Always validate that floating-point inputs represent finite numbers (i.e. rejecting NaN and Infinity) before performing numerical boundary checks, specifically using `math.isfinite()`.

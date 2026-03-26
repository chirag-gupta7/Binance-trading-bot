## 2024-05-24 - Log Injection Vulnerability Prevention
**Vulnerability:** A log injection vulnerability existed in `src/logger.py` where log inputs were not sanitized, allowing newline (`\n`) and carriage return (`\r`) characters to be inserted. This could allow an attacker to inject forged log entries.
**Learning:** This approach leaves the system vulnerable to attackers writing fake logs to masquerade their tracks or manipulate log analysis tools. Unsanitized strings passed to logging mechanisms are a common vector for log injection.
**Prevention:** Sanitize inputs to logging functions. Implement an internal `_sanitize` method (e.g., replacing `\n` with `\\n` and `\r` with `\\r`) inside the central logger, ensuring every log message flows through this sanitization before reaching the underlying logger library.

## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

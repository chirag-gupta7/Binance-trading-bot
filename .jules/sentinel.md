## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - Log Injection Vulnerability Prevention
**Vulnerability:** The logger in `src/logger.py` did not sanitize input strings before writing them to the log file. An attacker could potentially embed newline `\n` or carriage return `\r` characters in the input to inject fake log entries, leading to log spoofing or splitting (CWE-117).
**Learning:** Log injection vulnerabilities are commonly overlooked when custom loggers pass user-controlled input directly to the underlying logging library. Input validation or escaping is required at the logging perimeter to ensure the integrity of audit trails.
**Prevention:** Introduce an explicit `_sanitize(self, message)` method that sanitizes incoming log messages by casting them to a string and escaping `\n` and `\r` characters. This method should be called uniformly across all logging levels (e.g., `info`, `error`, `warning`) before messages are dispatched to the handler.

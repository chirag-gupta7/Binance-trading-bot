## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2024-05-24 - Log Injection Prevention
**Vulnerability:** A log injection vulnerability existed in `src/logger.py` where log methods (`info`, `error`, etc.) were passing user-controlled messages directly to the underlying `logging` module. This allowed an attacker to inject `\n` and `\r` characters into log messages, forging new log entries or corrupting log files.
**Learning:** Python's standard `logging` module does not automatically escape control characters like newlines. If a logger writes to a plain text file, newlines in the input string will be written as actual newlines in the output file.
**Prevention:** Always sanitize log messages before passing them to the logger by replacing control characters with their escaped representations. A `_sanitize` method replacing `\n` with `\\n` and `\r` with `\\r` ensures that log entries remain on a single line and cannot be forged.

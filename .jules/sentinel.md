## 2024-05-24 - Secure File Creation Pattern (TOCTOU Prevention)
**Vulnerability:** A Time-of-Check to Time-of-Use (TOCTOU) vulnerability existed in `src/logger.py` where a log file was created using `Path.touch(exist_ok=True)` and subsequently its permissions were changed using `os.chmod(self.log_file, 0o600)`.
**Learning:** This approach leaves a brief window between the file's creation and the permissions change where a malicious actor could access or modify the file.
**Prevention:** Instead of separating the creation and permission modification, use `os.open` with the `os.O_CREAT` flag and directly specify the desired permissions (e.g., `0o600`). This ensures the file is created atomically with the correct permissions. For example: `fd = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)` followed by `os.close(fd)`.

## 2026-03-17 - Log Injection (Forging) Vulnerability
**Vulnerability:** A log injection (forging) vulnerability existed in `src/logger.py` where log messages were written to log files without sanitizing newline (`\n`) or carriage return (`\r`) characters. This allows an attacker who controls the input to potentially inject fake log entries.
**Learning:** This architectural gap means logs cannot be fully trusted if input that is written to them is not sanitized properly. Unsanitized data logged as string interpolations can directly manipulate the output log structure.
**Prevention:** Introduce a sanitization step prior to any final log writing. Use string replacement `message.replace('\n', '\\n').replace('\r', '\\r')` before passing variables to logging output channels.

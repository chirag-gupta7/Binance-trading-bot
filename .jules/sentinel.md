## 2024-03-06 - [Log File Local File Inclusion/Information Disclosure Prevention]
**Vulnerability:** Trading data and potential parameters dumps were written to a log file without restrictive permissions, making it readable by all users on the same machine.
**Learning:** Even default file writes need explicit permission boundaries (e.g. `0o600`) when dealing with financial/trading information.
**Prevention:** Always restrict file permissions explicitly when creating files intended to store sensitive system or personal data.

## 2024-05-24 - Missing Timeout on External API Calls
**Vulnerability:** External API calls to Binance Futures using `UMFutures` lacked an explicit timeout setting.
**Learning:** Default external API wrappers may default to indefinite connection/read timeouts. If the API is slow or stops responding, the application execution flow hangs indefinitely, leading to resource exhaustion or denial-of-service conditions.
**Prevention:** Always define explicit connection and read timeouts (e.g., `timeout=10`) when initializing external API clients or making HTTP requests.

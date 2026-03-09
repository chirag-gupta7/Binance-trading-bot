## 2026-03-09 - [Added Timeout to External API Client]
**Vulnerability:** The Binance Futures API client (`UMFutures` in `src/api_client.py`) was initialized without a timeout parameter.
**Learning:** External API dependencies without explicit timeouts can cause the application to hang indefinitely if the external service experiences network issues or delays. This is a potential Denial of Service (DoS) risk that can consume resources.
**Prevention:** Always configure explicit timeouts when initializing external API clients or making HTTP requests.

## 2024-05-24 - [Add Timeout to External API Call]
**Vulnerability:** The Binance Futures API client (`UMFutures`) was instantiated without an explicit timeout parameter.
**Learning:** By default, if a timeout is not specified, Python's underlying socket operations (and thus the requests library) can block indefinitely if the server accepts the connection but never sends a response. In a trading bot, this could lead to the bot hanging, failing to execute subsequent critical operations (like stop losses), and potentially causing severe financial loss or resource exhaustion.
**Prevention:** Always explicitly configure a `timeout` parameter (e.g., `timeout=10`) when initializing external API clients or making network requests.

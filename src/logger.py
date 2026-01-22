"""
Structured logging module for Binance Futures Trading Bot
Provides centralized logging with timestamps and error tracing
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class BotLogger:
    """Centralized logger for the trading bot"""

    def __init__(self, log_file="bot.log"):
        self.log_file = log_file
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Configure logger with file and console handlers"""
        logger = logging.getLogger("BinanceFuturesBot")
        logger.setLevel(logging.DEBUG)

        # File handler with detailed format
        file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler with simpler format
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Detailed format for file
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Simpler format for console
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def info(self, message):
        """Log info level message"""
        self.logger.info(message)

    def error(self, message, exc_info=False):
        """Log error level message with optional traceback"""
        self.logger.error(message, exc_info=exc_info)

    def warning(self, message):
        """Log warning level message"""
        self.logger.warning(message)

    def debug(self, message):
        """Log debug level message"""
        self.logger.debug(message)

    def critical(self, message):
        """Log critical level message"""
        self.logger.critical(message)

    def log_order(self, order_type, symbol, side, quantity, params=None):
        """Log order placement with details"""
        msg = f"ORDER PLACED: {order_type} | {symbol} | {side} | Qty: {quantity}"
        if params:
            msg += f" | Params: {params}"
        self.info(msg)

    def log_execution(self, order_id, status, fill_price=None, qty_filled=None):
        """Log order execution details"""
        msg = f"ORDER EXECUTION: ID={order_id} | Status={status}"
        if fill_price:
            msg += f" | Fill Price: {fill_price}"
        if qty_filled:
            msg += f" | Qty Filled: {qty_filled}"
        self.info(msg)

    def log_validation_error(self, field, value, reason):
        """Log validation errors"""
        self.error(f"VALIDATION ERROR | Field: {field} | Value: {value} | Reason: {reason}")

    def log_api_call(self, endpoint, method, data=None):
        """Log API calls"""
        msg = f"API CALL | Method: {method} | Endpoint: {endpoint}"
        if data:
            msg += f" | Data: {data}"
        self.debug(msg)

    def log_api_response(self, endpoint, status_code, response_data=None):
        """Log API responses"""
        msg = f"API RESPONSE | Endpoint: {endpoint} | Status: {status_code}"
        if response_data:
            msg += f" | Response Keys: {list(response_data.keys()) if isinstance(response_data, dict) else type(response_data)}"
        self.debug(msg)


# Global logger instance
_logger_instance = None


def get_logger(log_file="bot.log"):
    """Get or create global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = BotLogger(log_file)
    return _logger_instance

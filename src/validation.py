"""
Input validation module for Binance Futures Trading Bot
Validates symbols, quantities, prices, and order parameters
"""

from typing import Tuple, Dict, Any, Optional
from logger import get_logger

logger = get_logger()


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class OrderValidator:
    """Centralized validation for order parameters"""

    # Common USDT-M trading pairs
    VALID_SYMBOLS = {
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOGEUSDT',
        'XRPUSDT', 'MATICUSDT', 'SOLUSDT', 'LTCUSDT', 'LINKUSDT',
        'AVAXUSDT', 'ATOMUSDT', 'ARBUSDT', 'UNIUSDT', 'APTUSDT',
        'GALAUSDT', 'OPUSDT', 'GMXUSDT', 'RDNTUSDT', 'PEPEUSDT'
    }

    VALID_SIDES = {'BUY', 'SELL'}
    VALID_ORDER_TYPES = {'MARKET', 'LIMIT', 'STOP_LIMIT', 'OCO', 'TWAP', 'GRID'}

    # Min/Max constraints
    MIN_QUANTITY = 0.001
    MAX_QUANTITY = 1000000
    MIN_PRICE = 0.00001
    MAX_PRICE = 999999

    @staticmethod
    def validate_symbol(symbol: str) -> str:
        """
        Validate trading pair symbol.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            
        Returns:
            Validated symbol (uppercase)
            
        Raises:
            ValidationError: If symbol is invalid
        """
        if not symbol or not isinstance(symbol, str):
            raise ValidationError(f"Symbol must be a non-empty string, got: {symbol}")

        symbol = symbol.upper()

        if symbol not in OrderValidator.VALID_SYMBOLS:
            available = ', '.join(sorted(OrderValidator.VALID_SYMBOLS))
            raise ValidationError(
                f"Symbol '{symbol}' not supported. Available: {available}"
            )

        logger.debug(f"Symbol validation passed: {symbol}")
        return symbol

    @staticmethod
    def validate_side(side: str) -> str:
        """
        Validate order side (BUY or SELL).
        
        Args:
            side: Order side
            
        Returns:
            Validated side (uppercase)
            
        Raises:
            ValidationError: If side is invalid
        """
        if not side or not isinstance(side, str):
            raise ValidationError(f"Side must be 'BUY' or 'SELL', got: {side}")

        side = side.upper()

        if side not in OrderValidator.VALID_SIDES:
            raise ValidationError(f"Side must be 'BUY' or 'SELL', got: {side}")

        logger.debug(f"Side validation passed: {side}")
        return side

    @staticmethod
    def validate_quantity(quantity: float, symbol: str = None) -> float:
        """
        Validate order quantity.
        
        Args:
            quantity: Order quantity
            symbol: Trading pair (optional, for logging)
            
        Returns:
            Validated quantity
            
        Raises:
            ValidationError: If quantity is invalid
        """
        try:
            qty = float(quantity)
        except (TypeError, ValueError):
            raise ValidationError(f"Quantity must be a number, got: {quantity}")

        if qty <= 0:
            raise ValidationError(f"Quantity must be positive, got: {qty}")

        if qty < OrderValidator.MIN_QUANTITY:
            raise ValidationError(
                f"Quantity {qty} below minimum {OrderValidator.MIN_QUANTITY}"
            )

        if qty > OrderValidator.MAX_QUANTITY:
            raise ValidationError(
                f"Quantity {qty} exceeds maximum {OrderValidator.MAX_QUANTITY}"
            )

        logger.debug(f"Quantity validation passed: {qty} {symbol or ''}")
        return qty

    @staticmethod
    def validate_price(price: float, symbol: str = None) -> float:
        """
        Validate price.
        
        Args:
            price: Price value
            symbol: Trading pair (optional, for logging)
            
        Returns:
            Validated price
            
        Raises:
            ValidationError: If price is invalid
        """
        try:
            p = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Price must be a number, got: {price}")

        if p <= 0:
            raise ValidationError(f"Price must be positive, got: {p}")

        if p < OrderValidator.MIN_PRICE:
            raise ValidationError(f"Price {p} below minimum {OrderValidator.MIN_PRICE}")

        if p > OrderValidator.MAX_PRICE:
            raise ValidationError(f"Price {p} exceeds maximum {OrderValidator.MAX_PRICE}")

        logger.debug(f"Price validation passed: {p} {symbol or ''}")
        return p

    @staticmethod
    def validate_stop_price(stop_price: float, entry_price: float, side: str) -> float:
        """
        Validate stop price logic.
        
        Args:
            stop_price: Stop price trigger
            entry_price: Entry/limit price
            side: BUY or SELL
            
        Returns:
            Validated stop price
            
        Raises:
            ValidationError: If stop price logic is invalid
        """
        try:
            stop = float(stop_price)
            entry = float(entry_price)
        except (TypeError, ValueError):
            raise ValidationError("Stop price and entry price must be numbers")

        side = side.upper()

        # For SELL stops (take-profit or stop-loss for shorts)
        if side == 'SELL':
            if stop <= entry:
                raise ValidationError(
                    f"For SELL orders, stop price ({stop}) must be > entry price ({entry})"
                )

        # For BUY stops
        elif side == 'BUY':
            if stop >= entry:
                raise ValidationError(
                    f"For BUY orders, stop price ({stop}) must be < entry price ({entry})"
                )

        logger.debug(f"Stop price validation passed: {stop}")
        return stop

    @staticmethod
    def validate_percentage(percentage: float) -> float:
        """
        Validate percentage value (0-100).
        
        Args:
            percentage: Percentage value
            
        Returns:
            Validated percentage
            
        Raises:
            ValidationError: If percentage is invalid
        """
        try:
            pct = float(percentage)
        except (TypeError, ValueError):
            raise ValidationError(f"Percentage must be a number, got: {percentage}")

        if pct <= 0 or pct > 100:
            raise ValidationError(f"Percentage must be between 0 and 100, got: {pct}")

        logger.debug(f"Percentage validation passed: {pct}%")
        return pct

    @staticmethod
    def validate_interval(interval: int) -> int:
        """
        Validate time interval in seconds.
        
        Args:
            interval: Time interval in seconds
            
        Returns:
            Validated interval
            
        Raises:
            ValidationError: If interval is invalid
        """
        try:
            intv = int(interval)
        except (TypeError, ValueError):
            raise ValidationError(f"Interval must be an integer, got: {interval}")

        if intv <= 0:
            raise ValidationError(f"Interval must be positive, got: {intv}")

        if intv < 1:  # Minimum 1 second
            raise ValidationError(f"Interval minimum is 1 second, got: {intv}")

        logger.debug(f"Interval validation passed: {intv}s")
        return intv

    @staticmethod
    def validate_order_type(order_type: str) -> str:
        """
        Validate order type.
        
        Args:
            order_type: Order type
            
        Returns:
            Validated order type
            
        Raises:
            ValidationError: If order type is invalid
        """
        if not order_type or not isinstance(order_type, str):
            raise ValidationError(f"Order type must be a string, got: {order_type}")

        order_type = order_type.upper()

        if order_type not in OrderValidator.VALID_ORDER_TYPES:
            valid_types = ', '.join(OrderValidator.VALID_ORDER_TYPES)
            raise ValidationError(
                f"Order type '{order_type}' not supported. Valid: {valid_types}"
            )

        logger.debug(f"Order type validation passed: {order_type}")
        return order_type


def validate_market_order(symbol: str, side: str, quantity: float) -> Dict[str, Any]:
    """Validate market order parameters"""
    try:
        return {
            'symbol': OrderValidator.validate_symbol(symbol),
            'side': OrderValidator.validate_side(side),
            'quantity': OrderValidator.validate_quantity(quantity, symbol)
        }
    except ValidationError as e:
        logger.log_validation_error('market_order', f"{symbol} {side} {quantity}", str(e))
        raise


def validate_limit_order(symbol: str, side: str, quantity: float, price: float) -> Dict[str, Any]:
    """Validate limit order parameters"""
    try:
        return {
            'symbol': OrderValidator.validate_symbol(symbol),
            'side': OrderValidator.validate_side(side),
            'quantity': OrderValidator.validate_quantity(quantity, symbol),
            'price': OrderValidator.validate_price(price, symbol)
        }
    except ValidationError as e:
        logger.log_validation_error(
            'limit_order',
            f"{symbol} {side} {quantity} @ {price}",
            str(e)
        )
        raise


def validate_stop_limit_order(
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
    limit_price: float
) -> Dict[str, Any]:
    """Validate stop-limit order parameters"""
    try:
        validated = {
            'symbol': OrderValidator.validate_symbol(symbol),
            'side': OrderValidator.validate_side(side),
            'quantity': OrderValidator.validate_quantity(quantity, symbol),
            'stop_price': OrderValidator.validate_price(stop_price, symbol),
            'limit_price': OrderValidator.validate_price(limit_price, symbol)
        }
        
        # Validate stop logic
        OrderValidator.validate_stop_price(stop_price, limit_price, side)
        
        return validated
    except ValidationError as e:
        logger.log_validation_error(
            'stop_limit_order',
            f"{symbol} {side} {quantity} Stop:{stop_price} Limit:{limit_price}",
            str(e)
        )
        raise

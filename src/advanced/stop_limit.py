"""
Stop-Limit Order implementation for Binance Futures Trading Bot
Triggers a limit order when price reaches stop price
"""

from typing import Dict, Any, Optional
from datetime import datetime
from validation import validate_stop_limit_order, ValidationError, OrderValidator
from logger import get_logger

logger = get_logger()


class StopLimitOrder:
    """Stop-Limit order handler - limit order triggered by stop price"""

    def __init__(self, api_client=None):
        """
        Initialize stop-limit order handler
        
        Args:
            api_client: Binance API client
        """
        self.api_client = api_client
        self.order_history = []

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        limit_price: float,
        time_in_force: str = 'GTC',
        test_mode: bool = False,
        working_type: str = 'CONTRACT_PRICE'
    ) -> Dict[str, Any]:
        """
        Place a stop-limit order.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            stop_price: Price that triggers the limit order
            limit_price: Limit price for execution
            time_in_force: 'GTC', 'IOC', or 'FOK'
            test_mode: If True, simulate without API
            working_type: 'CONTRACT_PRICE' or 'MARK_PRICE'
            
        Returns:
            Order response dictionary
            
        Raises:
            ValidationError: If inputs are invalid
        """
        # Validate inputs
        try:
            validated = validate_stop_limit_order(
                symbol, side, quantity, stop_price, limit_price
            )
        except ValidationError as e:
            logger.error(f"Stop-limit order validation failed: {e}")
            raise

        symbol = validated['symbol']
        side = validated['side']
        quantity = validated['quantity']
        stop_price = validated['stop_price']
        limit_price = validated['limit_price']

        params = {
            'stopPrice': stop_price,
            'limitPrice': limit_price,
            'timeInForce': time_in_force,
            'workingType': working_type
        }

        logger.log_order('STOP_LIMIT', symbol, side, quantity, params)

        if test_mode or self.api_client is None:
            return self._simulate_stop_limit_order(
                symbol, side, quantity, stop_price, limit_price, working_type
            )
        else:
            return self._place_via_api(
                symbol, side, quantity, stop_price, limit_price, time_in_force, working_type
            )

    def _simulate_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        limit_price: float,
        working_type: str
    ) -> Dict[str, Any]:
        """
        Simulate a stop-limit order for testing.
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
            stop_price: Stop trigger price
            limit_price: Limit execution price
            working_type: Working type
            
        Returns:
            Simulated order response
        """
        response = {
            'orderId': 12345680,
            'symbol': symbol,
            'side': side,
            'type': 'STOP_LIMIT',
            'stopPrice': stop_price,
            'price': limit_price,
            'quantity': quantity,
            'executedQty': 0,
            'status': 'NEW',
            'timeInForce': 'GTC',
            'updateTime': int(datetime.now().timestamp() * 1000),
            'avgPrice': 0,
            'totalFill': 0,
            'workingType': working_type
        }

        logger.info(
            f"Simulated STOP-LIMIT order: {symbol} {side} {quantity} | "
            f"Stop: {stop_price} | Limit: {limit_price} | Order ID: {response['orderId']}"
        )

        self.order_history.append(response)
        return response

    def _place_via_api(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        limit_price: float,
        time_in_force: str,
        working_type: str
    ) -> Dict[str, Any]:
        """
        Place stop-limit order via Binance API.
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
            stop_price: Stop price
            limit_price: Limit price
            time_in_force: Time in force
            working_type: Working type
            
        Returns:
            API response
        """
        if not self.api_client:
            raise Exception("API client not configured")

        try:
            params = {
                'symbol': symbol,
                'side': side,
                'type': 'STOP',
                'timeInForce': time_in_force,
                'quantity': quantity,
                'price': limit_price,
                'stopPrice': stop_price,
                'workingType': working_type
            }

            logger.log_api_call('futures/order', 'POST', params)

            response = self.api_client.futures_create_order(**params)

            logger.log_api_response('futures/order', 200, response)
            logger.info(
                f"STOP-LIMIT order placed: {symbol} {side} {quantity} | "
                f"Stop: {stop_price} | Limit: {limit_price} | Order ID: {response['orderId']}"
            )

            self.order_history.append(response)
            return response

        except Exception as e:
            logger.error(f"API error placing stop-limit order: {e}", exc_info=True)
            raise

    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Get order status"""
        for order in self.order_history:
            if order.get('orderId') == order_id:
                return order

        if self.api_client:
            try:
                response = self.api_client.futures_get_order(
                    symbol=symbol,
                    orderId=order_id
                )
                return response
            except Exception as e:
                logger.error(f"Error fetching order: {e}", exc_info=True)
                raise

        return {}

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel stop-limit order"""
        if not self.api_client:
            return {'status': 'CANCELLED', 'note': 'Simulated'}

        try:
            response = self.api_client.futures_cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            logger.info(f"Stop-limit order {order_id} cancelled")
            return response
        except Exception as e:
            logger.error(f"Error cancelling order: {e}", exc_info=True)
            raise

    def get_order_history(self) -> list:
        """Get all stop-limit orders"""
        return self.order_history

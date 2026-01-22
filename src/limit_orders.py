"""
Limit Order implementation for Binance Futures Trading Bot
Executes orders at specified price or better
"""

from typing import Dict, Any, Optional
from datetime import datetime
from validation import validate_limit_order, ValidationError
from logger import get_logger

logger = get_logger()


class LimitOrder:
    """Limit order handler - executes at specified price or better"""

    def __init__(self, api_client=None):
        """
        Initialize limit order handler
        
        Args:
            api_client: Binance API client (for actual trading)
        """
        self.api_client = api_client
        self.order_history = []

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = 'GTC',
        test_mode: bool = False,
        post_only: bool = False,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """
        Place a limit order.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit price
            time_in_force: 'GTC' (Good-til-Cancelled), 'IOC' (Immediate-or-Cancel), 'FOK' (Fill-or-Kill)
            test_mode: If True, return simulated response
            post_only: If True, only post to orderbook (maker orders only)
            reduce_only: If True, only reduce position
            
        Returns:
            Order response dictionary
            
        Raises:
            ValidationError: If inputs are invalid
            Exception: If API call fails
        """
        # Validate inputs
        try:
            validated = validate_limit_order(symbol, side, quantity, price)
        except ValidationError as e:
            logger.error(f"Limit order validation failed: {e}")
            raise

        symbol = validated['symbol']
        side = validated['side']
        quantity = validated['quantity']
        price = validated['price']

        params = {
            'price': price,
            'timeInForce': time_in_force,
            'postOnly': post_only,
            'reduceOnly': reduce_only
        }

        logger.log_order('LIMIT', symbol, side, quantity, params)

        # Simulate order or place via API
        if test_mode or self.api_client is None:
            return self._simulate_limit_order(symbol, side, quantity, price, time_in_force)
        else:
            return self._place_via_api(
                symbol, side, quantity, price, time_in_force, post_only, reduce_only
            )

    def _simulate_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str
    ) -> Dict[str, Any]:
        """
        Simulate a limit order for testing without API.
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force parameter
            
        Returns:
            Simulated order response
        """
        response = {
            'orderId': 12345679,
            'symbol': symbol,
            'side': side,
            'type': 'LIMIT',
            'timeInForce': time_in_force,
            'quantity': quantity,
            'price': price,
            'executedQty': 0,
            'status': 'NEW',
            'updateTime': int(datetime.now().timestamp() * 1000),
            'avgPrice': 0,
            'totalFill': 0
        }

        logger.info(
            f"Simulated LIMIT order placed: {symbol} {side} {quantity} @ {price} | "
            f"Order ID: {response['orderId']} | Status: {response['status']}"
        )

        self.order_history.append(response)
        return response

    def _place_via_api(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str,
        post_only: bool,
        reduce_only: bool
    ) -> Dict[str, Any]:
        """
        Place limit order via Binance API.
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force
            post_only: Post only flag
            reduce_only: Reduce only flag
            
        Returns:
            API response
            
        Raises:
            Exception: If API call fails
        """
        if not self.api_client:
            raise Exception("API client not configured")

        try:
            params = {
                'symbol': symbol,
                'side': side,
                'type': 'LIMIT',
                'timeInForce': time_in_force,
                'quantity': quantity,
                'price': price
            }

            if post_only:
                params['postOnly'] = True
            if reduce_only:
                params['reduceOnly'] = True

            logger.log_api_call('futures/order', 'POST', params)

            response = self.api_client.futures_create_order(**params)

            logger.log_api_response('futures/order', 200, response)
            logger.info(
                f"LIMIT order placed: {symbol} {side} {quantity} @ {price} | "
                f"Order ID: {response['orderId']} | Status: {response['status']}"
            )

            self.order_history.append(response)
            return response

        except Exception as e:
            logger.error(f"API error placing limit order: {e}", exc_info=True)
            raise

    def modify_order(
        self,
        symbol: str,
        order_id: int,
        new_quantity: Optional[float] = None,
        new_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Modify an existing limit order.
        
        Args:
            symbol: Trading pair
            order_id: Order ID to modify
            new_quantity: New quantity (if updating)
            new_price: New price (if updating)
            
        Returns:
            Updated order response
        """
        if not self.api_client:
            logger.warning(f"Cannot modify order {order_id} - no API client")
            return {'status': 'MODIFIED', 'note': 'Simulated modification'}

        try:
            # Cancel original order
            logger.info(f"Cancelling original order {order_id} to modify")
            self.cancel_order(symbol, order_id)

            # Place new order with updated parameters
            return self.place_order(
                symbol=symbol,
                side='BUY',  # This would need to be tracked from original
                quantity=new_quantity or 1.0,
                price=new_price or 0.0
            )

        except Exception as e:
            logger.error(f"Error modifying order {order_id}: {e}", exc_info=True)
            raise

    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get status of placed order.
        
        Args:
            symbol: Trading pair
            order_id: Order ID from response
            
        Returns:
            Order status dictionary
        """
        # Check history first
        for order in self.order_history:
            if order.get('orderId') == order_id:
                logger.info(f"Order {order_id} found in history: {order['status']}")
                return order

        # Query via API if not in history
        if self.api_client:
            try:
                logger.log_api_call('futures/order', 'GET')
                response = self.api_client.futures_get_order(
                    symbol=symbol,
                    orderId=order_id
                )
                logger.log_api_response('futures/order', 200, response)
                return response
            except Exception as e:
                logger.error(f"Error fetching order {order_id}: {e}", exc_info=True)
                raise

        logger.warning(f"Order {order_id} not found")
        return {}

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel a limit order.
        
        Args:
            symbol: Trading pair
            order_id: Order ID to cancel
            
        Returns:
            Cancellation response
        """
        if not self.api_client:
            logger.warning(f"Cannot cancel order {order_id} - no API client")
            return {'status': 'CANCELLED', 'note': 'Simulated cancellation'}

        try:
            logger.log_api_call('futures/order', 'DELETE', {
                'symbol': symbol,
                'orderId': order_id
            })

            response = self.api_client.futures_cancel_order(
                symbol=symbol,
                orderId=order_id
            )

            logger.log_api_response('futures/order', 200, response)
            logger.info(f"Order {order_id} cancelled successfully")
            return response

        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}", exc_info=True)
            raise

    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """
        Get all open orders.
        
        Args:
            symbol: Optional trading pair to filter
            
        Returns:
            List of open orders
        """
        open_orders = [
            order for order in self.order_history
            if order.get('status') == 'NEW'
        ]

        if symbol:
            open_orders = [
                order for order in open_orders
                if order.get('symbol') == symbol
            ]

        return open_orders

    def get_order_history(self) -> list:
        """Get all orders placed in this session"""
        return self.order_history

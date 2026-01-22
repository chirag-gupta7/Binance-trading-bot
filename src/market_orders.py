"""
Market Order implementation for Binance Futures Trading Bot
Executes market orders at current market price
"""

from typing import Dict, Any
from datetime import datetime
from validation import validate_market_order, ValidationError
from logger import get_logger

logger = get_logger()


class MarketOrder:
    """Market order handler - executes immediately at market price"""

    def __init__(self, api_client=None):
        """
        Initialize market order handler
        
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
        test_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Place a market order.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            test_mode: If True, return simulated response
            
        Returns:
            Order response dictionary
            
        Raises:
            ValidationError: If inputs are invalid
            Exception: If API call fails
        """
        # Validate inputs
        try:
            validated = validate_market_order(symbol, side, quantity)
        except ValidationError as e:
            logger.error(f"Market order validation failed: {e}")
            raise

        symbol = validated['symbol']
        side = validated['side']
        quantity = validated['quantity']

        logger.log_order('MARKET', symbol, side, quantity)

        # Simulate order or place via API
        if test_mode or self.api_client is None:
            return self._simulate_market_order(symbol, side, quantity)
        else:
            return self._place_via_api(symbol, side, quantity)

    def _simulate_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float
    ) -> Dict[str, Any]:
        """
        Simulate a market order for testing without API.
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
            
        Returns:
            Simulated order response
        """
        # Simulated prices for demo
        simulated_prices = {
            'BTCUSDT': 42500.50,
            'ETHUSDT': 2350.25,
            'BNBUSDT': 615.80,
            'ADAUSDT': 0.98,
            'DOGEUSDT': 0.38,
        }

        current_price = simulated_prices.get(symbol, 100.0)
        fill_amount = quantity * current_price

        response = {
            'orderId': 12345678,
            'symbol': symbol,
            'side': side,
            'type': 'MARKET',
            'quantity': quantity,
            'executedQty': quantity,
            'status': 'FILLED',
            'updateTime': int(datetime.now().timestamp() * 1000),
            'fills': [
                {
                    'price': current_price,
                    'qty': quantity,
                    'commission': fill_amount * 0.0002,  # 0.02% fee
                    'commissionAsset': 'USDT'
                }
            ],
            'avgPrice': current_price,
            'totalFill': fill_amount
        }

        logger.log_execution(
            response['orderId'],
            response['status'],
            current_price,
            quantity
        )

        self.order_history.append(response)
        return response

    def _place_via_api(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """
        Place market order via Binance API.
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
            
        Returns:
            API response
            
        Raises:
            Exception: If API call fails
        """
        if not self.api_client:
            raise Exception("API client not configured")

        try:
            logger.log_api_call('futures/order', 'POST', {
                'symbol': symbol,
                'side': side,
                'type': 'MARKET',
                'quantity': quantity
            })

            # Call actual API
            response = self.api_client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )

            logger.log_api_response('futures/order', 200, response)
            logger.log_execution(
                response.get('orderId'),
                response.get('status'),
                response.get('avgPrice'),
                response.get('executedQty')
            )

            self.order_history.append(response)
            return response

        except Exception as e:
            logger.error(f"API error placing market order: {e}", exc_info=True)
            raise

    def get_order_status(self, order_id: int) -> Dict[str, Any]:
        """
        Get status of placed order.
        
        Args:
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
                response = self.api_client.futures_get_order(orderId=order_id)
                logger.log_api_response('futures/order', 200, response)
                return response
            except Exception as e:
                logger.error(f"Error fetching order {order_id}: {e}", exc_info=True)
                raise

        logger.warning(f"Order {order_id} not found")
        return {}

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel a market order.
        
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

    def get_order_history(self) -> list:
        """Get all orders placed in this session"""
        return self.order_history

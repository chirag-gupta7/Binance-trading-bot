"""
OCO (One-Cancels-the-Other) Order implementation for Binance Futures Trading Bot
Places take-profit and stop-loss orders simultaneously
"""

from typing import Dict, Any, Optional
from datetime import datetime
from validation import validate_limit_order, ValidationError, OrderValidator
from logger import get_logger

logger = get_logger()


class OCOOrder:
    """OCO order handler - simultaneous take-profit and stop-loss orders"""

    def __init__(self, api_client=None):
        """
        Initialize OCO order handler
        
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
        take_profit_price: float,
        stop_loss_price: float,
        stop_loss_limit_price: Optional[float] = None,
        test_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Place an OCO order (take-profit + stop-loss).
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            take_profit_price: Take-profit trigger price
            stop_loss_price: Stop-loss trigger price
            stop_loss_limit_price: Limit price for stop-loss (if None, uses stop price)
            test_mode: If True, simulate without API
            
        Returns:
            Order response dictionary
            
        Raises:
            ValidationError: If inputs are invalid
        """
        # Validate basic inputs
        try:
            symbol = OrderValidator.validate_symbol(symbol)
            side = OrderValidator.validate_side(side)
            quantity = OrderValidator.validate_quantity(quantity, symbol)
            tp_price = OrderValidator.validate_price(take_profit_price, symbol)
            sl_price = OrderValidator.validate_price(stop_loss_price, symbol)
        except ValidationError as e:
            logger.error(f"OCO order validation failed: {e}")
            raise

        # Validate OCO logic
        self._validate_oco_logic(side, take_profit_price, stop_loss_price)

        sl_limit = stop_loss_limit_price or stop_loss_price

        params = {
            'takeProfitPrice': tp_price,
            'stopLossPrice': sl_price,
            'stopLossLimitPrice': sl_limit
        }

        logger.log_order('OCO', symbol, side, quantity, params)

        if test_mode or self.api_client is None:
            return self._simulate_oco_order(
                symbol, side, quantity, tp_price, sl_price, sl_limit
            )
        else:
            return self._place_via_api(
                symbol, side, quantity, tp_price, sl_price, sl_limit
            )

    def _validate_oco_logic(self, side: str, tp_price: float, sl_price: float):
        """
        Validate OCO order logic.
        
        For BUY side: take-profit > entry, stop-loss < entry
        For SELL side: take-profit < entry, stop-loss > entry
        
        Args:
            side: BUY or SELL
            tp_price: Take-profit price
            sl_price: Stop-loss price
            
        Raises:
            ValidationError: If logic is invalid
        """
        if side.upper() == 'BUY':
            if tp_price <= sl_price:
                raise ValidationError(
                    f"For BUY: take-profit ({tp_price}) must be > stop-loss ({sl_price})"
                )
        else:  # SELL
            if tp_price >= sl_price:
                raise ValidationError(
                    f"For SELL: take-profit ({tp_price}) must be < stop-loss ({sl_price})"
                )

    def _simulate_oco_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        tp_price: float,
        sl_price: float,
        sl_limit: float
    ) -> Dict[str, Any]:
        """
        Simulate an OCO order for testing.
        
        Returns:
            Simulated OCO response with both orders
        """
        response = {
            'orderListId': 987654321,
            'symbol': symbol,
            'orders': [
                {
                    'orderId': 12345681,
                    'symbol': symbol,
                    'side': side,
                    'type': 'TAKE_PROFIT',
                    'price': tp_price,
                    'quantity': quantity,
                    'status': 'NEW',
                    'timeInForce': 'GTC'
                },
                {
                    'orderId': 12345682,
                    'symbol': symbol,
                    'side': side,
                    'type': 'STOP_LOSS',
                    'stopPrice': sl_price,
                    'price': sl_limit,
                    'quantity': quantity,
                    'status': 'NEW',
                    'timeInForce': 'GTC'
                }
            ],
            'listStatus': 'EXECUTING',
            'listOrderStatus': 'NEW',
            'updateTime': int(datetime.now().timestamp() * 1000)
        }

        logger.info(
            f"Simulated OCO order: {symbol} {side} {quantity} | "
            f"TP: {tp_price} | SL: {sl_price} | ListID: {response['orderListId']}"
        )

        self.order_history.append(response)
        return response

    def _place_via_api(
        self,
        symbol: str,
        side: str,
        quantity: float,
        tp_price: float,
        sl_price: float,
        sl_limit: float
    ) -> Dict[str, Any]:
        """
        Place OCO order via Binance API.
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
            tp_price: Take-profit price
            sl_price: Stop-loss price
            sl_limit: Stop-loss limit price
            
        Returns:
            API response
        """
        if not self.api_client:
            raise Exception("API client not configured")

        try:
            params = {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': tp_price,
                'stopPrice': sl_price,
                'stopLimitPrice': sl_limit,
                'stopLimitTimeInForce': 'GTC'
            }

            logger.log_api_call('futures/order', 'POST', params)

            response = self.api_client.futures_create_order(**params)

            logger.log_api_response('futures/order', 200, response)
            logger.info(
                f"OCO order placed: {symbol} {side} {quantity} | "
                f"TP: {tp_price} | SL: {sl_price} | ListID: {response.get('orderListId')}"
            )

            self.order_history.append(response)
            return response

        except Exception as e:
            logger.error(f"API error placing OCO order: {e}", exc_info=True)
            raise

    def cancel_order(self, symbol: str, order_list_id: int) -> Dict[str, Any]:
        """
        Cancel an OCO order (cancels both TP and SL orders).
        
        Args:
            symbol: Trading pair
            order_list_id: Order list ID
            
        Returns:
            Cancellation response
        """
        if not self.api_client:
            return {'status': 'CANCELLED', 'note': 'Simulated'}

        try:
            response = self.api_client.futures_cancel_order(
                symbol=symbol,
                orderListId=order_list_id
            )
            logger.info(f"OCO order list {order_list_id} cancelled")
            return response
        except Exception as e:
            logger.error(f"Error cancelling OCO order: {e}", exc_info=True)
            raise

    def get_order_status(self, symbol: str, order_list_id: int) -> Dict[str, Any]:
        """
        Get OCO order status.
        
        Args:
            symbol: Trading pair
            order_list_id: Order list ID
            
        Returns:
            OCO order status
        """
        for order in self.order_history:
            if order.get('orderListId') == order_list_id:
                return order

        if self.api_client:
            try:
                response = self.api_client.futures_get_order_list(
                    symbol=symbol,
                    orderListId=order_list_id
                )
                return response
            except Exception as e:
                logger.error(f"Error fetching OCO order: {e}", exc_info=True)
                raise

        return {}

    def get_order_history(self) -> list:
        """Get all OCO orders"""
        return self.order_history

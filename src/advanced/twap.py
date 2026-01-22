"""
TWAP (Time-Weighted Average Price) Strategy for Binance Futures Trading Bot
Splits large orders into smaller chunks over time
"""

import time
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from validation import validate_market_order, validate_limit_order, ValidationError, OrderValidator
from logger import get_logger
from market_orders import MarketOrder
from limit_orders import LimitOrder

logger = get_logger()


class TWAPStrategy:
    """TWAP strategy handler - executes orders over time"""

    def __init__(self, api_client=None):
        """
        Initialize TWAP strategy handler
        
        Args:
            api_client: Binance API client
        """
        self.api_client = api_client
        self.market_orders = MarketOrder(api_client)
        self.limit_orders = LimitOrder(api_client)
        self.order_history = []
        self.active_orders = {}
        self.stop_event = threading.Event()

    def place_order(
        self,
        symbol: str,
        side: str,
        total_quantity: float,
        num_splits: int,
        interval_seconds: int,
        order_type: str = 'MARKET',
        price: Optional[float] = None,
        test_mode: bool = False,
        on_fill_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Place a TWAP order.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            total_quantity: Total quantity to execute
            num_splits: Number of orders to split into
            interval_seconds: Seconds between each order
            order_type: 'MARKET' or 'LIMIT'
            price: Limit price (required if order_type='LIMIT')
            test_mode: If True, simulate without API
            on_fill_callback: Optional callback function when order fills
            
        Returns:
            TWAP execution plan dictionary
            
        Raises:
            ValidationError: If inputs are invalid
        """
        # Validate inputs
        try:
            symbol = OrderValidator.validate_symbol(symbol)
            side = OrderValidator.validate_side(side)
            total_qty = OrderValidator.validate_quantity(total_quantity, symbol)
            num_splits = int(num_splits)
            interval = OrderValidator.validate_interval(interval_seconds)
        except (ValidationError, ValueError) as e:
            logger.error(f"TWAP order validation failed: {e}")
            raise

        if num_splits < 2:
            raise ValidationError("Number of splits must be at least 2")

        if num_splits > 100:
            raise ValidationError("Number of splits cannot exceed 100")

        qty_per_split = total_qty / num_splits

        params = {
            'totalQty': total_qty,
            'numSplits': num_splits,
            'interval': interval,
            'qtyPerSplit': qty_per_split,
            'orderType': order_type,
            'price': price if price else 'market'
        }

        logger.log_order('TWAP', symbol, side, total_qty, params)

        # Create execution plan
        plan = {
            'strategyId': int(datetime.now().timestamp() * 1000),
            'symbol': symbol,
            'side': side,
            'totalQuantity': total_qty,
            'numSplits': num_splits,
            'quantityPerSplit': qty_per_split,
            'interval': interval,
            'orderType': order_type,
            'price': price,
            'status': 'PLANNED',
            'startTime': datetime.now().isoformat(),
            'orders': []
        }

        self.order_history.append(plan)

        # Execute in background thread
        if not test_mode:
            thread = threading.Thread(
                target=self._execute_twap,
                args=(plan, order_type, price, on_fill_callback),
                daemon=True
            )
            thread.start()
            self.active_orders[plan['strategyId']] = thread
        else:
            self._execute_twap(plan, order_type, price, on_fill_callback)

        logger.info(
            f"TWAP strategy initiated: {symbol} {side} {total_qty} | "
            f"Splits: {num_splits} | Interval: {interval}s | "
            f"PerOrder: {qty_per_split} | Strategy ID: {plan['strategyId']}"
        )

        return plan

    def _execute_twap(
        self,
        plan: Dict[str, Any],
        order_type: str,
        price: Optional[float],
        callback: Optional[Callable]
    ):
        """
        Execute TWAP strategy with time intervals.
        
        Args:
            plan: Execution plan
            order_type: MARKET or LIMIT
            price: Limit price
            callback: Optional callback on fills
        """
        plan['status'] = 'EXECUTING'
        logger.info(f"Starting TWAP execution: Strategy {plan['strategyId']}")

        try:
            for i in range(plan['numSplits']):
                if self.stop_event.is_set():
                    plan['status'] = 'STOPPED'
                    logger.warning(f"TWAP strategy {plan['strategyId']} stopped by user")
                    break

                # Execute individual order
                try:
                    if order_type == 'MARKET':
                        order = self.market_orders.place_order(
                            symbol=plan['symbol'],
                            side=plan['side'],
                            quantity=plan['quantityPerSplit'],
                            test_mode=False
                        )
                    else:  # LIMIT
                        order = self.limit_orders.place_order(
                            symbol=plan['symbol'],
                            side=plan['side'],
                            quantity=plan['quantityPerSplit'],
                            price=price,
                            test_mode=False
                        )

                    plan['orders'].append(order)

                    logger.info(
                        f"TWAP split {i+1}/{plan['numSplits']} executed | "
                        f"Order ID: {order.get('orderId')} | "
                        f"Strategy: {plan['strategyId']}"
                    )

                    if callback:
                        callback(order)

                except Exception as e:
                    logger.error(
                        f"TWAP split {i+1} failed for strategy {plan['strategyId']}: {e}",
                        exc_info=True
                    )

                # Wait before next order (except after last)
                if i < plan['numSplits'] - 1:
                    time.sleep(plan['interval'])

            plan['status'] = 'COMPLETED'
            plan['completionTime'] = datetime.now().isoformat()
            logger.info(
                f"TWAP strategy {plan['strategyId']} completed | "
                f"Orders executed: {len(plan['orders'])}"
            )

        except Exception as e:
            plan['status'] = 'FAILED'
            logger.error(
                f"TWAP strategy {plan['strategyId']} failed: {e}",
                exc_info=True
            )

    def cancel_strategy(self, strategy_id: int) -> Dict[str, Any]:
        """
        Cancel an active TWAP strategy.
        
        Args:
            strategy_id: Strategy ID to cancel
            
        Returns:
            Cancellation result
        """
        for plan in self.order_history:
            if plan['strategyId'] == strategy_id:
                if plan['status'] in ['EXECUTING', 'PLANNED']:
                    plan['status'] = 'CANCELLED'
                    self.stop_event.set()

                    # Cancel all pending orders
                    for order in plan['orders']:
                        try:
                            self.market_orders.cancel_order(
                                plan['symbol'],
                                order['orderId']
                            )
                        except Exception as e:
                            logger.warning(f"Could not cancel order: {e}")

                    logger.info(f"TWAP strategy {strategy_id} cancelled")
                    return {'status': 'CANCELLED', 'strategyId': strategy_id}

        raise ValueError(f"Strategy {strategy_id} not found or not active")

    def get_strategy_status(self, strategy_id: int) -> Dict[str, Any]:
        """
        Get status of a TWAP strategy.
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            Strategy status
        """
        for plan in self.order_history:
            if plan['strategyId'] == strategy_id:
                return plan

        return {}

    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all TWAP strategies"""
        return self.order_history

    def get_active_strategies(self) -> List[Dict[str, Any]]:
        """Get currently executing TWAP strategies"""
        return [
            plan for plan in self.order_history
            if plan['status'] in ['PLANNED', 'EXECUTING']
        ]

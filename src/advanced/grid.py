"""
Grid Order Strategy for Binance Futures Trading Bot
Automated buy-low/sell-high within a price range
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from validation import OrderValidator, ValidationError
from logger import get_logger
from limit_orders import LimitOrder

logger = get_logger()


class GridStrategy:
    """Grid strategy handler - automated trading within price range"""

    def __init__(self, api_client=None):
        """
        Initialize grid strategy handler
        
        Args:
            api_client: Binance API client
        """
        self.api_client = api_client
        self.limit_orders = LimitOrder(api_client)
        self.strategy_history = []
        self.grid_levels = {}

    def place_order(
        self,
        symbol: str,
        lower_price: float,
        upper_price: float,
        num_grids: int,
        total_quantity: float,
        grid_type: str = 'LONG',
        test_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Place a grid strategy.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            lower_price: Lower bound of grid
            upper_price: Upper bound of grid
            num_grids: Number of grid levels
            total_quantity: Total quantity to deploy
            grid_type: 'LONG' (buy-low/sell-high) or 'SHORT' (sell-high/buy-low)
            test_mode: If True, simulate without API
            
        Returns:
            Grid strategy details
            
        Raises:
            ValidationError: If inputs are invalid
        """
        # Validate inputs
        try:
            symbol = OrderValidator.validate_symbol(symbol)
            lower = OrderValidator.validate_price(lower_price, symbol)
            upper = OrderValidator.validate_price(upper_price, symbol)
            total_qty = OrderValidator.validate_quantity(total_quantity, symbol)
            num_grids = int(num_grids)
        except (ValidationError, ValueError) as e:
            logger.error(f"Grid strategy validation failed: {e}")
            raise

        if lower >= upper:
            raise ValidationError(f"Lower price ({lower}) must be < upper price ({upper})")

        if num_grids < 2:
            raise ValidationError("Number of grids must be at least 2")

        if num_grids > 100:
            raise ValidationError("Number of grids cannot exceed 100")

        if grid_type not in ['LONG', 'SHORT']:
            raise ValidationError("Grid type must be 'LONG' or 'SHORT'")

        # Calculate grid parameters
        price_range = upper - lower
        price_step = price_range / (num_grids - 1)
        qty_per_grid = total_qty / num_grids

        # Create grid levels
        grid_levels = []
        for i in range(num_grids):
            price = lower + (price_step * i)
            grid_levels.append({
                'level': i,
                'price': price,
                'quantity': qty_per_grid,
                'side': 'BUY' if grid_type == 'LONG' else 'SELL',
                'status': 'PENDING',
                'order_id': None
            })

        strategy = {
            'strategyId': int(datetime.now().timestamp() * 1000),
            'symbol': symbol,
            'gridType': grid_type,
            'lowerPrice': lower,
            'upperPrice': upper,
            'numGrids': num_grids,
            'priceStep': price_step,
            'totalQuantity': total_qty,
            'quantityPerGrid': qty_per_grid,
            'status': 'ACTIVE',
            'startTime': datetime.now().isoformat(),
            'gridLevels': grid_levels,
            'orders': []
        }

        logger.log_order('GRID', symbol, grid_type, total_qty, {
            'lowerPrice': lower,
            'upperPrice': upper,
            'numGrids': num_grids,
            'priceStep': price_step,
            'qtyPerGrid': qty_per_grid
        })

        # Place orders for each grid level
        self._place_grid_orders(strategy, test_mode)

        self.strategy_history.append(strategy)
        self.grid_levels[strategy['strategyId']] = strategy

        logger.info(
            f"Grid strategy initiated: {symbol} {grid_type} | "
            f"Range: {lower}-{upper} | Grids: {num_grids} | "
            f"Step: {price_step:.2f} | QtyPerGrid: {qty_per_grid} | "
            f"Strategy ID: {strategy['strategyId']}"
        )

        return strategy

    def _place_grid_orders(self, strategy: Dict[str, Any], test_mode: bool):
        """
        Place limit orders for each grid level.
        
        Args:
            strategy: Strategy details
            test_mode: If True, simulate
        """
        for level in strategy['gridLevels']:
            try:
                if not test_mode and self.limit_orders:
                    order = self.limit_orders.place_order(
                        symbol=strategy['symbol'],
                        side=level['side'],
                        quantity=level['quantity'],
                        price=level['price'],
                        post_only=True
                    )
                    level['order_id'] = order.get('orderId')
                    level['status'] = 'PLACED'
                    strategy['orders'].append(order)
                else:
                    # Simulate
                    level['order_id'] = 10000000 + level['level']
                    level['status'] = 'PLACED'

                logger.debug(
                    f"Grid level {level['level']}: {strategy['symbol']} "
                    f"{level['side']} {level['quantity']} @ {level['price']} | "
                    f"Order ID: {level['order_id']}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to place grid order for level {level['level']}: {e}",
                    exc_info=True
                )
                level['status'] = 'FAILED'

    def update_grid(
        self,
        strategy_id: int,
        new_lower: Optional[float] = None,
        new_upper: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Update grid price range dynamically.
        
        Args:
            strategy_id: Strategy ID
            new_lower: New lower price
            new_upper: New upper price
            
        Returns:
            Updated strategy
        """
        for strategy in self.strategy_history:
            if strategy['strategyId'] == strategy_id:
                # Cancel existing orders
                self._cancel_grid_orders(strategy)

                # Update prices
                if new_lower:
                    strategy['lowerPrice'] = new_lower
                if new_upper:
                    strategy['upperPrice'] = new_upper

                # Recalculate and place new orders
                lower = strategy['lowerPrice']
                upper = strategy['upperPrice']
                num_grids = strategy['numGrids']

                price_range = upper - lower
                price_step = price_range / (num_grids - 1)

                # Update grid levels
                for i in range(num_grids):
                    price = lower + (price_step * i)
                    strategy['gridLevels'][i]['price'] = price

                strategy['priceStep'] = price_step

                # Place new orders
                self._place_grid_orders(strategy, False)

                logger.info(
                    f"Grid strategy {strategy_id} updated: {strategy['lowerPrice']}-"
                    f"{strategy['upperPrice']}"
                )

                return strategy

        raise ValueError(f"Strategy {strategy_id} not found")

    def cancel_strategy(self, strategy_id: int) -> Dict[str, Any]:
        """
        Cancel a grid strategy.
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            Cancellation result
        """
        for strategy in self.strategy_history:
            if strategy['strategyId'] == strategy_id:
                self._cancel_grid_orders(strategy)
                strategy['status'] = 'CANCELLED'
                strategy['endTime'] = datetime.now().isoformat()

                logger.info(f"Grid strategy {strategy_id} cancelled")

                return {'status': 'CANCELLED', 'strategyId': strategy_id}

        raise ValueError(f"Strategy {strategy_id} not found")

    def _cancel_grid_orders(self, strategy: Dict[str, Any]):
        """Cancel all orders in a grid strategy"""
        for order in strategy['orders']:
            try:
                self.limit_orders.cancel_order(
                    strategy['symbol'],
                    order['orderId']
                )
            except Exception as e:
                logger.warning(f"Could not cancel order {order['orderId']}: {e}")

    def get_strategy_status(self, strategy_id: int) -> Dict[str, Any]:
        """Get status of a grid strategy"""
        for strategy in self.strategy_history:
            if strategy['strategyId'] == strategy_id:
                return strategy

        return {}

    def get_profit_loss(self, strategy_id: int) -> Dict[str, Any]:
        """
        Calculate P&L for a grid strategy.
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            P&L details
        """
        strategy = self.get_strategy_status(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy {strategy_id} not found")

        # Calculate buy and sell totals
        buy_total = 0
        sell_total = 0
        buy_qty = 0
        sell_qty = 0

        for order in strategy['orders']:
            if order.get('side') == 'BUY':
                buy_total += order.get('executedQty', 0) * order.get('avgPrice', 0)
                buy_qty += order.get('executedQty', 0)
            else:
                sell_total += order.get('executedQty', 0) * order.get('avgPrice', 0)
                sell_qty += order.get('executedQty', 0)

        pnl = sell_total - buy_total if buy_qty > 0 and sell_qty > 0 else 0

        return {
            'strategyId': strategy_id,
            'buyTotal': buy_total,
            'buyQty': buy_qty,
            'sellTotal': sell_total,
            'sellQty': sell_qty,
            'grossProfit': pnl,
            'roi': (pnl / buy_total * 100) if buy_total > 0 else 0
        }

    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all grid strategies"""
        return self.strategy_history

    def get_active_strategies(self) -> List[Dict[str, Any]]:
        """Get currently active grid strategies"""
        return [s for s in self.strategy_history if s['status'] == 'ACTIVE']

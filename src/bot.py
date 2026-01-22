"""
Binance Futures Trading Bot - Main CLI Interface
Provides command-line interface for all order types and strategies
"""

import argparse
import sys
import json
from typing import Dict, Any
from datetime import datetime

from logger import get_logger
from api_client import get_api_client
from market_orders import MarketOrder
from limit_orders import LimitOrder
from advanced.stop_limit import StopLimitOrder
from advanced.oco import OCOOrder
from advanced.twap import TWAPStrategy
from advanced.grid import GridStrategy
from validation import ValidationError

logger = get_logger()

# Initialize API client
api_client = get_api_client()

# Initialize order handlers with API client
market_order = MarketOrder(api_client.client if api_client.is_connected() else None)
limit_order = LimitOrder(api_client.client if api_client.is_connected() else None)
stop_limit_order = StopLimitOrder(api_client.client if api_client.is_connected() else None)
oco_order = OCOOrder(api_client.client if api_client.is_connected() else None)
twap_strategy = TWAPStrategy(api_client.client if api_client.is_connected() else None)
grid_strategy = GridStrategy(api_client.client if api_client.is_connected() else None)


def format_order_response(order: Dict[str, Any]) -> str:
    """Format order response for display"""
    output = []
    output.append("\n" + "="*60)
    output.append("ORDER RESPONSE")
    output.append("="*60)
    
    if 'orderId' in order:
        output.append(f"Order ID:        {order['orderId']}")
    if 'orderListId' in order:
        output.append(f"Order List ID:   {order['orderListId']}")
    
    output.append(f"Symbol:          {order.get('symbol', 'N/A')}")
    output.append(f"Side:            {order.get('side', 'N/A')}")
    output.append(f"Type:            {order.get('type', 'N/A')}")
    output.append(f"Status:          {order.get('status', 'N/A')}")
    output.append(f"Quantity:        {order.get('quantity', 0)}")
    
    if order.get('price'):
        output.append(f"Price:           {order['price']}")
    if order.get('avgPrice'):
        output.append(f"Avg Price:       {order['avgPrice']}")
    if order.get('executedQty'):
        output.append(f"Executed Qty:    {order['executedQty']}")
    
    output.append("="*60)
    return "\n".join(output)


def cmd_market_order(args):
    """Handle market order command"""
    try:
        mode = "TEST" if args.test or not api_client.is_connected() else "LIVE"
        logger.info(f"Processing MARKET order ({mode}): {args.symbol} {args.side} {args.quantity}")
        
        response = market_order.place_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            test_mode=args.test
        )
        
        print(format_order_response(response))
        logger.info("Market order completed successfully")
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        print(f"\n❌ Validation Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Market order failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


def cmd_limit_order(args):
    """Handle limit order command"""
    try:
        logger.info(
            f"Processing LIMIT order: {args.symbol} {args.side} "
            f"{args.quantity} @ {args.price}"
        )
        
        response = limit_order.place_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            price=args.price,
            time_in_force=args.time_in_force,
            test_mode=args.test,
            post_only=args.post_only,
            reduce_only=args.reduce_only
        )
        
        print(format_order_response(response))
        logger.info("Limit order completed successfully")
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        print(f"\n❌ Validation Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Limit order failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


def cmd_stop_limit_order(args):
    """Handle stop-limit order command"""
    try:
        logger.info(
            f"Processing STOP-LIMIT order: {args.symbol} {args.side} "
            f"{args.quantity} | Stop: {args.stop_price} | Limit: {args.limit_price}"
        )
        
        response = stop_limit_order.place_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            stop_price=args.stop_price,
            limit_price=args.limit_price,
            working_type=args.working_type,
            test_mode=args.test
        )
        
        print(format_order_response(response))
        logger.info("Stop-limit order completed successfully")
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        print(f"\n❌ Validation Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Stop-limit order failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


def cmd_oco_order(args):
    """Handle OCO order command"""
    try:
        logger.info(
            f"Processing OCO order: {args.symbol} {args.side} {args.quantity} | "
            f"TP: {args.take_profit} | SL: {args.stop_loss}"
        )
        
        response = oco_order.place_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            take_profit_price=args.take_profit,
            stop_loss_price=args.stop_loss,
            stop_loss_limit_price=args.sl_limit,
            test_mode=args.test
        )
        
        print(format_order_response(response))
        logger.info("OCO order completed successfully")
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        print(f"\n❌ Validation Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"OCO order failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


def cmd_twap_order(args):
    """Handle TWAP strategy command"""
    try:
        logger.info(
            f"Processing TWAP strategy: {args.symbol} {args.side} "
            f"{args.quantity} | Splits: {args.splits} | Interval: {args.interval}s"
        )
        
        response = twap_strategy.place_order(
            symbol=args.symbol,
            side=args.side,
            total_quantity=args.quantity,
            num_splits=args.splits,
            interval_seconds=args.interval,
            order_type=args.order_type,
            price=args.price,
            test_mode=args.test
        )
        
        output = []
        output.append("\n" + "="*60)
        output.append("TWAP STRATEGY INITIATED")
        output.append("="*60)
        output.append(f"Strategy ID:     {response['strategyId']}")
        output.append(f"Symbol:          {response['symbol']}")
        output.append(f"Side:            {response['side']}")
        output.append(f"Total Qty:       {response['totalQuantity']}")
        output.append(f"Splits:          {response['numSplits']}")
        output.append(f"Per Split:       {response['quantityPerSplit']}")
        output.append(f"Interval:        {response['interval']}s")
        output.append(f"Order Type:      {response['orderType']}")
        output.append(f"Status:          {response['status']}")
        output.append("="*60 + "\n")
        print("\n".join(output))
        
        logger.info(f"TWAP strategy {response['strategyId']} initiated")
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        print(f"\n❌ Validation Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"TWAP strategy failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


def cmd_grid_order(args):
    """Handle Grid strategy command"""
    try:
        logger.info(
            f"Processing GRID strategy: {args.symbol} {args.grid_type} "
            f"Range: {args.lower}-{args.upper} | Grids: {args.grids}"
        )
        
        response = grid_strategy.place_order(
            symbol=args.symbol,
            lower_price=args.lower,
            upper_price=args.upper,
            num_grids=args.grids,
            total_quantity=args.quantity,
            grid_type=args.grid_type,
            test_mode=args.test
        )
        
        output = []
        output.append("\n" + "="*60)
        output.append("GRID STRATEGY INITIATED")
        output.append("="*60)
        output.append(f"Strategy ID:     {response['strategyId']}")
        output.append(f"Symbol:          {response['symbol']}")
        output.append(f"Grid Type:       {response['gridType']}")
        output.append(f"Price Range:     {response['lowerPrice']} - {response['upperPrice']}")
        output.append(f"Number of Grids: {response['numGrids']}")
        output.append(f"Price Step:      {response['priceStep']:.8f}")
        output.append(f"Total Qty:       {response['totalQuantity']}")
        output.append(f"Qty Per Grid:    {response['quantityPerGrid']}")
        output.append(f"Status:          {response['status']}")
        output.append(f"Orders Placed:   {len(response['orders'])}")
        output.append("="*60 + "\n")
        print("\n".join(output))
        
        logger.info(f"Grid strategy {response['strategyId']} initiated")
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        print(f"\n❌ Validation Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Grid strategy failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


def cmd_status(args):
    """Check order/strategy status"""
    try:
        if args.type == 'market':
            status = market_order.get_order_status(args.order_id)
        elif args.type == 'limit':
            status = limit_order.get_order_status(args.symbol, args.order_id)
        elif args.type == 'stop_limit':
            status = stop_limit_order.get_order_status(args.symbol, args.order_id)
        elif args.type == 'twap':
            status = twap_strategy.get_strategy_status(args.order_id)
        elif args.type == 'grid':
            status = grid_strategy.get_strategy_status(args.order_id)
        else:
            raise ValueError(f"Unknown type: {args.type}")
        
        print("\n" + "="*60)
        print("ORDER/STRATEGY STATUS")
        print("="*60)
        print(json.dumps(status, indent=2))
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


def cmd_history(args):
    """View order/strategy history"""
    try:
        if args.type == 'market':
            history = market_order.get_order_history()
        elif args.type == 'limit':
            history = limit_order.get_order_history()
        elif args.type == 'twap':
            history = twap_strategy.get_all_strategies()
        elif args.type == 'grid':
            history = grid_strategy.get_all_strategies()
        else:
            raise ValueError(f"Unknown type: {args.type}")
        
        print("\n" + "="*60)
        print(f"{args.type.upper()} ORDER/STRATEGY HISTORY")
        print("="*60)
        print(json.dumps(history, indent=2, default=str))
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"History retrieval failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Binance Futures Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Market order
  python bot.py market BTCUSDT BUY 0.01

  # Limit order
  python bot.py limit ETHUSDT BUY 1.0 2300.50

  # Stop-limit order
  python bot.py stop-limit BTCUSDT SELL 0.01 42000 41500

  # OCO order (take-profit + stop-loss)
  python bot.py oco BTCUSDT BUY 0.01 45000 40000

  # TWAP strategy (split 0.05 BTC into 5 orders over 30 seconds)
  python bot.py twap BTCUSDT BUY 0.05 --splits 5 --interval 10

  # Grid strategy (buy-low/sell-high between 40000-45000)
  python bot.py grid BTCUSDT 40000 45000 --grids 10 --qty 0.1 --type LONG
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Market order command
    market_parser = subparsers.add_parser('market', help='Place a market order')
    market_parser.add_argument('symbol', help='Trading pair (e.g., BTCUSDT)')
    market_parser.add_argument('side', help='BUY or SELL')
    market_parser.add_argument('quantity', type=float, help='Order quantity')
    market_parser.add_argument('--test', action='store_true', help='Test mode (simulated)')
    market_parser.set_defaults(func=cmd_market_order)

    # Limit order command
    limit_parser = subparsers.add_parser('limit', help='Place a limit order')
    limit_parser.add_argument('symbol', help='Trading pair')
    limit_parser.add_argument('side', help='BUY or SELL')
    limit_parser.add_argument('quantity', type=float, help='Order quantity')
    limit_parser.add_argument('price', type=float, help='Limit price')
    limit_parser.add_argument('--tif', dest='time_in_force', default='GTC',
                              choices=['GTC', 'IOC', 'FOK'], help='Time in force')
    limit_parser.add_argument('--post-only', action='store_true', help='Post only')
    limit_parser.add_argument('--reduce-only', action='store_true', help='Reduce only')
    limit_parser.add_argument('--test', action='store_true', help='Test mode')
    limit_parser.set_defaults(func=cmd_limit_order)

    # Stop-limit order command
    sl_parser = subparsers.add_parser('stop-limit', help='Place a stop-limit order')
    sl_parser.add_argument('symbol', help='Trading pair')
    sl_parser.add_argument('side', help='BUY or SELL')
    sl_parser.add_argument('quantity', type=float, help='Order quantity')
    sl_parser.add_argument('stop_price', type=float, help='Stop trigger price')
    sl_parser.add_argument('limit_price', type=float, help='Limit execution price')
    sl_parser.add_argument('--working-type', default='CONTRACT_PRICE',
                           choices=['CONTRACT_PRICE', 'MARK_PRICE'], help='Working type')
    sl_parser.add_argument('--test', action='store_true', help='Test mode')
    sl_parser.set_defaults(func=cmd_stop_limit_order)

    # OCO order command
    oco_parser = subparsers.add_parser('oco', help='Place an OCO order')
    oco_parser.add_argument('symbol', help='Trading pair')
    oco_parser.add_argument('side', help='BUY or SELL')
    oco_parser.add_argument('quantity', type=float, help='Order quantity')
    oco_parser.add_argument('take_profit', type=float, help='Take-profit price')
    oco_parser.add_argument('stop_loss', type=float, help='Stop-loss price')
    oco_parser.add_argument('--sl-limit', type=float, default=None,
                            help='Stop-loss limit price')
    oco_parser.add_argument('--test', action='store_true', help='Test mode')
    oco_parser.set_defaults(func=cmd_oco_order)

    # TWAP strategy command
    twap_parser = subparsers.add_parser('twap', help='Execute TWAP strategy')
    twap_parser.add_argument('symbol', help='Trading pair')
    twap_parser.add_argument('side', help='BUY or SELL')
    twap_parser.add_argument('quantity', type=float, help='Total quantity')
    twap_parser.add_argument('--splits', type=int, default=5, help='Number of splits')
    twap_parser.add_argument('--interval', type=int, default=10, help='Interval in seconds')
    twap_parser.add_argument('--order-type', default='MARKET',
                             choices=['MARKET', 'LIMIT'], help='Order type')
    twap_parser.add_argument('--price', type=float, help='Limit price (if LIMIT)')
    twap_parser.add_argument('--test', action='store_true', help='Test mode')
    twap_parser.set_defaults(func=cmd_twap_order)

    # Grid strategy command
    grid_parser = subparsers.add_parser('grid', help='Execute grid strategy')
    grid_parser.add_argument('symbol', help='Trading pair')
    grid_parser.add_argument('lower', type=float, help='Lower price bound')
    grid_parser.add_argument('upper', type=float, help='Upper price bound')
    grid_parser.add_argument('--grids', type=int, default=10, help='Number of grids')
    grid_parser.add_argument('--qty', type=float, default=0.1, dest='quantity',
                             help='Total quantity')
    grid_parser.add_argument('--type', dest='grid_type', default='LONG',
                             choices=['LONG', 'SHORT'], help='Grid type')
    grid_parser.add_argument('--test', action='store_true', help='Test mode')
    grid_parser.set_defaults(func=cmd_grid_order)

    # Status command
    status_parser = subparsers.add_parser('status', help='Check order/strategy status')
    status_parser.add_argument('type', choices=['market', 'limit', 'stop_limit', 'twap', 'grid'])
    status_parser.add_argument('order_id', type=int, help='Order or strategy ID')
    status_parser.add_argument('--symbol', help='Trading pair (for limit/stop-limit)')
    status_parser.set_defaults(func=cmd_status)

    # History command
    history_parser = subparsers.add_parser('history', help='View order/strategy history')
    history_parser.add_argument('type', choices=['market', 'limit', 'twap', 'grid'])
    history_parser.set_defaults(func=cmd_history)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Critical Error: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()

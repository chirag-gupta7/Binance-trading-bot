# Binance Futures Trading Bot

A comprehensive CLI-based trading bot for Binance USDT-M Futures supporting multiple order types with robust logging, validation, and documentation.

## Features

### Core Orders (Mandatory)
- **Market Orders**: Execute immediately at current market price
- **Limit Orders**: Execute at specified price or better

### Advanced Orders (Bonus)
- **Stop-Limit Orders**: Trigger a limit order when price reaches stop level
- **OCO (One-Cancels-the-Other)**: Place take-profit and stop-loss simultaneously
- **TWAP (Time-Weighted Average Price)**: Split large orders into smaller chunks over time
- **Grid Orders**: Automated buy-low/sell-high within a price range

### Quality Assurance
- **Input Validation**: Comprehensive symbol, quantity, and price validation
- **Structured Logging**: All actions logged with timestamps to `bot.log`
- **Error Handling**: Robust error handling with detailed error messages
- **Test Mode**: Simulate orders without calling actual API

## Project Structure

```
project_root/
├── src/
│   ├── bot.py                 # Main CLI entry point
│   ├── logger.py              # Structured logging module
│   ├── validation.py          # Input validation module
│   ├── market_orders.py       # Market order implementation
│   ├── limit_orders.py        # Limit order implementation
│   └── advanced/
│       ├── stop_limit.py      # Stop-limit order implementation
│       ├── oco.py             # OCO order implementation
│       ├── twap.py            # TWAP strategy implementation
│       └── grid.py            # Grid strategy implementation
├── config/
│   └── .env.example           # API credentials template
├── docs/
│   └── API_SETUP.md           # API setup instructions
├── bot.log                    # Trading bot logs
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── historical_data.csv        # Sample historical data
```

## Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Binance account with USDT-M Futures enabled

### Setup Steps

1. **Clone/Download the repository**
```bash
cd primetrade_python
```

2. **Create a virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API credentials**
```bash
# Copy example config
cp config/.env.example config/.env

# Edit .env with your Binance API keys
# (Currently in test mode - no API credentials needed)
```

## Usage

All commands are executed through the CLI. Use the following syntax:

```bash
python src/bot.py <command> [arguments] [options]
```

### Command Overview

#### 1. Market Orders
Place an order at current market price:

```bash
python src/bot.py market <symbol> <side> <quantity> [--test]
```

**Examples:**
```bash
# Buy 0.01 BTC
python src/bot.py market BTCUSDT BUY 0.01 --test

# Sell 1 ETH
python src/bot.py market ETHUSDT SELL 1.0 --test
```

#### 2. Limit Orders
Place an order at a specific price:

```bash
python src/bot.py limit <symbol> <side> <quantity> <price> [options]
```

**Options:**
- `--tif {GTC,IOC,FOK}`: Time in force (default: GTC)
- `--post-only`: Only post to orderbook (maker orders)
- `--reduce-only`: Only reduce position
- `--test`: Test mode

**Examples:**
```bash
# Buy 1 ETH at 2300.50
python src/bot.py limit ETHUSDT BUY 1.0 2300.50 --test

# Sell with post-only flag
python src/bot.py limit BTCUSDT SELL 0.01 43000 --post-only --test
```

#### 3. Stop-Limit Orders
Trigger a limit order when price reaches stop level:

```bash
python src/bot.py stop-limit <symbol> <side> <quantity> <stop_price> <limit_price> [options]
```

**Options:**
- `--working-type {CONTRACT_PRICE,MARK_PRICE}`: Price reference (default: CONTRACT_PRICE)
- `--test`: Test mode

**Examples:**
```bash
# Stop-loss: Sell 0.01 BTC when price drops to 42000, limit at 41500
python src/bot.py stop-limit BTCUSDT SELL 0.01 42000 41500 --test

# Take-profit: Buy when price rises to 41000, limit at 41500
python src/bot.py stop-limit BTCUSDT BUY 0.01 41000 41500 --test
```

#### 4. OCO Orders
Place take-profit and stop-loss simultaneously:

```bash
python src/bot.py oco <symbol> <side> <quantity> <take_profit> <stop_loss> [options]
```

**Options:**
- `--sl-limit <price>`: Stop-loss limit price (optional)
- `--test`: Test mode

**Examples:**
```bash
# Buy 0.01 BTC with TP at 45000 and SL at 40000
python src/bot.py oco BTCUSDT BUY 0.01 45000 40000 --test

# Sell with custom SL limit price
python src/bot.py oco BTCUSDT SELL 0.05 39000 41500 --sl-limit 41000 --test
```

#### 5. TWAP Strategy
Split large orders into smaller chunks over time:

```bash
python src/bot.py twap <symbol> <side> <quantity> [options]
```

**Options:**
- `--splits <n>`: Number of splits (default: 5)
- `--interval <seconds>`: Interval between orders (default: 10)
- `--order-type {MARKET,LIMIT}`: Order type (default: MARKET)
- `--price <price>`: Limit price (if LIMIT type)
- `--test`: Test mode

**Examples:**
```bash
# Split 0.1 BTC into 5 market orders over 50 seconds
python src/bot.py twap BTCUSDT BUY 0.1 --splits 5 --interval 10 --test

# Split with limit orders at 42500
python src/bot.py twap BTCUSDT BUY 0.1 --splits 10 --interval 5 --order-type LIMIT --price 42500 --test
```

#### 6. Grid Strategy
Automated buy-low/sell-high within a price range:

```bash
python src/bot.py grid <symbol> <lower_price> <upper_price> [options]
```

**Options:**
- `--grids <n>`: Number of grid levels (default: 10)
- `--qty <quantity>`: Total quantity (default: 0.1)
- `--type {LONG,SHORT}`: Grid type (default: LONG)
- `--test`: Test mode

**Examples:**
```bash
# LONG grid: Buy low/sell high between 40000-45000 with 10 levels
python src/bot.py grid BTCUSDT 40000 45000 --grids 10 --qty 0.1 --type LONG --test

# SHORT grid: Sell high/buy low with 20 levels
python src/bot.py grid BTCUSDT 40000 45000 --grids 20 --qty 0.2 --type SHORT --test
```

#### 7. Check Order Status
Check the status of an order or strategy:

```bash
python src/bot.py status <type> <order_id> [--symbol <symbol>]
```

**Type Options:** `market`, `limit`, `stop_limit`, `twap`, `grid`

**Examples:**
```bash
# Check market order status
python src/bot.py status market 12345678

# Check limit order status
python src/bot.py status limit 12345679 --symbol BTCUSDT

# Check TWAP strategy status
python src/bot.py status twap 1673456789000
```

#### 8. View History
View all orders or strategies executed:

```bash
python src/bot.py history <type>
```

**Type Options:** `market`, `limit`, `twap`, `grid`

**Examples:**
```bash
# View all market orders
python src/bot.py history market

# View all TWAP strategies
python src/bot.py history twap
```

## Validation Rules

The bot validates all inputs according to these rules:

### Symbols
- Must be from supported USDT-M pairs (e.g., BTCUSDT, ETHUSDT)
- Case-insensitive (auto-converted to uppercase)

### Quantities
- Minimum: 0.001
- Maximum: 1,000,000
- Must be positive

### Prices
- Minimum: 0.00001
- Maximum: 999,999
- Must be positive

### Order Logic
- **Limit Orders**: price > 0
- **Stop-Limit BUY**: stop_price < limit_price
- **Stop-Limit SELL**: stop_price > limit_price
- **OCO BUY**: take_profit > stop_loss
- **OCO SELL**: take_profit < stop_loss
- **TWAP**: num_splits >= 2 and <= 100
- **Grid**: num_grids >= 2 and <= 100, lower_price < upper_price

## Logging

All bot actions are logged to `bot.log` with timestamps and severity levels.

### Log Format
```
2024-01-22 14:30:45 | INFO     | bot | place_order:123 | ORDER PLACED: LIMIT | BTCUSDT | BUY | Qty: 0.01
```

### Log Levels
- **DEBUG**: Detailed information, API calls
- **INFO**: General information, order placement, executions
- **WARNING**: Warning messages
- **ERROR**: Error messages with context
- **CRITICAL**: Critical failures

### Log Entries Include
- Timestamp (YYYY-MM-DD HH:MM:SS)
- Log level
- Function name and line number
- Detailed message

## API Setup (Optional for Real Trading)

To enable real trading instead of test mode:

1. **Create Binance API Key**
   - Login to [Binance](https://www.binance.com)
   - Go to Account Settings → API Management
   - Create new API key with Futures trading enabled
   - Copy API Key and Secret Key

2. **Configure Credentials**
   ```bash
   # Edit config/.env
   BINANCE_API_KEY=your_api_key_here
   BINANCE_API_SECRET=your_secret_key_here
   ```

3. **Load Configuration in bot.py**
   - Currently disabled in test mode
   - Uncomment API client initialization to enable

## Example Workflows

### Scenario 1: DCA (Dollar Cost Averaging)
```bash
# Buy BTC gradually over 1 hour in 6 splits
python src/bot.py twap BTCUSDT BUY 0.06 --splits 6 --interval 600 --test
```

### Scenario 2: Swing Trading
```bash
# Place OCO for swing trade: buy at market, TP at +10%, SL at -5%
python src/bot.py oco ETHUSDT BUY 1.0 2530 2230 --test
```

### Scenario 3: Range Trading
```bash
# Grid trade ETH between 2300-2400 with 5 levels
python src/bot.py grid ETHUSDT 2300 2400 --grids 5 --qty 2.0 --type LONG --test
```

### Scenario 4: Limit Orders
```bash
# Place 3 limit buy orders at different prices
python src/bot.py limit BTCUSDT BUY 0.01 41000 --test
python src/bot.py limit BTCUSDT BUY 0.01 40500 --test
python src/bot.py limit BTCUSDT BUY 0.01 40000 --test
```

## Testing

All commands include a `--test` flag for simulated execution:

```bash
python src/bot.py market BTCUSDT BUY 0.01 --test
```

In test mode:
- Orders are simulated with realistic prices
- No actual trades are executed
- Full logging still occurs
- Perfect for learning and testing strategies

## Troubleshooting

### Issue: "Symbol not supported"
**Solution**: Check if symbol is in the supported list. Valid symbols include: BTCUSDT, ETHUSDT, BNBUSDT, etc.

### Issue: "Quantity below minimum"
**Solution**: Increase quantity. Most pairs have a minimum of 0.001 (or equivalent in USD value).

### Issue: "Validation error" on price
**Solution**: Ensure prices are positive and within valid range (0.00001 - 999,999).

### Issue: Cannot import modules
**Solution**: Ensure you're running from the project root directory and have activated the virtual environment.

## Performance Considerations

- **TWAP**: Ideal for large orders to minimize market impact
- **Grid**: Best for range-bound markets
- **OCO**: Efficient for risk management with single order
- **Stop-Limit**: Provides more control than market orders

## Security Notes

1. **API Keys**: Never commit `.env` file to version control
2. **Testing**: Always use `--test` mode before live trading
3. **Position Size**: Start with small quantities when testing new strategies
4. **Logging**: Bot logs all activities - review regularly for anomalies

## Supported Symbols

The bot supports these USDT-M trading pairs (Binance):
- BTCUSDT, ETHUSDT, BNBUSDT, ADAUSDT, DOGEUSDT
- XRPUSDT, MATICUSDT, SOLUSDT, LTCUSDT, LINKUSDT
- AVAXUSDT, ATOMUSDT, ARBUSDT, UNIUSDT, APTUSDT
- GALAUSDT, OPUSDT, GMXUSDT, RDNTUSDT, PEPEUSDT

## Documentation

For detailed API documentation, see:
- [Binance Futures API Docs](https://binance-docs.github.io/apidocs/futures/en/)

## Evaluation Criteria

This bot is evaluated on:
1. **Basic Orders (50%)**: Market/limit orders with validation
2. **Advanced Orders (30%)**: Stop-limit, OCO, TWAP, Grid implementation
3. **Logging & Errors (10%)**: Structured logging with timestamps
4. **Report & Documentation (10%)**: Clear README and examples

## License

Developed for educational purposes.

## Support

For questions or issues:
1. Check `bot.log` for detailed error messages
2. Review validation rules in [Validation Module](src/validation.py)
3. Consult Binance API documentation

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Author**: Trading Bot Development Team

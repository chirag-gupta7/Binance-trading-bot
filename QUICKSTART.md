# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Trading (Test Mode)
```bash
# Market order
python src/bot.py market BTCUSDT BUY 0.01 --test

# Limit order
python src/bot.py limit ETHUSDT BUY 1.0 2300 --test

# OCO order (take-profit + stop-loss)
python src/bot.py oco BTCUSDT BUY 0.01 45000 40000 --test

# Grid strategy
python src/bot.py grid BTCUSDT 40000 45000 --grids 10 --qty 0.1 --test

# TWAP strategy (split 0.1 BTC over 5 orders)
python src/bot.py twap BTCUSDT BUY 0.1 --splits 5 --interval 10 --test
```

## Real Trading Setup

### 1. Get Binance API Keys
- Login to [Binance](https://www.binance.com)
- Go to Account → API Management
- Create API key with Futures trading enabled
- Copy API Key and Secret Key

### 2. Configure Credentials
Edit `config/.env`:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_secret_here
```

### 3. Trade (Remove --test flag)
```bash
python src/bot.py market BTCUSDT BUY 0.01
```

## Command Reference

| Command | Syntax | Example |
|---------|--------|---------|
| Market | `market <symbol> <side> <qty>` | `market BTCUSDT BUY 0.01` |
| Limit | `limit <symbol> <side> <qty> <price>` | `limit ETHUSDT BUY 1.0 2300.50` |
| Stop-Limit | `stop-limit <symbol> <side> <qty> <stop> <limit>` | `stop-limit BTCUSDT SELL 0.01 42000 41500` |
| OCO | `oco <symbol> <side> <qty> <tp> <sl>` | `oco BTCUSDT BUY 0.01 45000 40000` |
| TWAP | `twap <symbol> <side> <qty> --splits N --interval S` | `twap BTCUSDT BUY 0.1 --splits 5 --interval 10` |
| Grid | `grid <symbol> <lower> <upper> --grids N --qty Q` | `grid BTCUSDT 40000 45000 --grids 10 --qty 0.1` |

## Supported Symbols

BTCUSDT, ETHUSDT, BNBUSDT, ADAUSDT, DOGEUSDT, XRPUSDT, MATICUSDT, SOLUSDT, LTCUSDT, LINKUSDT, and more!

## Check Logs
```bash
tail -f bot.log
```

## Get Help
```bash
python src/bot.py --help
python src/bot.py market --help
```

---

**Next**: Read `README.md` for detailed documentation!

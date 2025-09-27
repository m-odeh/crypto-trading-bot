# crypto-trading-bot

Wave Trend momentum trading bot with trailing stop-loss for cryptocurrency markets.

---

## Strategy Overview

**Entry Signal:**
- Wave Trend Oscillator crossover (WT1 crosses above WT2) 
- Oversold condition (WT2 ≤ -20)
- On-Balance Volume confirmation (increasing)
- BTC sentiment filter (24h change > threshold)

**Exit Strategy:**
- Dynamic trailing stop-loss (adjustable distance)
- ATR-based initial stop-loss (2x ATR)
- 4-hour maximum position time
- Market orders for immediate exits

---

## Features

- **Paper & Live Trading** - Test safely before risking capital
- **15-minute timeframe** - Momentum-based scalping strategy  
- **Multi-indicator signals** - Wave Trend, OBV, ATR, Stochastic
- **Risk management** - Trailing stops with time limits
- **Trade logging** - Complete CSV records
- **Market filtering** - BTC sentiment-based trading conditions

---

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Parameters
Edit these variables in the script:

**Trading Pairs:**
```python
pairs_list = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT']
```

**Bot Settings:**
```python
paper_trading = True              # Set False for live trading
balance_usdt = 1000              # Starting balance (paper mode)
btc_24change_threshold = -5      # Min BTC 24h change to trade
trail = 0.003                    # 0.3% trailing stop distance
profit = 0.005                   # 0.5% profit target (for logging)
```

**API Configuration:**
```python
api_key = "your_binance_api_key"
api_secret = "your_binance_secret"
```

### 3. Create Required Files
Ensure you have `get_signal.py` with the following functions:
- `get_historical_ohlc_data(symbol, interval)`
- Required TA library imports

---

## Usage

### Start the Bot
```bash
python bot.py
```

### Monitor Output
The bot will display:
- Candle synchronization timing
- BTC market conditions
- Entry/exit signals
- Trade execution details
- P&L calculations

### Trade Logging
All trades are saved to `trades_log.csv` with columns:
```
Time, signal type, Asset, Amount in coin, Balance in USDT, 
Price, ATR, target price, stop loss, Profit, btc 24 change, stock_k
```

---

## Strategy Details

### Technical Indicators
- **Wave Trend Oscillator (9,12)** - Primary signal generator
- **On Balance Volume** - Volume confirmation
- **Average True Range** - Dynamic stop-loss calculation
- **Stochastic** - Momentum confirmation
- **RSI, EMA, MFI** - Additional market analysis

### Risk Parameters
- **Initial Stop:** Entry price - (2 × ATR)
- **Trailing Distance:** 0.3% (configurable)
- **Maximum Hold:** 4 hours
- **Position Sizing:** Full balance per trade

### Order Types
- **Entry:** Limit orders at signal price
- **Exit:** Market orders for immediate execution

---

## Important Warnings

⚠️ **This bot trades real money when `paper_trading = False`**

**Before Live Trading:**
1. Test extensively in paper mode
2. Understand the strategy logic completely
3. Start with small amounts
4. Monitor performance closely
5. Ensure stable internet connection

**Risk Factors:**
- Cryptocurrency markets are highly volatile
- 0.3% trailing stops may be too tight for some conditions
- Limit buy orders may miss signals in fast markets
- No guarantee of profitability

**Legal Disclaimer:** This software is for educational purposes. Trading cryptocurrencies involves substantial risk of loss. Use at your own risk.

---

# Quantitative Trading: Market Making Simulator

A Python-based backtesting engine designed to simulate Market Making strategies on high-frequency equity data (AAPL 1-minute intervals). This project explores the evolution of a market-making bot, moving from basic statistical mean reversion to a risk-aware, trend-filtered system.

## 🚀 Overview
The goal of this project was to develop a market-making framework that provides liquidity while managing **Inventory Risk** and **Adverse Selection**. The project is split into four progressive iterations, each addressing a specific challenge found in real-world trading environments.

---

## 🛠️ Project Structure

### v1.0: Basic SMA Mean Reversion (`main_v1.py`)
* **Strategy:** Used a Simple Moving Average (SMA) as the "Fair Price."
* **Logic:** Placed Bids and Asks at a fixed distance from the SMA.
* **Challenge:** Identified "Lag" in the fair price calculation, leading to entries based on outdated price levels.

### v2.0: Exponential Smoothing (`main_v2.py`)
* **Improvement:** Replaced SMA with an **Exponential Moving Average (EMA)**.
* **Logic:** EMA gives more weight to recent prices, reducing lag.
* **Result:** Improved response time to price shifts, though the strategy remained vulnerable to strong trends.

### v3.0: Volatility-Adaptive Bollinger Bands (`main_v3.py`)
* **Improvement:** Implemented **Bollinger Bands ($2.5\sigma$)** to define the spread.
* **Logic:** Instead of a fixed spread, the bot dynamically widens its quotes during high volatility.
* **Result:** Increased selectivity, significantly reducing "bleeding" during low-conviction market moves.

### v4.0: Trend-Aware Regime Filter (`main_v4.py`)
* **Improvement:** Integrated a **Regime Detection Filter** (50-period SMA) and **Asymmetric Inventory Limits**.
* **Logic:** The bot detects the market trend. In a Bull market, it allows a larger Long position (+10) but caps Short exposure (-2) to prevent fighting the trend.
* **Result:** Successfully mitigated massive adverse selection losses during trending periods.

---

## 📈 Key Quantitative Concepts Implemented

### 1. Inventory Skewing
To maintain a delta-neutral position, the bot shifts its quotes based on current holdings. If the bot is "Long," it lowers its Ask price to attract sellers and lower its "Bid" to avoid buying more.

### 2. Adverse Selection Mitigation
By using Bollinger Bands and Trend Filters, the bot avoids the "Toxic Flow" of being filled only when the market is moving strongly against its position.

### 3. Backtesting with Real-World Constraints
* **Look-ahead Bias Prevention:** Orders are calculated at $T-1$ and filled at $T$ based on the High/Low of the candle.
* **Inventory Constraints:** Hard limits on position sizing to simulate capital risk limits.

---

## 📊 Performance Visualization

### Equity Curve & Inventory Management
Below is the performance of the final Trend-Aware iteration.

> **[INSERT_EQUITY_CURVE_IMAGE_HERE]**

*The top chart shows the Total Equity (PnL) including unrealized gains/losses. The bottom chart illustrates how the Trend Filter successfully maintains asymmetric inventory levels.*

---

## 🧪 Installation & Usage
1. Clone the repository.
2. Ensure you have the dependencies: `pip install pandas numpy matplotlib yfinance`
3. Run the final iteration:
   ```bash
   python main_v4.

---
   
## 📝 Conclusion & Future Improvements
While the backtest reflects the difficulties of mean-reverting in trending regimes, the project demonstrates a robust framework for Inventory Management. Future versions would explore:

Order Book Imbalance: Incorporating L2 data to improve fair price estimation.

Machine Learning: Using an LSTM to predict short-term volatility regime.


---
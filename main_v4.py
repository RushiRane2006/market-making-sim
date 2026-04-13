import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class TrendAwareMarketMaker:
    def __init__(self, data, initial_cash=100000, bb_std=2.0):
        self.df = data.copy()
        self.initial_cash = initial_cash
        self.bb_std = bb_std
        
        self.cash = initial_cash
        self.inventory = 0
        self.pnl_history = []
        self.inventory_history = []

    def run(self):
        # 1. Technical Indicators
        self.df['mid_band'] = self.df['Close'].ewm(span=20, adjust=False).mean()
        self.df['std_dev'] = self.df['Close'].rolling(window=20).std()
        
        # Trend Filter: 50-period SMA
        self.df['trend_sma'] = self.df['Close'].rolling(window=50).mean()
        
        # Bollinger Bands
        self.df['upper_band'] = self.df['mid_band'] + (self.df['std_dev'] * self.bb_std)
        self.df['lower_band'] = self.df['mid_band'] - (self.df['std_dev'] * self.bb_std)
        
        self.df = self.df.dropna()

        current_bid = 0
        current_ask = 0

        for i, row in self.df.iterrows():
            # 2. Fill Logic (Execution)
            if current_bid > 0 and row['Low'] <= current_bid:
                # Dynamic Long Limit: 10 if Bullish, 2 if Bearish
                long_limit = 10 if row['Close'] > row['trend_sma'] else 2
                if self.inventory < long_limit:
                    self.cash -= current_bid
                    self.inventory += 1
            
            if current_ask > 0 and row['High'] >= current_ask:
                # Dynamic Short Limit: -10 if Bearish, -2 if Bullish
                short_limit = -10 if row['Close'] < row['trend_sma'] else -2
                if self.inventory > short_limit:
                    self.cash += current_ask
                    self.inventory -= 1

            # 3. Order Calculation
            fair = row['mid_band']
            vol = row['std_dev'] if row['std_dev'] > 0 else 0.01
            
            # Inventory Skew (Risk Management)
            # We use a 10-unit scale for skew calculation
            skew = (self.inventory / 10) * (vol * 1.5)
            
            current_bid = row['lower_band'] - skew
            current_ask = row['upper_band'] - skew

            # 4. Record Performance
            total_value = self.cash + (self.inventory * row['Close'])
            self.pnl_history.append(total_value)
            self.inventory_history.append(self.inventory)

        self.df['PnL'] = self.pnl_history
        self.df['Inventory'] = self.inventory_history
        return self.df

    def plot_results(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), sharex=True)
        
        ax1.plot(self.df.index, self.df['PnL'], color='forestgreen', label='Total Equity')
        ax1.set_title(f'Trend-Aware Equity Curve', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        ax2.step(self.df.index, self.df['Inventory'], color='darkorange', label='Inventory')
        ax2.axhline(0, color='black', linestyle='--', alpha=0.5)
        ax2.set_title('Asymmetric Inventory (Trend-Filtered)', fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

# Execution
df = pd.read_csv("apple_data.csv", parse_dates=True)

tester = TrendAwareMarketMaker(df, bb_std=2.0)
results = tester.run()
tester.plot_results()
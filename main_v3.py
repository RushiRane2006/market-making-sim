import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class MarketMakerBacktester:
    def __init__(self, data, inventory_limit=10, initial_cash=100000, bb_std=2.5):
        self.df = data.copy()
        self.limit = inventory_limit
        self.initial_cash = initial_cash
        self.bb_std = bb_std  # Number of Standard Deviations for the bands
        
        # Performance Tracking
        self.cash = initial_cash
        self.inventory = 0
        self.pnl_history = []
        self.inventory_history = []

    def run(self):
        # 1. Technical Indicators
        # Middle Band: 20-period EMA
        self.df['mid_band'] = self.df['Close'].ewm(span=20, adjust=False).mean()
        # Volatility: 20-period Standard Deviation
        self.df['std_dev'] = self.df['Close'].rolling(window=20).std()
        
        # Calculate Bollinger Bands
        self.df['upper_band'] = self.df['mid_band'] + (self.df['std_dev'] * self.bb_std)
        self.df['lower_band'] = self.df['mid_band'] - (self.df['std_dev'] * self.bb_std)
        
        self.df = self.df.dropna()

        # Previous minute's orders (we set orders at T-1 to be hit at T)
        current_bid = 0
        current_ask = 0

        for i, row in self.df.iterrows():
            # 2. Check for Fills (Execution Logic)
            # Did the market touch our Bid or Ask from the PREVIOUS minute?
            if current_bid > 0 and row['Low'] <= current_bid and self.inventory < self.limit:
                self.cash -= current_bid
                self.inventory += 1
            
            if current_ask > 0 and row['High'] >= current_ask and self.inventory > -self.limit:
                self.cash += current_ask
                self.inventory -= 1

            # 3. Bollinger-Based Order Logic
            # Instead of a constant spread, we use the Bands as our target entry/exit
            fair = row['mid_band']
            vol = row['std_dev'] if row['std_dev'] > 0 else 0.01
            
            # Inventory Skew (Keep this! It's your primary risk control)
            skew = (self.inventory / self.limit) * (vol * 1.5)
            
            # Place Bid at the Lower Band and Ask at the Upper Band
            # This makes the bot much more selective
            current_bid = row['lower_band'] - skew
            current_ask = row['upper_band'] - skew

            # 4. Recording
            total_value = self.cash + (self.inventory * row['Close'])
            self.pnl_history.append(total_value)
            self.inventory_history.append(self.inventory)

        self.df['PnL'] = self.pnl_history
        self.df['Inventory'] = self.inventory_history
        return self.df

    def plot_results(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # Plot PnL (Equity Curve)
        ax1.plot(self.df.index, self.df['PnL'], color='green', label='Total Equity')
        ax1.set_title('Strategy Equity Curve (PnL)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Plot Inventory
        ax2.step(self.df.index, self.df['Inventory'], color='orange', label='Inventory Position')
        ax2.axhline(0, color='black', linestyle='--', alpha=0.5)
        ax2.set_title('Inventory Management (Position Sizing)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()
        plt.show()

df = pd.read_csv("apple_data.csv", parse_dates=True)
tester = MarketMakerBacktester(df)
results = tester.run()
tester.plot_results()
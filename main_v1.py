import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class MarketMakerBacktester:
    def __init__(self, data, inventory_limit=10, initial_cash=100000):
        self.df = data.copy()
        self.limit = inventory_limit
        self.initial_cash = initial_cash
        
        # Performance Tracking
        self.cash = initial_cash
        self.inventory = 0
        self.pnl_history = []
        self.inventory_history = []

    def run(self):
        # 1. Pre-calculate 'Fair Price' and Volatility
        # We use a 20-period rolling window to avoid 'predicting the future'
        self.df['fair_price'] = self.df['Close'].rolling(window=20).mean()
        self.df['volatility'] = self.df['Close'].rolling(window=20).std()
        
        # Drop rows where we don't have enough data for the mean yet
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

            # 3. Calculate Orders for NEXT minute
            fair = row['fair_price']
            vol = row['volatility'] if row['volatility'] > 0 else 0.01
            
            # Inventory Skew: If we are 'Long', we lower our prices to encourage a sell
            # If we are 'Short', we raise our prices to encourage a buy
            skew = (self.inventory / self.limit) * (vol * 0.5)
            
            current_bid = fair - (vol * 0.5) - skew
            current_ask = fair + (vol * 0.5) - skew

            # 4. Record Performance
            # Total Value = Cash + (What our stock is worth right now)
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
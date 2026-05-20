from backtesting import Backtest
from backtesting import Strategy

class AITradingStrategy(Strategy):

    def init(self):
        pass

    def next(self):

        if self.data.Close[-1] > self.data.Close[-2]:
            self.buy()

        else:
            self.sell()
import datetime

class CryptoTrade:
    def __init__(self, symbol, quantity, price, fees, trade_type, timestamp=None):
        """
        Initializes a new crypto trade.

        Args:
            symbol (str): crypto symbol (BTC, ETH, etc.).
            quantity (float): The quantity of the asset traded.
            price (float): The price at which the trade was executed.
            fees (float): The fees paid for the trade.
            trade_type (str): The type of the trade, either "buy" or "sell".
            timestamp (datetime.datetime, optional): 
                The timestamp of the trade. Defaults to the current time.
        Raises:
          ValueError: 
            If trade_type is not "buy" or "sell".
        """

        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.fees = fees
        self.trade_type = trade_type.lower() # Konvertiere zu Kleinbuchstaben für Robustheit
        if self.trade_type not in ("buy", "sell"):
          raise ValueError("Trade type must be 'buy' or 'sell'.")

        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now()

    def __str__(self):
        """
        String representation of the trade.
        """
        return (f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - "
                f"{self.trade_type.upper()}: {self.quantity} {self.symbol} @ {self.price}")

    def value(self):
        """
        Calculates the value of the trade.
        """
        return self.quantity * self.price
    

class CryptoTrades:
    def __init__(self):
        """
        Initializes a new trade tracker.
        """
        self.trades = []

    def add_trade(self, trade: CryptoTrade):
        """
        Adds a new trade to the tracker.

        Args:
            trade (CryptoTrade): The trade to add.
        Raises:
            TypeError: If trade is not a CryptoTrade object.
        """
        if not isinstance(trade, CryptoTrade):
          raise TypeError("Only CryptoTrade objects can be added.")
        self.trades.append(trade)

    def get_trades(self, symbol=None) -> list[CryptoTrade]:
        """
        Returns a list of trades, optionally filtered by symbol.

        Args:
            symbol (str, optional): The symbol to filter by.

        Returns:
            list: A list of trades.
        """
        if symbol:
            return [trade for trade in self.trades if trade.symbol == symbol]
        return self.trades

    def total_value(self, symbol=None):
      """
      Returns the total value of all trades, optionally filtered by symbol.

      Args:
          symbol (str, optional): 

      Returns:
          float: The total value of all trades.
      """
      trades = self.get_trades(symbol)
      return sum(trade.value() for trade in trades)
    
    def total_fees(self, symbol=None):
        """
        Returns the total fees paid for all trades, optionally filtered by symbol.
    
        Args:
            symbol (str, optional): The symbol to filter by.
    
        Returns:
            float: The total fees paid for all trades.
        """
        trades = self.get_trades(symbol)
        return sum(trade.fees for trade in trades)

    def profit_loss(self, symbol):
        """
        Calculates the profit/loss for a given symbol.

        Args:
            symbol (str): The symbol to calculate the profit/loss for.

        Returns:
            float: The profit/loss for the symbol.
            None: If no trades are found for the symbol.
        """
        trades = self.get_trades(symbol)
        if not trades:
            return None

        total_bought = 0
        total_sold = 0
        for trade in trades:
            if trade.trade_type == "buy":
                total_bought += trade.value()
            elif trade.trade_type == "sell":
                total_sold += trade.value()

        return total_sold - total_bought - self.total_fees(symbol)


import unittest

from crypto_trades import CryptoTrades, CryptoTrade

class TestCryptoTrades(unittest.TestCase):

    def test_add_trade(self):
        trades = CryptoTrades()
        self.assertEqual(len(trades.trades), 0)
        trades.add_trade(CryptoTrade("BTC", 1.0, 10000.0, 10.0, "buy"))
        self.assertEqual(len(trades.trades), 1)
        trades.add_trade(CryptoTrade("BTC", 1.0, 20000.0, 10.0, "sell"))
        self.assertEqual(len(trades.trades), 2)

    def test_add_trade_invalid_trade_type(self):
        trades = CryptoTrades()
        with self.assertRaises(ValueError):
            trades.add_trade(CryptoTrade("BTC", 1.0, 10000.0, 10.0, "invalid"))

    def test_total_value(self):
        trades = CryptoTrades()
        trades.add_trade(CryptoTrade("BTC", 1.0, 10000.0, 10.0, "buy"))
        trades.add_trade(CryptoTrade("BTC", 1.0, 5000.0, 10.0, "sell"))
        self.assertEqual(trades.total_value(), 15000.0)

    def test_total_value(self):
        trades = CryptoTrades()
        trades.add_trade(CryptoTrade("BTC", 1.0, 10000.0, 10.0, "buy"))
        trades.add_trade(CryptoTrade("BTC", 1.0, 5000.0, 10.0, "sell"))
        self.assertEqual(trades.total_fees(), 20.0)


    def test_total_value_no_trades(self):
        trades = CryptoTrades()
        self.assertEqual(trades.total_value(), 0.0)

    def test_profit_loss(self):
        trades = CryptoTrades()
        trades.add_trade(CryptoTrade("BTC", 1.0, 10000.0, 10.0, "buy"))
        trades.add_trade(CryptoTrade("BTC", 1.0, 20000.0, 10.0, "sell"))
        self.assertEqual(trades.profit_loss("BTC"), 9980.0)

    def test_profit_loss(self):
        trades = CryptoTrades()
        trades.add_trade(CryptoTrade("BTC", 1.0, 10000.0, 10.0, "buy"))
        trades.add_trade(CryptoTrade("BTC", 1.0, 5000.0, 10.0, "sell"))
        self.assertEqual(trades.profit_loss("BTC"), -5020.0)


    def test_profit_loss_no_trades(self):
        trades = CryptoTrades()
        self.assertIsNone(trades.profit_loss("BTC"))

    def test_profit_loss_no_trades_for_symbol(self):
        trades = CryptoTrades()
        trades.add_trade(CryptoTrade("BTC", 1.0, 10000.0, 10.0, "buy"))
        self.assertIsNone(trades.profit_loss("ETH"))


if __name__ == '__main__':

    unittest.main()


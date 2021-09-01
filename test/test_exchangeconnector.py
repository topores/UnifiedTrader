import unittest
import datetime

import pandas as pd

from src.exchangeconnector import ExchangeConnector
from src.static import Action


class ExchangeConnectorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.exchange_connector = ExchangeConnector(test=True)

    def test_get_ticker_history(self):
        result = self.exchange_connector.get_ticker_history(ticker='BTCUSDT', timeframe='15m', history_length=129)
        ts = result['time'].iloc[-1] / 1000
        dt = datetime.datetime.fromtimestamp(ts)
        self.assertIn(len(result), [128, 129], "wrong length of dataframe")
        self.assertLessEqual(dt, datetime.datetime.now() - datetime.timedelta(minutes=0), "wrong time")
        self.assertGreaterEqual(dt, datetime.datetime.now() - datetime.timedelta(minutes=30), "wrong time")

    def test_get_ticker_history_with_threadpool(self):
        timeframe = '15m'
        history_length = 120

        tickers_to_get = list(list(zip(*self.exchange_connector.info))[0])
        print(tickers_to_get)
        results = self.exchange_connector.get_ticker_history_with_threadpool(tickers_to_get=tickers_to_get,
                                                                             timeframe=timeframe,
                                                                             history_length=history_length)

        self.assertIsInstance(results, list)

        result_dict = dict(zip(tickers_to_get, results))
        self.assertIsInstance(result_dict, dict)

        if len(results) > 0:
            el = results[0]
            self.assertIsInstance(el, pd.DataFrame)
            self.assertIn(len(el), [history_length, history_length - 1])

    def test_get_balance(self):
        result = self.exchange_connector.get_balance()
        # print(result)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)

    def test_get_balance_info(self):
        result = self.exchange_connector.get_balance_info()
        print(result)
        self.assertIsInstance(result, dict)

        self.assertIsInstance(result['total'], float)
        self.assertGreaterEqual(result['total'], 0)

        self.assertIsInstance(result['free'], float)
        self.assertGreaterEqual(result['free'], 0)


def test_place_order(self):
    result = self.exchange_connector.place_order('BTCUSDT', side=Action.SHORT, amount=1)
    # print(result)
    self.assertIn('order_id', result)
    self.assertIn('timestamp', result)
    self.assertIn('amount', result)

    #####
    tickers = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'XRPUSDT']
    for ticker in tickers:
        with self.assertRaises(ArithmeticError):
            self.exchange_connector.place_order(ticker, side=Action.SHORT, amount=0)


if __name__ == '__main__':
    unittest.main()

import datetime
import unittest
import random

from src.algorithm import Algorithm
from src.static import Position, Action, State
from src.storage import Storage
from test.test_storage import StorageTestCase


class AlgorithmTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = Storage()
        self.algo = Algorithm()

    def _fill_storage(self):
        random.seed()
        self.storage.data = []
        tickers = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'XRPUSDT']
        for i in range(100):
            pos = Position(
                ticker=tickers[random.randint(0, 3)],
                side=(Action.SHORT, Action.LONG)[random.randint(0, 1)],
                amount=random.random() * 5,
                state=(State.READY_TO_OPEN, State.OPENED, State.READY_TO_CLOSE, State.CLOSED)[random.randint(0, 3)],
                order_id=i)
            self.storage._add_position(pos)

    def test_new_last_time(self):
        now = datetime.datetime.now()
        result_time = self.algo.new_last_time(now)
        self.assertGreaterEqual(result_time, now)
        self.assertLessEqual(result_time,
                             now + datetime.timedelta(minutes=self.algo.timeframe_minutes[self.algo.timeframe]))
        self.assertEqual(result_time.second, 0)
        self.assertEqual(result_time.microsecond, 0)
        pass

    def test_define_amount(self):
        now = datetime.datetime.now()
        result_time = self.algo.define_amount(10)
        self.assertIsInstance(result_time, float)
        self.assertGreaterEqual(result_time, 0)
        self.assertGreaterEqual(result_time, self.algo.usd_amount)
        pass


if __name__ == '__main__':
    unittest.main()

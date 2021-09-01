import unittest

from src.static import Position, Action, State
from src.storage import Storage
import random


class StorageTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = Storage()

    def test_add_position(self):
        self.storage.data = []
        pos = Position(
            ticker='ticker',
            side=Action.SHORT,
            amount=0,
            state=State.READY_TO_OPEN)
        self.storage._add_position(pos)
        self.assertEqual(self.storage.data, [pos])

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

    def test_find_position(self):
        self._fill_storage()
        for i in range(100):
            res = self.storage.find_position_idx(i)
            self.assertEqual(res, i)
        res = self.storage.find_position_idx(100)
        self.assertEqual(res, -1)

    def test_remove_position(self):
        self._fill_storage()
        self.storage.remove_position_by_order_id(order_id=3)
        self.assertEqual(len(self.storage.data), 99)
        self.storage.remove_position_by_order_id(order_id=3)
        self.assertEqual(len(self.storage.data), 99)

        res = self.storage.find_position_idx(3)
        self.assertEqual(res, -1)

    def test_get_positions_by_state(self):
        self._fill_storage()
        for state in (State.READY_TO_OPEN, State.OPENED, State.READY_TO_CLOSE, State.CLOSED):
            res = self.storage.get_positions_by_state(state=state)
            count_res = 0
            count = 0
            for pos in res:
                self.assertEqual(pos.state, state)
                count_res += 1
            for pos in self.storage.data:
                if pos.state == state:
                    count += 1
            self.assertEqual(count_res, count)


if __name__ == '__main__':
    unittest.main()

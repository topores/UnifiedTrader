import datetime
from logging_utils.generator import generate_logger
from strategy.basemodel import BaseModel
from src.static import Action, State
import random

from src.storage import Storage

random.seed()


def tf_15m_smooth_func(x):
    return x.replace(minute=(x.minute // 15) * 15)


class Algorithm():

    def __init__(self, test=False):
        self.test = test
        self.data = {}
        self.usd_amount = 0

        self.model = BaseModel()

        self.history_length = 120
        self.timeframe = '15m'
        self.timeframe_minutes = {
            '15m': 15
        }
        self.tickers = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'XRPUSDT', 'ETCUSDT']

        self.timeframe_smooth_func = {
            '15m': tf_15m_smooth_func
        }

        self.logger = generate_logger('invoker.algorithm')
        self.logger.propagate = False

    def new_last_time(self, now):

        last_invoke_time = now + datetime.timedelta(minutes=self.timeframe_minutes[self.timeframe])

        #trim time
        last_invoke_time = last_invoke_time.replace(second=0, microsecond=0)
        last_invoke_time = self.timeframe_smooth_func[self.timeframe](last_invoke_time)

        return last_invoke_time

    def define_amount(self, balance: float):
        leverage = 8.0
        k = 1 / len(self.tickers)
        self.usd_amount = balance * leverage * k
        return self.usd_amount

    def load_data(self, data: dict):
        self.data = data

    def load_storage(self, storage: Storage):
        self.storage = storage

    def _get_tickers_to_check(self):

        return self.tickers

    def analyse_open(self):

        tickers_to_check = self._get_tickers_to_check()
        result = []

        for ticker in tickers_to_check:
            if ticker not in self.data:
                self.logger.critical('Ticker not in algorithm data!')
                continue
            df = self.data[ticker]
            if df is None:
                self.logger.critical(f'Can not nalyse_open for {ticker} due to data is None!')
                return Action.HOLD

            action = self.model.analyse_open(data=df)
            value_pos = self.model.get_value_pos(data=df)
            if self.test:
                action = Action.SHORT

            self.logger.debug(f'Action for {ticker}(closed) is {Action.represent(action)} (value_pos={value_pos})')

            if action != Action.HOLD:
                self.storage.add_position(ticker=ticker,
                                          action=action,
                                          amount=value_pos * self.usd_amount / df['close'].iloc[-1],
                                          info={
                                              'open_price': df['close'].iloc[-1]
                                          })
            result.append({
                'ticker': ticker,
                'action': action,
                'amount': value_pos * self.usd_amount / df['close'].iloc[-1]
            })

        return result

    def analyse_close(self):
        result = []
        poses = self.storage.get_positions_by_state(state=State.OPENED)
        for pos in poses[:]:

            action = self.model.analyse_close(self.data[pos.ticker],
                                              open_price=pos.info['open_price'],
                                              side=pos.side)

            to_close_time = datetime.timedelta(minutes=15 * 6 + 10, seconds=30)

            if datetime.datetime.now() > datetime.datetime.fromtimestamp(
                    pos.timestamp) + to_close_time:
                action = Action.CLOSE

            if self.test:
                action = Action.CLOSE

            self.logger.debug(
                'Action for {position}(opened) is {action}'.format(position=pos, action=Action.represent(action)))

            if action == Action.CLOSE:
                self.storage.update_position_state_by_order_id(order_id=pos.order_id, state=State.READY_TO_CLOSE)

            result.append({
                'position': pos,
                'action': action
            })

        return result

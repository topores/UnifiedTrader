import datetime
import os
from multiprocessing.pool import ThreadPool
from typing import List

from exchange_api.ftx_api import FtxClient
from exchange_api.binance import Binance
from logging_utils.generator import generate_logger
from src.static import *
import logging
import configparser


class ExchangeConnector():
    def __init__(self, test):
        self.test = test
        config = configparser.ConfigParser()
        config.read(f'{os.path.dirname(__file__)}/../service_files/api_keys.ini')

        self.trade_exchange_api = FtxClient(api_key=config['DEFAULT']['api_key'],
                                            api_secret=config['DEFAULT']['api_secret'],
                                            subaccount_name=config['DEFAULT']['subaccount_name'])
        self.data_exchange_api = Binance
        self.info = [
            ('BTCUSDT', 'BTC-PERP'),
            ('ETHUSDT', 'ETH-PERP'),
            ('LTCUSDT', 'LTC-PERP'),
            ('XRPUSDT', 'XRP-PERP'),
            ('ETCUSDT', 'ETC-PERP')
        ]
        self.min_sizes = {
            'BTCUSDT': 0.001,
            'ETHUSDT': 0.001,
            'LTCUSDT': 0.01,
            'XRPUSDT': 1,
            'ETCUSDT': 0.1

        }

        self.timeframes = {
            '15m': '15m'
        }
        self.logger = generate_logger('exchange_connector')
        pass

    def get_ticker_history(self, ticker: str, timeframe: str, history_length: int):
        try:
            df = self.data_exchange_api.get_window(symbol=ticker, timeframe=self.timeframes[timeframe],
                                                   limit=history_length)
            if datetime.datetime.now() - datetime.datetime.fromtimestamp(
                    df['time'].iloc[-1] / 1000) < datetime.timedelta(minutes=6):
                df['close'].iloc[-2] = df['close'].iloc[-1]

                df = df.iloc[:-1]

            return df
        except Exception as e:
            self.logger.critical(
                'Could not get ticker({ticker}) history due to exception(e)'.format(ticker=ticker, e=str(e)))
            return None

    def get_ticker_history_with_threadpool(self, tickers_to_get: List, timeframe: str, history_length: int):
        try:
            p = ThreadPool(len(tickers_to_get))
            print(tickers_to_get)
            params_pool = list(zip(tickers_to_get, [timeframe] * len(tickers_to_get),
                                   [history_length] * len(tickers_to_get)))

            results = p.starmap(self.get_ticker_history, params_pool)

            p.close()
            p.join()
            return results
        except Exception as e:
            self.logger.critical(
                'Could not get ticker({ticker}) history due to exception(e)'.format(ticker=ticker, e=e))
            return None

    def get_balance(self):
        try:
            result = self.trade_exchange_api.get_balances()
        except Exception as e:
            return None

        for el in result:
            if el['coin'] == 'USD':
                return el['total']
        return None

    def get_balance_info(self):
        self.logger.debug('Getting balance info')
        try:
            result = self.trade_exchange_api.get_balances()
        except Exception as e:
            return None

        for el in result:
            if el['coin'] == 'USD':
                return el  # [''free'']
        return None

    # Длинный список параметров
    def place_order(self, pos: Position, invert_side: bool = False):

        if pos.side == Action.SHORT:
            if not invert_side:
                e_side = 'sell'
            else:
                e_side = 'buy'
        elif pos.side == Action.LONG:
            if not invert_side:
                e_side = 'buy'
            else:
                e_side = 'sell'
        else:
            raise ValueError('wrong side value')

        if pos.amount < self.min_sizes[pos.ticker]:
            raise ArithmeticError('Amount less than minimum for pos.ticker')

        try:
            e_ticker = dict(self.info)[pos.ticker]
        except Exception as e:
            raise KeyError('Can not find trade exchange ticker')

        try:
            if not self.test:
                result = self.trade_exchange_api.place_order(market=e_ticker,
                                                             side=e_side,
                                                             price=None,
                                                             size=pos.amount,
                                                             type="market"
                                                             )
            else:
                result = {
                    'size': pos.amount,
                    'id': datetime.datetime.now().timestamp(),
                    'timestamp': datetime.datetime.now().timestamp()
                }
            print(result)

            return {
                'amount': result['size'],
                'order_id': result['id'],
                'timestamp': datetime.datetime.now().timestamp()
            }
        except Exception as e:
            raise e

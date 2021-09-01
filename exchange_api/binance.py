import pandas as pd
import requests
import json
import time
from multiprocessing.pool import ThreadPool


class Binance(object):
    @staticmethod
    def get_window(symbol, timeframe, limit):

        try:
            result = requests.get(
                "https://api.binance.com/api/v1/klines?symbol=" + symbol + "&interval=" + timeframe + "&limit=" + str(
                    limit))

            result = result.json()
            df = pd.DataFrame.from_records(data=result,
                                           columns=['time', 'O', 'H', 'L', 'C', 'vol', 'close_time', 'qa_volume',
                                                    'nb_trades', 'tba_valume', 'tqa_valume', 'ignore'])

            df['close'] = df['C'].astype(float)
            df['time'] = df['time'].astype(int)
            df['nb'] = df['nb_trades'].astype(int)
            df = df[['time', 'close', 'nb']]

            return df

        except Exception as e:
            print(e)
            time.sleep(1)
            return None

    @staticmethod
    def get_wide_window(symbol):
        limit = 1000
        timeframe = "1m"
        startTime = int(time.time() * 1000) - 2 * limit * 60 * 1000
        endTime = startTime + 500 * 60 * 1000
        try:

            args = [
                ("https://api3.binance.com/api/v1/klines?symbol=" + symbol + "&interval=" + timeframe + "&limit=" + str(
                    limit))]
            args += [(
                    "https://api3.binance.com/api/v1/klines?symbol=" + symbol + "&interval=" + timeframe + "&startTime=" + str(
                startTime) + "&endTime=" + str(endTime))]
            startTime += 500 * 60 * 1000
            endTime += 500 * 60 * 1000
            args += [(
                    "https://api3.binance.com/api/v1/klines?symbol=" + symbol + "&interval=" + timeframe + "&startTime=" + str(
                startTime) + "&endTime=" + str(endTime))]

            pool = ThreadPool(processes=2)
            results = pool.map(requests.get, args)
            pool.close()
            pool.join()
            df = pd.DataFrame.from_records(data=results[1].json(),
                                           columns=['time', 'O', 'H', 'L', 'C', 'vol', 'close_time', 'qa_volume',
                                                    'nb_trades', 'tba_valume', 'tqa_valume', 'ignore'])
            df = pd.DataFrame.from_records(data=results[2].json(),
                                           columns=['time', 'O', 'H', 'L', 'C', 'vol', 'close_time', 'qa_volume',
                                                    'nb_trades', 'tba_valume', 'tqa_valume', 'ignore'])

            df = df.append(pd.DataFrame.from_records(data=results[0].json(),
                                                     columns=['time', 'O', 'H', 'L', 'C', 'vol', 'close_time',
                                                              'qa_volume',
                                                              'nb_trades', 'tba_valume', 'tqa_valume', 'ignore']))

            df = df.reset_index().drop('index', axis=1)
            df['close'] = df['C'].astype(float)
            df['time'] = df['time'].astype(int)
            df['nb'] = df['nb_trades'].astype(int)
            df = df[['time', 'close', 'nb']]

            return df

        except Exception as e:
            print(e)
            time.sleep(1)
            return None

import time
from multiprocessing import Process
from threading import Thread

from logging_utils.generator import generate_logger
from src.algorithm import Algorithm
from src.static import AppContext
from src.exchangeconnector import ExchangeConnector
from src.static import *
from multiprocessing.pool import ThreadPool

from src.storage import Storage
import logging


class Invoker(Thread):
    def __init__(self, ctx: AppContext, exchange_connector: ExchangeConnector, storage: Storage, algo: Algorithm):
        Thread.__init__(self)
        self.last_invoke_time = datetime.datetime.now()
        self.ctx = ctx
        self.exchange_connector = exchange_connector
        self.storage = storage
        self.algorithm = algo

        self.logger = generate_logger('invoker')

        self._reduced_position = None

    def new_last_time(self, func):

        self.last_invoke_time = func(datetime.datetime.now())  # self.last_invoke_time

        self.logger.info('New time: {time}'.format(time=self.last_invoke_time))

    def _execute(self):
        self.logger.info('Invoker executing...\nTimestamp: {ts}'.format(ts=datetime.datetime.now().timestamp()))
        # loading storage from file
        self.storage.load()
        self.logger.debug('Storage loaded')

        # getting balance
        balance = self.exchange_connector.get_balance()
        self.ctx.info['current_balance'] = balance

        if balance is None:
            self.logger.critical('Fail to get balance: skipping iteration...')
            return

        self.logger.info('Balance got: {balance}'.format(balance=balance))

        # tickers to get market data
        tickers_to_get = list(list(zip(*self.exchange_connector.info))[0])
        # getting market data in ThreadPool
        results = self.exchange_connector.get_ticker_history_with_threadpool(tickers_to_get=tickers_to_get,
                                                                             timeframe=self.algorithm.timeframe,
                                                                             history_length=self.algorithm.history_length)
        self.logger.debug('Exchange data was updated')

        # injecting instances and variables to algorithm instance
        self.algorithm.define_amount(balance=balance)
        self.algorithm.load_data(data=dict(zip(tickers_to_get, results)))
        self.algorithm.load_storage(storage=self.storage)

        # analysing for close
        self.logger.debug('Analysing positions for close...')
        result_close = self.algorithm.analyse_close()
        ###
        ###DEBUGINFO
        # if len(result_close)>0:
        #     if len(list(filter(lambda x: x['action'] != Action.HOLD, result_close))) > 0:
        #         self.logger.debug('Tickers for close were analysed: {results}'.format(
        #             results=list(filter(lambda x: x['action'] != Action.HOLD, result_close))))
        ###DEBUGINFO
        ###
        self.logger.debug('Tickers for close were analysed')

        # analysing for open
        self.logger.debug('Analysing tickers for open...')
        results_open = self.algorithm.analyse_open()

        ###
        ###DEBUGINFO
        # if len(results_open) > 0:
        #     if len(list(filter(lambda x: x['action'] != Action.HOLD, results_open))) > 0:
        #         self.logger.debug('Tickers for open were analysed: {results}'.format(
        #             results=list(filter(lambda x: x['action'] != Action.HOLD, results_open))))
        ###DEBUGINFO
        ###
        if len(results_open) == 0:
            self.logger.debug('Tickers for open were analysed, no open actions')

        # dumping storage
        self.storage.dump()

    def run(self):
        self.logger.critical('Invoker started')
        while True:
            if self.ctx.app_exit:
                return

            try:
                if datetime.datetime.now() > self.last_invoke_time:
                    with self.storage.lock:
                        start_time = datetime.datetime.now()
                        self._execute()
                        execution_time = datetime.datetime.now() - start_time
                        self.ctx.info['invoker_latency'] = execution_time.total_seconds()
                    self.new_last_time(self.algorithm.new_last_time)
            except Exception as e:
                self.logger.critical('INVOKER IS DOWN!')
                self.ctx.invoker_fault = True
                raise e

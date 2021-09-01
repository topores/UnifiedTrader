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


class PositionReducer(Thread):
    def __init__(self, ctx: AppContext, exchange_connector: ExchangeConnector, storage_i: Storage, margin_rate_border):
        Thread.__init__(self)
        self.last_invoke_time = datetime.datetime.now()
        self.ctx = ctx
        self.exchange_connector = exchange_connector
        self.storage_i = storage_i
        self.margin_rate_border = margin_rate_border

        self.logger = generate_logger('position_reducer')

    def new_last_time(self, func):

        self.last_invoke_time = func(datetime.datetime.now())
        self.logger.debug('New time for position reducer: {time}'.format(time=self.last_invoke_time))

    def _execute(self):
        balance_info = self.exchange_connector.get_balance_info()
        try:
            margin_rate = balance_info['free'] / balance_info['total']
            self.ctx.info['margin_rate'] = margin_rate
        except Exception as e:
            self.logger.critical(f'error calculating margin rate for position reducer')
            return

        if margin_rate < self.margin_rate_border:
            poses = self.storage_i.get_positions_by_state(state=State.OPENED)
            poses_sorted = sorted(poses,
                                  key=lambda x: x.timestamp)
            if len(poses_sorted) == 0:
                self.logger.debug(f'margin_rate is low ({self.margin_rate_border}), but no positions found to delete')
                return
            position = self.storage_i.data[self.storage_i.find_position_idx(poses_sorted[0])]
            self.storage_i.update_position_state_by_order_id(order_id=position.order_id, state=State.READY_TO_CLOSE)
            self.logger.critical(
                f'The oldest position was closed (state chaged to READY_TO_CLOSE) due to low margin (margin_rate={self.margin_rate_border}):\n{position}')

    def run(self):
        self.logger.critical('Position reducer started')
        while True:
            if self.ctx.app_exit:
                return

            try:
                if datetime.datetime.now() > self.last_invoke_time:
                    with self.storage_i.lock:
                        start_time = datetime.datetime.now()
                        self._execute()
                        execution_time = datetime.datetime.now() - start_time
                        self.ctx.info['position_reducer_latency'] = execution_time.total_seconds()
                    self.new_last_time(lambda x: x + datetime.timedelta(minutes=1))
            except Exception as e:
                self.logger.critical('POSITION REDUCER IS DOWN!')
                self.ctx.position_reducer_fault = True
                raise e

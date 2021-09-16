import json
import logging
from multiprocessing import Process
from threading import Thread

from logging_utils.generator import generate_logger, generate_writer_logger
from src.exchangeconnector import ExchangeConnector
from src.storage import Storage
from src.static import *

import time


class Executor(Thread):
    def __init__(self, ctx: AppContext):
        Thread.__init__(self)
        self.ctx = ctx
        self.exchange_connector = self.ctx.exchange_connector
        self.storage = self.ctx.storage
        self.logger = generate_logger('executor')
        self.writer_logger = generate_writer_logger('executor-writer')

    def __remove_positions(self):

        for pos in self.storage.get_positions_by_state(state=State.READY_TO_OPEN)[:]:
            if pos.amount < self.exchange_connector.min_sizes[pos.ticker]:
                self.storage.data.remove(pos)
                self.logger.critical('Position was removed due to the low amount:\n {pos}'.format(pos=pos))
                self.writer_logger.critical(json.dumps({'result': 'removed_low_amount', 'position:': pos.__dict__}))

                self.storage.dump()

        for pos in self.storage.get_positions_by_state(state=State.CLOSED)[:]:
            self.storage.data.remove(pos)
            self.logger.warning('Position(state=CLOSED) successfully removed:\n {pos}'.format(pos=pos))
            self.writer_logger.critical(json.dumps({'result': 'removed_closed', 'position:': pos.__dict__}))

            self.storage.dump()

    def __open_position(self, pos: Position):
        self.logger.debug('found position to OPEN:\n {pos}'.format(pos=pos))

        #длинный список параметров
        result = self.exchange_connector.place_order(pos)

        if result is not None:

            pos.amount = result['amount']
            pos.order_id = result['order_id']
            pos.timestamp = result['timestamp']
            pos.state = State.OPENED
            self.logger.warning('Position successfully opened:\n {pos}'.format(pos=pos))
            self.writer_logger.critical(json.dumps({'result': 'opened', 'position:': pos.__dict__}))
        else:

            self.logger.critical('Position was not opened!:\n {pos}'.format(pos=pos))
            self.writer_logger.critical(json.dumps({'result': 'not_opened', 'position:': pos.__dict__}))

        self.storage.dump()

    def __close_position(self, pos: Position):
        self.logger.debug('found position to CLOSE:\n {pos}'.format(pos=pos))
        result = self.exchange_connector.place_order(pos,invert_side=True)

        if result is not None:
            pos.state = State.CLOSED
            self.logger.warning(
                'Position successfully closed (state changed to CLOSED:\n {pos}'.format(pos=pos))
            self.writer_logger.critical(json.dumps({'result': 'closed', 'position:': pos.__dict__}))
        else:
            self.logger.critical('Position was not closed!:\n {pos}'.format(pos=pos))
            self.writer_logger.critical(json.dumps({'result': 'not_closed', 'position:': pos.__dict__}))
        self.storage.dump()

    def __execute_positions(self):
        for pos in self.storage.data:

            if pos.state == State.READY_TO_OPEN:
                self.__open_position(pos)

            if pos.state == State.READY_TO_CLOSE:
                self.__close_position(pos)

    # Длинный метод
    def _execute(self):

        # removing positions with low size / state==close
        self.__remove_positions()

        # executing positions
        self.__remove_positions()

    def execute(self):
        return self._execute()

    def run(self):
        self.logger.critical('Executor started')
        while True:
            if self.ctx.app_exit:
                return

            time.sleep(0.1)

            try:
                with self.storage.lock:
                    start_time = datetime.datetime.now()
                    self._execute()
                    execution_time = datetime.datetime.now() - start_time
                    self.ctx.info['executor_latency'] = execution_time.total_seconds()
            except Exception as e:
                self.logger.critical('EXECUTOR IS DOWN!')
                self.ctx.executor_fault = True
                raise e

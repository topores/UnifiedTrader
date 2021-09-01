import datetime
from collections import deque
import multiprocessing

from logging_utils.generator import generate_logger
from processes.position_reducer import PositionReducer
from processes.invoker import Invoker
from processes.executor import Executor

from src.algorithm import Algorithm
from src.exchangeconnector import ExchangeConnector
from src.storage import Storage
import time
import logging
import json
from src.static import AppContext


class App():

    def __init__(self):

        self.storage = Storage()
        self.exchangeconnector = ExchangeConnector(test=True)
        self.algorithm = Algorithm(test=True)

        self.ctx = AppContext()

        self.executor = Executor(ctx=self.ctx,
                                 exchange_connector=self.exchangeconnector,
                                 storage=self.storage)
        self.invoker = Invoker(ctx=self.ctx,
                               exchange_connector=self.exchangeconnector,
                               storage=self.storage,
                               algo=self.algorithm)
        self.position_reducer = PositionReducer(self.ctx,
                                                self.exchangeconnector,
                                                self.storage,
                                                margin_rate_border=0.12)


        self.logger = generate_logger('app')

        pass

    def _dump_for_monitor(self):
        f = open('state.json', 'w')
        json.dump({
            'timestamp': datetime.datetime.now().timestamp(),
            'app_context': self.ctx.__dict__
        },
            fp=f,
            indent=4)
        f.close()

        self.storage.json_dump(filename='storage.json')

    def run(self):
        self.logger.critical('App started')

        self.invoker.start()
        self.executor.start()
        self.position_reducer.start()

        while True:

            try:
                time.sleep(1)
                if self.ctx.invoker_fault:
                    raise RuntimeError('Error occurred in invoker instance')

                if self.ctx.executor_fault:
                    raise RuntimeError('Error occurred in executor instance')

                if self.ctx.position_reducer_fault:
                    raise RuntimeError('Error occurred in position_reducer instance')

                self._dump_for_monitor()

            except RuntimeError as e:
                self.ctx.app_exit = True
                self.logger.critical('Error occurred in threads: {e}'.format(e=str(e)))
                self._dump_for_monitor()
                raise e
            except Exception as e:
                self.ctx.app_exit = True
                self.logger.critical('Error occurred: {e}'.format(e=str(e)))
                self._dump_for_monitor()
                raise e
            except KeyboardInterrupt as e:
                self.ctx.app_exit = True
                self.logger.critical('Keyboard Interrupt')

                self._dump_for_monitor()
                raise e

import inspect
import json
import logging
import os

import datetime
from threading import RLock
from typing import List

from logging_utils.generator import generate_logger, generate_writer_logger
from src.static import Position, State
import pickle


class Storage():
    def __init__(self, data: List[Position] = None):
        if data is None:
            data = []
        self.data = data
        pass
        self.writing = False

        self.logger = generate_logger('storage')
        self.open_positions_writer_logger = generate_writer_logger('storage-writer.open_positions')
        self.update_positions_writer_logger = generate_writer_logger('storage-writer.update_positions')
        self.lock = RLock()

    def _add_position(self, position: Position):
        self.data.append(position)

    def find_position_idx(self, order_id):
        idx = -1
        for i in range(0, len(self.data)):
            if self.data[i].order_id == order_id:
                idx = i
        return idx

    def update_position_state_by_order_id(self, order_id, state):
        idx = self.find_position_idx(order_id)
        if idx < 0:
            raise RuntimeWarning('Could not found while update_timestamp_for_position_by_order_id()')
        position = self.data[idx]
        position.state = state
        self.dump()

        try:
            stack = inspect.stack()
            the_class = stack[1][0].f_locals["self"].__class__.__name__
            the_method = stack[1][0].f_code.co_name
            caller_info = f'{the_class}.{the_method}'
        except:
            caller_info = 'error geting caller_info'
        self.logger.warning('Position state was updated to state={state}:\n {pos}\n Called by {caller_info}'.format(
            state=state, pos=position, caller_info=caller_info))

        self.update_positions_writer_logger.critical(json.dumps(position.__dict__))

    def update_position_timestamp_by_order_id(self, order_id, timestamp):
        idx = self.find_position_idx(order_id)
        if idx < 0:
            raise RuntimeWarning('Could not found while update_timestamp_for_position_by_order_id()')
        position = self.data[idx]
        position.timestamp = timestamp
        self.dump()
        self.logger.warning('Position was continued - timestamp updated to now({now}):\n {pos}'.format(
            now=datetime.datetime.now().timestamp(), pos=position))

        self.update_positions_writer_logger.critical(json.dumps(position.__dict__))

    def remove_position_by_order_id(self, order_id):
        idx = self.find_position_idx(order_id=order_id)
        if idx >= 0:
            self.data.pop(idx)
        else:
            pass


    def add_position(self, ticker, action, amount, state=State.READY_TO_OPEN, info=None):
        pos = Position(ticker=ticker,
                       side=action,
                       amount=amount,
                       state=state,
                       info=info)
        self._add_position(pos)
        self.dump()
        self.logger.info('Position was added to storage with state=READY_TO_OPEN:\n {pos}'.format(pos=pos))
        self.open_positions_writer_logger.critical(json.dumps(pos.__dict__))

    def get_positions_by_state(self, state: int) -> List[Position]:
        if len(self.data) > 0:
            return list(filter(lambda el: el.state == state, self.data))
        else:
            return []

    def dump(self, filename='storage.pickle'):
        filename_ = f'{os.path.dirname(__file__)}/../service_files/{filename}'
        while self.writing:
            pass

        self.writing = True
        try:
            f = open(filename_, 'wb')
            pickle.dump(self.data, f)
            f.close()
            self.logger.debug('Storage dumped')
        except Exception as e:
            self.logger.critical(f'Error dumping: ({str(e)}')
            raise e
        self.writing = False

    def json_dump(self, filename='storage.json'):

        try:
            f = open(filename, 'w')
            json_data = []
            for position in self.data:
                json_data.append(position.__dict__)

            json.dump(json_data, f, indent=4, sort_keys=True)
            f.close()

            f = open('../storage_backup.list', 'w')
            f.write(str(self.data))
            f.close()
        except Exception as e:

            raise e

    def load(self, filename='storage.pickle'):
        filename_ = f'{os.path.dirname(__file__)}/../service_files/{filename}'
        while self.writing:
            pass
        self.logger.debug('loading...')
        try:
            f = open(filename_, 'rb')
            data = pickle.load(f)
            self.trade_data.data = data
            f.close()
            print('Storage loaded')
            self.logger.info('storage loaded')
        except Exception as e:
            self.logger.error('Error reading pickle: dumping and then reading...')
            self.dump(filename)
            f = open(filename_, 'rb')
            data = pickle.load(f)
            self.trade_data.data = data
            f.close()

import datetime


class AppContext():
    def __init__(self):
        self.invoker_fault = False
        self.executor_fault = False
        self.position_reducer_fault = False
        self.logger_fault = False

        self.app_exit = False
        self.info = {}



class Action():
    CLOSE = -1
    HOLD = 0
    LONG = 1
    SHORT = 2

    @staticmethod
    def represent(action):
        return {-1: "CLOSE",
                0: "HOLD",
                1: "LONG",
                2: "SHORT"
                }[action]

    @staticmethod
    def invert(action):
        if action == 1:
            return 2
        elif action == 2:
            return 1
        else:
            raise Exception('invalid invert function action')


class State():
    READY_TO_OPEN = 3
    OPENED = 2
    READY_TO_CLOSE = 1
    CLOSED = 0

    @staticmethod
    def represent(action):
        return {3: "READY_TO_OPEN",
                2: "OPENED",
                1: "READY_TO_CLOSE",
                0: "CLOSED"
                }[action]


class Position():
    def __init__(self, ticker: str, side: int, amount: float, state: int, timestamp: float = None, order_id: int = None,
                 info: dict = None):
        self.ticker = ticker
        self.side = side
        self.amount = amount
        self.state = state
        self.timestamp = timestamp
        self.order_id = order_id
        self.info = info

    def __str__(self) -> str:
        # return '\nPosition<\nticker={ticker},\nside={side},\namount={amount},\nstate={state},\norder_id={order_id},\ntimestamp={timestamp}\n>'.format(
        #     ticker=self.ticker,
        #     side=self.side,
        #     amount=self.amount,
        #     state=self.state,
        #     timestamp=self.timestamp,
        #     order_id=self.order_id
        # )
        return f'Position<ticker={self.ticker}, (si/a/st/oid/ts)=({self.side}/{self.amount}/{self.state}/{self.order_id}/{self.timestamp})>'

    def __repr__(self) -> str:
        return self.__str__()


class Util():
    @staticmethod
    def represent_dict(d, level=''):
        s = ''  # level[:]
        for el in d:
            if type(d[el]) == list:
                s += '{level}{key}:\n{val}\n'.format(level=level, key=el,
                                                     val=Util.represent_list(d[el], level=level + '+++')) + '\n'
            elif type(d[el]) == dict:
                s += '{level}{key}:\n{val}\n'.format(level=level, key=el,
                                                     val=Util.represent_dict(d[el], level=level + '+++')) + '\n'
            else:
                s += '{level}{key}: {val}\n'.format(level=level, key=el, val=d[el])

        s = s[:len(s) - 1]
        return s

    @staticmethod
    def represent_list(d, level=''):
        s = ''
        for el in d:
            if type(el) == list:
                s += '{val}\n'.format(level=level, val=Util.represent_list(el, level=level + '+++')) + '\n'
            elif type(el) == dict:
                s += '{val}\n'.format(level=level, val=Util.represent_dict(el, level=level + '|')) + '\n'
            else:

                s += '{level}|{val}\n'.format(level=level, val=el)
        s = s[:len(s) - 1]
        return s
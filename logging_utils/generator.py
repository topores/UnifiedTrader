import logging
import logging.handlers
import os


# from logging_utils.telegramhandler import TelegramLoggerHandler


def generate_logger(name='root'):
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(logging.Formatter("[%(name)s] %(asctime)s - %(levelname)s:\n%(message)s\n"))
    streamHandler.setLevel(logging.DEBUG)

    trfHandler = logging.handlers.TimedRotatingFileHandler(f'{os.path.dirname(__file__)}/../logs/debug_{name}.log',
                                                           when='D', interval=1, backupCount=5)
    trfHandler.setFormatter(logging.Formatter("[%(name)s] %(asctime)s - %(levelname)s:\n%(message)s\n"))
    trfHandler.setLevel(logging.DEBUG)

    logger.addHandler(streamHandler)
    # logger.addHandler(TelegramLoggerHandler())
    logger.addHandler(trfHandler)
    if len(logger.handlers) > 3:
        raise Exception('logger.handlers length exception')

    print('{name} logger setted up'.format(name=name))

    return logger


def generate_writer_logger(name='root'):
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    trfHandler = logging.handlers.TimedRotatingFileHandler(f'{os.path.dirname(__file__)}/../logs/debug_{name}.log',
                                                           when='D', interval=60, backupCount=5)
    trfHandler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    trfHandler.setLevel(logging.DEBUG)

    logger.addHandler(trfHandler)
    # logger.propagate
    # raise Exception('writer logger exception')

    print('{name} logger setted up'.format(name=name))

    # logger.info('Logger setted up'.format(name=name))
    return logger

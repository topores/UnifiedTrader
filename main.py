# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, service_files, tool windows, actions, and settings.
import logging
import resource

from processes.invoker import *
from src.app import App
import logging

def set_logger_config():
    pass
    # for v in logging.Logger.manager.loggerDict.values():
    #     if type(v) == type(logging.Logger('123')):
    #         #print(v.name)
    #         v.disabled = True

        # if v.name!='root':
        #     v.disabled = True

    # fileHandler = logging.FileHandler("telegram.log")
    # fileHandler.setFormatter(logging.Formatter("[%(levelname)s][%(name)s] %(asctime)s : %(message)s"))
    # fileHandler.setLevel(logging.WARNING)

    # logging.basicConfig(handlers=[
    #                         streamHandler,
    #                         TelegramLoggerHandler()
    #                     ])


def main(name):



    set_logger_config()
    App().run()


def limit_memory():
    rss_maxsize=5*1024*1024
    vmem_maxsize = 5 * 1024# * 1024

    soft, hard = resource.getrlimit(resource.RLIMIT_RSS)

    resource.setrlimit(resource.RLIMIT_RSS,(vmem_maxsize,hard))
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    limit_memory()
    main('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

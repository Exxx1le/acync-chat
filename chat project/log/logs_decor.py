import functools
import datetime
import sys
import traceback
import inspect
from log.config import client_logger, server_logger
import socket

if sys.argv[0].find("client") == -1:
    logger = server_logger.logger
else:
    logger = client_logger.logger


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(
            f"Была вызвана функция {func.__name__} c параметрами {args}, {kwargs} в {timestamp} "
            f"Вызов из модуля {func.__module__}. Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}."
            f"Вызов из функции {inspect.stack()[1][3]}"
        )
        return func(*args, **kwargs)

    return wrapper


def login_required(func):
    def checker(*args, **kwargs):
        from server.core import MessageProcessor
        from variables import ACTION, PRESENCE

        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker

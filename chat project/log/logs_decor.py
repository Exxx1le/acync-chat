import logging
import functools
import datetime

logger = logging.getLogger("client_logger")


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Вызвана функция {func.__name__}")

        logger.info(
            f"Функция {func.__name__} была вызвана c параметрами {args}, {kwargs}."
            f"Вызов из модуля {func.__module__} {timestamp}"
        )
        return func

    return wrapper

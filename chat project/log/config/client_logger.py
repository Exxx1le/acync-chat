import logging
import logging.handlers
import sys
from pathlib import Path

client_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(filename)s %(message)s"
)

path = f"{Path(__file__).parents[1]}/logs/client.log"

stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(client_formatter)
stream_handler.setLevel(logging.ERROR)
log_file = logging.FileHandler(path, encoding="utf8")
log_file.setFormatter(client_formatter)

logger = logging.getLogger("client_logger")
logger.addHandler(stream_handler)
logger.addHandler(log_file)
logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    logger.critical("Критическая ошибка")
    logger.error("Ошибка")
    logger.info("Информация")
    logger.debug("Отладка")

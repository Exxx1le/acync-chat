import logging
import logging.handlers
import sys
from pathlib import Path

server_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')
    
path = f'{Path(__file__).parents[1]}/logs/server.log'

stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(server_formatter)
stream_handler.setLevel(logging.ERROR)
log_file = logging.handlers.TimedRotatingFileHandler(path, encoding='utf8', interval=1, when='midnight')
log_file.setFormatter(server_formatter)

logger = logging.getLogger('server_logger')
logger.addHandler(stream_handler)
logger.addHandler(log_file)
logger.setLevel(logging.DEBUG)
    

if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.info('Информация')
    logger.debug('Отладка')

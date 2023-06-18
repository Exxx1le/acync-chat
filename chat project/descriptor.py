from log.config import server_logger


logger = server_logger.logger


class PortChecker:
    def __set__(self, instance, port_number):
        if not 1023 < port_number < 65536:
            logger.critical(
                f"Неправильный порт запуска сервера {port_number}. Допустимы адреса с 1024 до 65535."
            )
            exit(1)
        instance.__dict__[self.name] = port_number

    def __set_name__(self, owner, name):
        self.name = name

from socket import socket, AF_INET, SOCK_STREAM
from log.config import client_logger
from log.logs_decor import log

logger = client_logger.logger


@log
def send_message():
    with socket(AF_INET, SOCK_STREAM) as sock:
        server_address = ("localhost", 7777)
        sock.connect(server_address)
        while True:
            message = input("Введите сообщение: ")
            try:
                sock.send(message.encode("utf-8"))
                data = sock.recv(4096).decode("utf-8")
                print(data)
                logger.debug(f"На сервер отправлено сообщение {message}")
                logger.debug(f"Получено сообщение {data}")
            except ConnectionRefusedError as e:
                logger.critical(f"В соединении отказано {e}")
            except Exception as e:
                logger.exception("Возникло исключение при отправке сообщения {e}")


if __name__ == "__main__":
    send_message()

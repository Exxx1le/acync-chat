import socket
from log.config import client_logger
from log.logs_decor import log

logger = client_logger.logger


# @log
# def create_presence_message():
#     message = {
#         "action": "presence",
#         "type": "status",
#         "user": {"account_name": "my_username", "status": "Online"},
#     }
#     return message


# @log
# def send_message(server_address, server_port, message):
#     try:
#         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         client_socket.connect((server_address, server_port))
#         client_socket.send(json.dumps(message).encode())
#         logger.info(f"Отправлено сообщение: {message}")
#         response = client_socket.recv(1024).decode()
#         client_socket.close()
#     except ConnectionRefusedError as e:
#         logger.error("В соединеннии отказано", e)
#     except Exception as e:
#         logger.exception("Исключение: %s", str(e))


# if __name__ == "__main__":
#     server_address = sys.argv[1]
#     server_port = int(sys.argv[2]) if len(sys.argv) > 2 else 7777

#     presence_message = create_presence_message()
#     send_message(server_address, server_port, presence_message)


@log
def send_message(message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("localhost", 7777)
    try:
        client_socket.connect(server_address)
    except ConnectionRefusedError as e:
        logger.critical(f"В соединении отказано {e}")

    # Отправка сообщения серверу
    client_socket.sendall(message.encode())

    client_socket.close()


if __name__ == "__main__":
    while True:
        message = input("Enter message: ")
        try:
            send_message(message)
            logger.debug(f"На сервер отправлено сообщение {message}")
        except Exception as e:
            logger.exception("Возникло исключение при отправке сообщения {e}")

import sys
import socket
import json
from log.config import client_logger
from log.logs_decor import log

logger = client_logger.logger


@log
def create_presence_message():
    message = {
        "action": "presence",
        "type": "status",
        "user": {"account_name": "my_username", "status": "Online"},
    }
    return message


@log
def send_message(server_address, server_port, message):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        client_socket.send(json.dumps(message).encode())
        logger.info(f"Отправлено сообщение: {message}")
        response = client_socket.recv(1024).decode()
        # print("Ответ сервера:", response)
        logger.info("Ответ сервера:", response)
        client_socket.close()
    except ConnectionRefusedError as e:
        logger.error("В соединеннии отказано", e)
    except Exception as e:
        logger.exception("Исключение: %s", str(e))


if __name__ == "__main__":
    server_address = sys.argv[1]
    server_port = int(sys.argv[2]) if len(sys.argv) > 2 else 7777

    presence_message = create_presence_message()
    send_message(server_address, server_port, presence_message)

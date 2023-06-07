import socket
import select
from log.config import server_logger
from log.logs_decor import log

logger = server_logger.logger

# def handle_client(client_socket):
#     request = client_socket.recv(1024).decode()
#     # print("Полученное сообщение:", request)
#     logger.debug(f"Получено сообщение: {request}")

#     response = {"response": 200, "alert": "OK"}

#     client_socket.send(json.dumps(response).encode())
#     client_socket.close()


# def start_server(server_address, server_port):
#     try:
#         server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         server_socket.bind((server_address, server_port))
#         server_socket.listen(5)
#         # print(f"Сервер стартовал на {server_address}:{server_port}")
#         logger.info(f"Сервер стартовал на {server_address}:{server_port}")

#         while True:
#             client_socket, client_address = server_socket.accept()
#             # print("Клиент подключен:", client_address)
#             logger.info(f"Клиент подключен: {client_address}")
#             handle_client(client_socket)

#     except OSError as e:
#         # print("Ошибка сервера:", e)
#         logger.critical("Ошибка сервера", e)
#     except Exception as e:
#         logger.exception("Исключение: %s", str(e))
#     finally:
#         server_socket.close()


# if __name__ == "__main__":
#     server_port = 7777
#     server_address = "0.0.0.0"

#     start_server(server_address, server_port)


@log
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ("localhost", 7777)

    try:
        server_socket.bind(server_address)
        logger.info(f"Сервер запущен на {str(server_address)}")
        server_socket.listen(5)
    except OSError as e:
        logger.critical("Ошибка сервера", e)

    client_sockets = []

    while True:
        readable, _, _ = select.select([server_socket] + client_sockets, [], [])

        for sock in readable:
            if sock is server_socket:
                client_socket, client_address = server_socket.accept()
                client_sockets.append(client_socket)
                logger.info(f"Новое соединение с {client_address}")

            else:
                # Получаем данные от клиента
                data = sock.recv(1024)
                if data:
                    # Отправляем данные всем клиентам, кроме отправителя
                    for client in client_sockets:
                        if client != sock:
                            client.send(data)
                            logger.info(f"Отправлено сообщение {data}")
                else:
                    client_sockets.remove(sock)
                    sock.close()


if __name__ == "__main__":
    start_server()

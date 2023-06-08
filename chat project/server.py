from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from select import select

from log.config import server_logger
from log.logs_decor import log

logger = server_logger.logger


@log
def read_requests(read_clients, all_clients) -> list:
    recieved_messages = []

    for sock in read_clients:
        try:
            data = sock.recv(1024).decode("utf-8")
            recieved_messages.append(data)
        except Exception:
            logger.info(f"Клиент {sock.fileno()} {sock.getpeername()} отключился")
            all_clients.remove(sock)

    return recieved_messages


@log
def write_responses(messages_list, write_clients, all_clients):
    for sock in write_clients:
        try:
            # response = requests.get(sock)
            message = messages_list[-1]
            sock.send(message.encode("utf-8"))
        except Exception:
            logger.info(f"Клиент {sock.fileno()} {sock.getpeername()} отключился")
            sock.close()
            all_clients.remove(sock)


@log
def start_server():
    with socket(AF_INET, SOCK_STREAM) as server_cock:
        server_cock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_address = ("localhost", 7777)
        server_cock.bind(server_address)
        server_cock.listen(5)
        server_cock.settimeout(1)
        client_sockets = []

        while True:
            try:
                client_sock, address = server_cock.accept()
            except OSError as e:
                # logger.critical(f"Ошибка сервера {e}")
                pass
            else:
                client_sockets.append(client_sock)
                logger.info(f"Получен запрос на соединение от {str(address)}")
            finally:
                cl_read = []
                cl_write = []
                cl_read, cl_write, _ = select(client_sockets, client_sockets, [], 0)
                # if sock in cl_read:
                #     recieved_data = sock.recv(4096)
                #     data = recieved_data.decode("utf-8")
                #     logger.info(f"Получено сообщение {data}")
                #     sock.send(data.encode("utf-8"))
                requests = read_requests(cl_read, client_sockets)
                if requests:
                    write_responses(requests, cl_write, client_sockets)


if __name__ == "__main__":
    start_server()

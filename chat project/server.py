from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from select import select

from log.config import server_logger
from log.logs_decor import log

logger = server_logger.logger


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
                pass
            else:
                client_sockets.append(client_sock)
            finally:
                for sock in client_sockets:
                    cl_read = []
                    cl_write = []
                    cl_read, cl_write, _ = select(client_sockets, client_sockets, [], 0)
                    if sock in cl_read:
                        recieved_data = sock.recv(4096)
                        data = recieved_data.decode("utf-8")
                        logger.info(f"Получено сообщение {data}")
                        sock.send(data.encode("utf-8"))


if __name__ == "__main__":
    start_server()

import sys
import socket
import json
from log.config import server_logger

logger = server_logger.logger

def handle_client(client_socket):
    request = client_socket.recv(1024).decode()
    # print("Полученное сообщение:", request)
    logger.debug(f'Получено сообщение: {request}')
    
    response = {
        "response": 200,
        "alert": "OK"
    }
    
    client_socket.send(json.dumps(response).encode())
    client_socket.close()

def start_server(server_address, server_port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((server_address, server_port))
        server_socket.listen(1)
        # print(f"Сервер стартовал на {server_address}:{server_port}")
        logger.info(f"Сервер стартовал на {server_address}:{server_port}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            # print("Клиент подключен:", client_address)
            logger.info(f"Клиент подключен: {client_address}")
            handle_client(client_socket)
            
    except OSError as e:
        # print("Ошибка сервера:", e)
        logger.critical("Ошибка сервера", e)
    except Exception as e:
        logger.exception('Исключение: %s', str(e))
    finally:
        server_socket.close()

if __name__ == "__main__":
    server_port = 7777
    server_address = "0.0.0.0"
    
    if "-p" in sys.argv:
        port_index = sys.argv.index("-p") + 1
        server_port = int(sys.argv[port_index])
    
    if "-a" in sys.argv:
        addr_index = sys.argv.index("-a") + 1
        server_address = sys.argv[addr_index]
    
    start_server(server_address, server_port)

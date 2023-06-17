import sys
import socket
import argparse
import select
import json

from variables import (
    ACTION,
    TIME,
    USER,
    ACCOUNT_NAME,
    SENDER,
    PRESENCE,
    ERROR,
    MESSAGE,
    MESSAGE_TEXT,
    RESPONSE_400,
    DESTINATION,
    RESPONSE_200,
    EXIT,
)
from log.config import server_logger
from log.logs_decor import log
from metaclasses import ServerVerifier

logger = server_logger.logger


@log
def get_message(client):
    encoded_response = client.recv(1024)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode("utf-8")
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response


@log
def send_message(sock, message):
    js_message = json.dumps(message)
    encoded_message = js_message.encode("utf-8")
    sock.send(encoded_message)


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", default=7777, type=int, nargs="?")
    parser.add_argument("-a", default="", nargs="?")
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        logger.critical(
            f"Попытка запуска сервера с указанием неподходящего порта {listen_port}. "
            f"Допустимы адреса с 1024 до 65535."
        )
        sys.exit(1)

    return listen_address, listen_port


class Server(metaclass=ServerVerifier):
    def __init__(self, listen_address, listen_port):
        self.addr = listen_address
        self.port = listen_port

        self.clients = []
        self.messages = []
        self.names = dict()

    def init_socket(self):
        logger.info(
            f"Запущен сервер, порт для подключений: {self.port} ,"
            f"адрес с которого принимаются подключения: {self.addr}."
        )
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen()

    def run_server(self):
        self.init_socket()
        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f"Установлено соедение с ПК {client_address}")
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, _ = select.select(
                        self.clients, self.clients, [], 0
                    )
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(
                            get_message(client_with_message), client_with_message
                        )
                    except:
                        logger.info(
                            f"Клиент {client_with_message.getpeername()} отключился от сервера."
                        )
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except:
                    logger.info(f"Связь с клиентом {message[DESTINATION]} потеряна")
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    def process_message(self, message, listen_socks):
        if (
            message[DESTINATION] in self.names
            and self.names[message[DESTINATION]] in listen_socks
        ):
            send_message(self.names[message[DESTINATION]], message)
            logger.info(
                f"Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}."
            )
        elif (
            message[DESTINATION] in self.names
            and self.names[message[DESTINATION]] not in listen_socks
        ):
            raise ConnectionError
        else:
            logger.error(
                f"Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна."
            )

    def process_client_message(self, message, client):
        logger.debug(f"Разбор сообщения от клиента : {message}")
        if (
            ACTION in message
            and message[ACTION] == PRESENCE
            and TIME in message
            and USER in message
        ):
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = "Имя пользователя уже занято."
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif (
            ACTION in message
            and message[ACTION] == MESSAGE
            and DESTINATION in message
            and TIME in message
            and SENDER in message
            and MESSAGE_TEXT in message
        ):
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = "Запрос некорректен."
            send_message(client, response)
            return


def main():
    listen_address, listen_port = arg_parser()
    server = Server(listen_address, listen_port)
    server.run_server()


if __name__ == "__main__":
    main()

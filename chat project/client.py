import sys
import json
import socket
import time
import argparse
import threading

from variables import (
    ACTION,
    EXIT,
    TIME,
    ACCOUNT_NAME,
    MESSAGE,
    SENDER,
    DESTINATION,
    MESSAGE_TEXT,
    PRESENCE,
    USER,
    RESPONSE,
)
from log.config import client_logger
from log.logs_decor import log
from metaclasses import ClientVerifier

logger = client_logger.logger


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


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def create_exit_message(self):
        return {ACTION: EXIT, TIME: time.time(), ACCOUNT_NAME: self.account_name}

    def create_message(self):
        to = input("Введите получателя сообщения: ")
        message = input("Введите сообщение для отправки: ")
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message,
        }
        logger.debug(f"Сформирован словарь сообщения: {message_dict}")
        try:
            send_message(self.sock, message_dict)
            logger.info(f"Отправлено сообщение для пользователя {to}")
        except:
            logger.critical("Потеряно соединение с сервером.")
            exit(1)

    def run(self):
        self.print_help()
        while True:
            command = input("Введите команду: ")
            if command == "message":
                self.create_message()
            elif command == "help":
                self.print_help()
            elif command == "exit":
                try:
                    send_message(self.sock, self.create_exit_message())
                except:
                    pass
                print("Завершение соединения.")
                logger.info("Завершение работы по команде пользователя.")
                time.sleep(0.5)
                break
            else:
                print(
                    "Команда не распознана, попробойте снова. help - вывести поддерживаемые команды."
                )

    def print_help(self):
        print("Поддерживаемые команды:")
        print("message - отправить сообщение. Кому и текст будет запрошены отдельно.")
        print("help - вывести подсказки по командам")
        print("exit - выход из программы")


class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if (
                    ACTION in message
                    and message[ACTION] == MESSAGE
                    and SENDER in message
                    and DESTINATION in message
                    and MESSAGE_TEXT in message
                    and message[DESTINATION] == self.account_name
                ):
                    print(
                        f"Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}"
                    )
                    logger.info(
                        f"Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}"
                    )
                else:
                    logger.error(
                        f"Получено некорректное сообщение с сервера: {message}"
                    )
            except (
                OSError,
                ConnectionError,
                ConnectionAbortedError,
                ConnectionResetError,
                json.JSONDecodeError,
            ):
                print("Потеряно соединение с сервером")
                logger.critical(f"Потеряно соединение с сервером.")
                break


@log
def create_presence(account_name):
    out = {ACTION: PRESENCE, TIME: time.time(), USER: {ACCOUNT_NAME: account_name}}
    logger.debug(f"Сформировано {PRESENCE} сообщение для пользователя {account_name}")
    return out


@log
def process_response_ans(message):
    logger.debug(f"Разбор приветственного сообщения от сервера: {message}")
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return "200 : OK"
        elif message[RESPONSE] == 400:
            logger.critical(f"Ошибка соединения с сервером")
            sys.exit(1)


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("addr", default="127.0.0.1", nargs="?")
    parser.add_argument("port", default=7777, type=int, nargs="?")
    parser.add_argument("-n", "--name", default=None, nargs="?")
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        logger.critical(
            f"Попытка запуска клиента с неподходящим номером порта: {server_port}. Допустимы адреса с 1024 до 65535."
        )
        sys.exit(1)

    return server_address, server_port, client_name


def main():
    print("Консольный месседжер. Клиентский модуль.")

    server_address, server_port, client_name = arg_parser()

    if not client_name:
        client_name = input("Введите имя пользователя: ")
    else:
        print(f"Клиентский модуль запущен с именем: {client_name}")

    logger.info(
        f"Запущен клиент с парамертами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}"
    )

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_response_ans(get_message(transport))
        logger.info(f"Установлено соединение с сервером. Ответ сервера: {answer}")
        print(f"Установлено соединение с сервером.")
    except json.JSONDecodeError:
        logger.error("Не удалось декодировать полученную Json строку.")
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(
            f"Не удалось подключиться к серверу {server_address}:{server_port}."
        )
        exit(1)
    else:
        module_reciver = ClientReader(client_name, transport)
        module_reciver.daemon = True
        module_reciver.start()
        module_sender = ClientSender(client_name, transport)
        module_sender.daemon = True
        module_sender.start()
        logger.debug("Запущены процессы")

        while True:
            time.sleep(1)
            if module_reciver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == "__main__":
    main()

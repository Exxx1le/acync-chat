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
def process_client_message(message, messages_list, client, clients, names):
    logger.debug(f"Разбор сообщения от клиента : {message}")
    if (
        ACTION in message
        and message[ACTION] == PRESENCE
        and TIME in message
        and USER in message
    ):
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = "Имя пользователя уже занято."
            send_message(client, response)
            clients.remove(client)
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
        messages_list.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        response = RESPONSE_400
        response[ERROR] = "Запрос некорректен."
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        logger.info(
            f"Отправлено сообщение пользователю {message[DESTINATION]} "
            f"от пользователя {message[SENDER]}."
        )
    elif (
        message[DESTINATION] in names
        and names[message[DESTINATION]] not in listen_socks
    ):
        raise ConnectionError
    else:
        logger.error(
            f"Пользователь {message[DESTINATION]} не зарегистрирован на сервере, "
            f"отправка сообщения невозможна."
        )


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", default=7777, type=int, nargs="?")
    parser.add_argument("-a", default="", nargs="?")
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        logger.critical(
            f"Попытка запуска сервера с указанием неподходящего порта {listen_port}. "
            f"Допустимы адреса с 1024 до 65535."
        )
        sys.exit(1)

    return listen_address, listen_port


def main():
    listen_address, listen_port = arg_parser()

    logger.info(
        f"Запущен сервер, порт для подключений: {listen_port}, "
        f"адрес с которого принимаются подключения: {listen_address}. "
        f"Если адрес не указан, принимаются соединения с любых адресов."
    )
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    clients = []
    messages = []

    names = dict()

    transport.listen(5)
    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            logger.info(f"Установлено соедение с ПК {client_address}")
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(
                    clients, clients, [], 0
                )
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(
                        get_message(client_with_message),
                        messages,
                        client_with_message,
                        clients,
                        names,
                    )
                except Exception:
                    logger.info(
                        f"Клиент {client_with_message.getpeername()} "
                        f"отключился от сервера."
                    )
                    clients.remove(client_with_message)

        for i in messages:
            try:
                process_message(i, names, send_data_lst)
            except Exception:
                logger.info(f"Связь с клиентом с именем {i[DESTINATION]} была потеряна")
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()


if __name__ == "__main__":
    main()

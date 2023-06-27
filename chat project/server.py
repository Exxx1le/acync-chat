import sys
import socket
import argparse
import select
import json
import threading
import configparser
import os
from errors import IncorrectDataRecivedError
from variables import *
from log.config import server_logger
from log.logs_decor import log
from metaclasses import ServerVerifier
from descriptor import PortChecker
from server_db import ServerStorage
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from server_gui import (
    MainWindow,
    gui_create_model,
    HistoryWindow,
    create_stat_model,
    ConfigWindow,
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem

logger = server_logger.logger
conflag_lock = threading.Lock()


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
    return listen_address, listen_port


class Server(metaclass=ServerVerifier):
    port = PortChecker()

    def __init__(self, listen_address, listen_port, database):
        self.addr = listen_address
        self.port = listen_port
        self.database = database
        self.clients = []
        self.messages = []
        self.names = dict()
        super().__init__()

    def init_socket(self):
        logger.info(
            f"Запущен сервер, порт для подключений: {self.port} , адрес с которого принимаются подключения: {self.addr}. Если адрес не указан, принимаются соединения с любых адресов."
        )
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen()

    def run(self):
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
            except OSError as err:
                logger.error(f"Ошибка работы с сокетами: {err}")

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(
                            get_message(client_with_message), client_with_message
                        )
                    except OSError:
                        logger.info(
                            f"Клиент {client_with_message.getpeername()} отключился от сервера."
                        )
                        for name in self.names:
                            if self.names[name] == client_with_message:
                                self.database.user_logout(name)
                                del self.names[name]
                                break
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except (
                    ConnectionAbortedError,
                    ConnectionError,
                    ConnectionResetError,
                    ConnectionRefusedError,
                ):
                    logger.info(
                        f"Связь с клиентом с именем {message[DESTINATION]} была потеряна"
                    )
                    self.clients.remove(self.names[message[DESTINATION]])
                    self.database.user_logout(message[DESTINATION])
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
        global new_connection
        logger.debug(f"Разбор сообщения от клиента : {message}")

        if (
            ACTION in message
            and message[ACTION] == PRESENCE
            and TIME in message
            and USER in message
        ):
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(
                    message[USER][ACCOUNT_NAME], client_ip, client_port
                )
                send_message(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
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
            and self.names[message[SENDER]] == client
        ):
            self.messages.append(message)
            self.database.process_message(message[SENDER], message[DESTINATION])
            return

        elif (
            ACTION in message
            and message[ACTION] == EXIT
            and ACCOUNT_NAME in message
            and self.names[message[ACCOUNT_NAME]] == client
        ):
            self.database.user_logout(message[ACCOUNT_NAME])
            logger.info(
                f"Клиент {message[ACCOUNT_NAME]} корректно отключился от сервера."
            )
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            with conflag_lock:
                new_connection = True
            return

        elif (
            ACTION in message
            and message[ACTION] == GET_CONTACTS
            and USER in message
            and self.names[message[USER]] == client
        ):
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            send_message(client, response)

        elif (
            ACTION in message
            and message[ACTION] == ADD_CONTACT
            and ACCOUNT_NAME in message
            and USER in message
            and self.names[message[USER]] == client
        ):
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)

        elif (
            ACTION in message
            and message[ACTION] == REMOVE_CONTACT
            and ACCOUNT_NAME in message
            and USER in message
            and self.names[message[USER]] == client
        ):
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)

        elif (
            ACTION in message
            and message[ACTION] == USERS_REQUEST
            and ACCOUNT_NAME in message
            and self.names[message[ACCOUNT_NAME]] == client
        ):
            response = RESPONSE_202
            response[LIST_INFO] = [user[0] for user in self.database.users_list()]
            send_message(client, response)

        else:
            response = RESPONSE_400
            response[ERROR] = "Запрос некорректен."
            send_message(client, response)
            return


def main():
    listen_address, listen_port = arg_parser()
    database = ServerStorage()
    server = Server(listen_address, listen_port, database)
    server.run()

    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.statusBar().showMessage("Server Working")
    main_window.active_clients_table.setModel(gui_create_model(database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(gui_create_model(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    def server_config():
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(config["SETTINGS"]["Database_path"])
        config_window.db_file.insert(config["SETTINGS"]["Database_file"])
        config_window.port.insert(config["SETTINGS"]["Default_port"])
        config_window.ip.insert(config["SETTINGS"]["Listen_Address"])
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()
        config["SETTINGS"]["Database_path"] = config_window.db_path.text()
        config["SETTINGS"]["Database_file"] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, "Ошибка", "Порт должен быть числом")
        else:
            config["SETTINGS"]["Listen_Address"] = config_window.ip.text()
            if 1023 < port < 65536:
                config["SETTINGS"]["Default_port"] = str(port)
                print(port)
                with open("server.ini", "w") as conf:
                    config.write(conf)
                    message.information(
                        config_window, "OK", "Настройки успешно сохранены!"
                    )
            else:
                message.warning(
                    config_window, "Ошибка", "Порт должен быть от 1024 до 65536"
                )

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    server_app.exec_()


if __name__ == "__main__":
    main()

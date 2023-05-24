import sys
import socket
import json

def create_presence_message():
    message = {
        "action": "presence",
        "type": "status",
        "user": {
            "account_name": "my_username",
            "status": "Online"
        }
    }
    return message

def send_message(server_address, server_port, message):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        client_socket.send(json.dumps(message).encode())
        response = client_socket.recv(1024).decode()
        print("Server response:", response)
        client_socket.close()
    except ConnectionRefusedError:
        print("В соединеннии отказано")

if __name__ == "__main__":
    server_address = sys.argv[1]
    server_port = int(sys.argv[2]) if len(sys.argv) > 2 else 7777
    
    presence_message = create_presence_message()
    send_message(server_address, server_port, presence_message)

"""
Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов. 
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом. 
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения 
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""
import subprocess
from ipaddress import ip_address


def host_ping(nodes):
    for node in nodes:
        try:
            ip = ip_address(node)
            response = subprocess.Popen(
                ["ping", "-c", "3", str(ip)], shell=False, stdout=subprocess.PIPE
            )
            response.wait()
            if response.returncode == 0:
                print(f"Узел {node} доступен")
            else:
                print(f"Узел {node} недоступен")
        except ValueError:
            print(f"{node} не является допустимым IP-адресом")


nodes = ["google.com", "10.0.0.1", "localhost", "256.0.0.1"]
host_ping(nodes)

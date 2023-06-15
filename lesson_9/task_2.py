"""
Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только последний 
октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение.
"""
from ping3 import ping
from ipaddress import ip_network


def host_range_ping(base_ip, start, end):
    try:
        network = ip_network(base_ip)
    except ValueError as e:
        print(f"Неверный IP-адрес: {e}")
        return

    for i in range(start, end + 1):
        ip = str(network.network_address + i)
        response_time = ping(ip, timeout=5)
        if response_time is not None:
            print(f"Узел {ip} доступен")
        else:
            print(f"Узел {ip} недоступен")


base_ip = "192.168.0.0/24"
start = 1
end = 10
host_range_ping(base_ip, start, end)

from ping3 import ping
from ipaddress import ip_network
from tabulate import tabulate


def host_range_ping_tab(base_ip, start, end):
    try:
        network = ip_network(base_ip)
    except ValueError as e:
        print(f"Неверный IP-адрес: {e}")
        return

    results = []
    for i in range(start, end + 1):
        ip = str(network.network_address + i)
        response_time = ping(ip, timeout=5)
        if response_time is not None:
            status = "Доступен"
        else:
            status = "Недоступен"
        results.append([ip, status])

    table_headers = ["IP-адрес", "Статус"]
    print(tabulate(results, headers=table_headers, tablefmt="grid"))


base_ip = "192.168.0.0/24"
start = 1
end = 10
host_range_ping_tab(base_ip, start, end)

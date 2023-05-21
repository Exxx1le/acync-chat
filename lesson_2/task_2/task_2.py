import json

def write_order_to_json(item, quantity, price, buyer, date):
    order = {
        "item": item,
        "quantity": quantity,
        "price": price,
        "buyer": buyer,
        "date": date
    }

    with open("orders.json", "w") as file:
        json.dump(order, file, indent=4)
        file.write("\n")

write_order_to_json("Телефон", 2, 500, "Иванов", "2023-05-19")
write_order_to_json("Ноутбук", 1, 1200, "Петров", "2023-05-20")

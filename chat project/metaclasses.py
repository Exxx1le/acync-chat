import dis


class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        attrs = []
        for func in clsdict:
            try:
                interator = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in interator:
                    print(i)
                    if i.opname == "LOAD_GLOBAL":
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == "LOAD_ATTR":
                        if i.argval not in attrs:
                            attrs.append(i.argval)

        if "connect" in methods:
            raise TypeError("Недопустимо использование метода connect")

        if not ("SOCK_STREAM" in attrs and "AF_INET" in attrs):
            raise TypeError("Некорректная инициализация сокета.")

        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                interator = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in interator:
                    if i.opname == "LOAD_GLOBAL":
                        if i.argval not in methods:
                            methods.append(i.argval)
        for command in ("accept", "listen", "socket"):
            if command in methods:
                raise TypeError(
                    "Использован запрещенный метод (accept, listen или socket)"
                )
        if "get_message" in methods or "send_message" in methods:
            pass
        else:
            raise TypeError("Нет вызовов функций, работающих с сокетами.")
        super().__init__(clsname, bases, clsdict)

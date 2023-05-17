# 3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.

a = 'attribute'
b = 'класс'
c = 'функция'
d = 'type'

def check_bytes(attr):
    try:
        print(bytes(attr, 'ascii'))
    except UnicodeEncodeError as e:
        print(attr, ':', e)

check_bytes(a)
check_bytes(b)
check_bytes(c)
check_bytes(d)

#ошибку выдют кириллические строки

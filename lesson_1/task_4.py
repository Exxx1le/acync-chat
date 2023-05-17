# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в 
# байтовое и выполнить обратное преобразование (используя методы encode и decode).

a = 'разработка'
b = 'администрирование'
c = 'protocol'
d = 'standard'

a_encode = a.encode('utf-8')
b_encode = b.encode('utf-8')
c_encode = c.encode('utf-8')
d_encode = d.encode('utf-8')

a_decode = a_encode.decode('utf-8')
b_decode = b_encode.decode('utf-8')
c_decode = c_encode.decode('utf-8')
d_decode = d_encode.decode('utf-8')

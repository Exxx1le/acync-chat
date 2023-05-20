# 1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из файлов 
# info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:
# Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание 
# данных. 
# В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров «Изготовитель 
# системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в соответствующий список. 
# Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. 
#В этой же функции 
# создать главный список для хранения данных отчета — например, main_data — и поместить в него названия столбцов отчета 
# в виде списка: «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения для этих столбцов также 
# оформить в виде списка и поместить в файл main_data (также для каждого файла);
# Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение данных 
# через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
# Проверить работу программы через вызов функции write_to_csv().

import re
import csv
import os


def get_data():
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []

    main_data = [['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']]

    cwd = os.getcwd()
    files = [f'{cwd}/info_1.txt', f'{cwd}/info_2.txt', f'{cwd}/info_3.txt']

    for file in files:
        with open(file, 'r', encoding='windows-1251') as f:
            data = f.read()
            
            os_prod = re.search(r'Изготовитель системы:\s*(.*)', data)
            if os_prod:
                os_prod_list.append(os_prod.group(1))

            os_name = re.search(r'Название ОС:\s*(.*)', data)
            if os_name:
                os_name_list.append(os_name.group(1))

            os_code = re.search(r'Код продукта:\s*(.*)', data)
            if os_code:
                os_code_list.append(os_code.group(1))

            os_type = re.search(r'Тип системы:\s*(.*)', data)
            if os_type:
                os_type_list.append(os_type.group(1))

            main_data.append([os_prod.group(1), os_name.group(1), os_code.group(1), os_type.group(1)])

    return os_prod_list, os_name_list, os_code_list, os_type_list, main_data


def write_to_csv(csv_file):
    os_prod_list, os_name_list, os_code_list, os_type_list, main_data = get_data()

    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(main_data)

    print(f"Данные записаны в файл: {csv_file}")

write_to_csv('report.csv')

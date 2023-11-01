import requests
from collections import Counter
import os
from datetime import datetime
import sqlite3
import  json


def getPage(page, url, name_vacancies):
    params = {
        'text': f'NAME:{name_vacancies}',
        'area': 1,
        'page': page,
        'per_page': 20
    }
    result = requests.get(url, params=params)
    result_decode = result.content.decode()
    result.close()
    return result_decode
def check_time_delta(select_date_create):
    delta = 0
    if select_date_create:
        time_create_records = select_date_create[0][0]
        dt_mow = datetime.now()
        delta = (dt_mow - time_create_records).days
        return delta
    else:
        return delta
def parsingVacancies(list_pages):

    # считываем с каждой страницы вакансии
    list_items_pages = [page.get('items') for page in list_pages]

    # определяем id каждой вакансии на сайте hh.ru
    list_url_id = []
    for items in list_items_pages:
        for item in items:
            list_url_id.append(item.get('url'))
    list_key_skills = []
    for url in list_url_id:
        res_vac_id = json.loads(getVacancies_ID(url))
        value = res_vac_id.get('key_skills')
        list_key_skills.append(value)

    result_list_skills = skills_statistic(list_key_skills)
    return result_list_skills
def getVacancies_ID(url):
    result = requests.get(url)
    result_decode = result.content.decode()
    result.close()
    return result_decode
def skills_statistic(list_key_skills):
    list_all_skills = []
    for skills in list_key_skills:
        if type(skills) == list:
            for skill in skills:
                list_all_skills.append(skill.get('name'))
    sort_skills = Counter(list_all_skills)
    count_skills = len(sort_skills)
    list_sort_key = list(sort_skills)
    dict_skills = dict(sort_skills)
    value_sort_skills = sorted(dict_skills.values())
    value_sort_skills.reverse()
    list_statistic_skills = []
    for count in range(len(list_sort_key)):
        dict_skills = {}
        # value = f'count:{value_sort_skills[count]}, percent:{int(value_sort_skills[count] * 100 / count_skills)}%'
        # dict_skills = {list_sort_key[count]: value}
        interest = int(value_sort_skills[count] * 100 / count_skills)
        # dict_skills = {list_sort_key[count]: value}
        skills_tuple = (list_sort_key[count], interest)
        list_statistic_skills.append(skills_tuple)
    return list_statistic_skills

def averageSalary(list_salary):
    summ = 0
    for i in list_salary:
        summ += i
    average_salary = int(summ / len(list_salary))
    return average_salary



# функции для использования с БД SQlite без ORM
def create_data_base(name_db):
    try:
        connection = sqlite3.connect(name_db, detect_types=sqlite3.PARSE_DECLTYPES |
                                                           sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()
        print("База данных создана и успешно подключена к SQLite")
    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (connection):
            connection.close()
            print("Соединение с SQLite закрыто")

def create_table_sqlite(name_db, query):
    try:
        connection = sqlite3.connect(name_db, detect_types=sqlite3.PARSE_DECLTYPES |
                                                           sqlite3.PARSE_COLNAMES)
        sqlite_create_table_query = query
        cursor = connection.cursor()
        print("База данных подключена к SQLite")
        cursor.execute(sqlite_create_table_query)
        connection.commit()
        print("Таблица SQLite создана")
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (connection):
            connection.close()
            print("Соединение с SQLite закрыто")

def insert_date_table(name_db, query, data):
    try:
        connection = sqlite3.connect(name_db, detect_types=sqlite3.PARSE_DECLTYPES |
                                                           sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()
        print("Подключен к SQLite")
        sqlite_insert_with_param = query
        data_tuple = data
        if len(data) > 1:
            cursor.executemany(sqlite_insert_with_param, data_tuple)
        else:
            cursor.execute(sqlite_insert_with_param, data_tuple)
        connection.commit()
        print("Переменные Python успешно вставлены в таблицу")
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if connection:
            connection.close()
            print("Соединение с SQLite закрыто")

def read_date_table(name_db, query, param='N/A'):
    try:
        sqlite_connection = sqlite3.connect(name_db, detect_types=sqlite3.PARSE_DECLTYPES |
                                                                  sqlite3.PARSE_COLNAMES)
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")
        sqlite_select_query = query
        if param != 'N/A':
            cursor.execute(sqlite_select_query, param)
        else:
            cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
    return records

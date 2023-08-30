import json
import sqlite3
from function import create_data_base,create_table_sqlite, insert_date_table, read_date_table
import os
import datetime

# import requests_hh

# создаем и подключаем базу данных
# 'hh_parsing.db'
# create_data_base('hh_parsing.db')
# создаем таблицы
# query_table1 = '''CREATE TABLE vacancy (name_vacancies VARCHAR(64) UNIQUE,
#                                               id INTEGER PRIMARY KEY);'''
# create_table_sqlite('hh_parsing.db', query_table1)
#
# query_table2 = '''CREATE TABLE key_skills (
#                                 id INTEGER PRIMARY KEY,
#                                 name_skills VARCHAR(64) UNIQUE);'''
#
# create_table_sqlite('hh_parsing.db', query_table2)
#
# query_table3 = '''CREATE TABLE vacancy_key_skills (
#                                 vacancies_id INTEGER,
#                                 key_skills_id INTEGER,
#                                 statistics INTEGER,
#                                 date_recording timestamp,
#                                 FOREIGN KEY (vacancies_id) REFERENCES vacancy (id),
#                                 FOREIGN KEY (key_skills_id) REFERENCES key_skills (id),
#                                 PRIMARY KEY (vacancies_id,key_skills_id) );'''
#
# create_table_sqlite('hh_parsing.db', query_table3)

# добавим в таблицу новую колонку
# try:
#     connection = sqlite3.connect('hh_parsing.db')
#     cursor = connection.cursor()
#     print("успешно подключена к SQLite")
#     new_column1 = "ALTER TABLE vacancy_key_skills  ADD COLUMN statistics INTEGER"
#     new_column2 = "ALTER TABLE vacancy_key_skills  ADD COLUMN date_recording timestamp"
#     cursor.execute(new_column1)
#     cursor.execute(new_column2)
#     connection.commit()
#     print("Столбцы успешно добавлены")
#     cursor.close()
# except sqlite3.Error as error:
#     print("Ошибка при подключении к sqlite", error)
# finally:
#     if (connection):
#         connection.close()
#         print("Соединение с SQLite закрыто")

# добавляем данные в таблицы

# insert_query1 = """INSERT OR IGNORE INTO vacancy
#                               (name_vacancies)
#                               VALUES (?);"""
# date1 = []
# if os.path.exists('main.txt'):
#     with open('main.txt', 'r') as f:
#         date1.append(f.read())
#
# insert_date_table('hh_parsing.db', insert_query1, date1)

# insert_query2 = """INSERT OR IGNORE INTO key_skills
#                               (name_skills)
#                               VALUES (?);"""
# statistic_list = []
# with open('statistic_skills.txt', 'r') as f:
#     statistic_list = json.load(f)
# list_skills = []
# for skill in statistic_list:
#     list_skills.append(list(skill.keys()))
# insert_date_table('hh_parsing.db', insert_query2, list_skills)
# print(list_skills)

# получим список данных из таблиц для того что бы узнать id каждого значения

# qury_select1 = """SELECT * from vacancy"""
# data_vacancy = read_date_table('hh_parsing.db', qury_select1)
# data_vacancy = dict(data_vacancy)
# print(list(data_vacancy.keys())[0])
#
# qury_select2 = """SELECT * from key_skills"""
# list_tuple_skills = read_date_table('hh_parsing.db', qury_select2)
# # dict_data_skills = dict(list_tuple_skills)
# list_skills_id = []
# for tuple in list_tuple_skills:
#     list_skills_id.append(list(tuple))
# print(list_skills_id)
#
# insert_query3 = """INSERT OR IGNORE INTO vacancy_key_skills
#                               (vacancies_id,key_skills_id, statistics, date_recording)
#                               VALUES (?,?,?,?);"""
# if os.path.exists('main.txt'):
#     with open('main.txt', 'r') as f:
#         name_vacancy = f.read()
# vacancies_id = data_vacancy[name_vacancy]
# time_add = datetime.datetime.now()
# list_insert_date = []
#
# for row in list_skills:
#     skill_id = 0
#     for skill in list_skills_id:
#         if row[0] == skill[1]:
#             skill_id = skill[0]
#     count = list_skills.index(row)
#     row_list = []
#     row_list.append(vacancies_id)
#     row_list.append(skill_id)
#     row_list.append(list(statistic_list[count].values())[0])
#     row_list.append(time_add)
#     list_insert_date.append(row_list)
# print(list_insert_date)
# insert_date_table('hh_parsing.db', insert_query3, list_insert_date)

# # запрос из бд итоговой таблицы
# qury_select3 = """SELECT k.name_skills, vk.statistics from vacancy v, key_skills k, vacancy_key_skills vk WHERE vk.vacancies_id=v.id and
#  vk.key_skills_id=k.id and v.id=? ORDER BY statistics DESC"""
# # v.name_vacancies

# result_list = []
# result_list = read_date_table('hh_parsing.db', qury_select3, [vacancies_id])
# result_dict = dict(result_list)
# print(result_dict)

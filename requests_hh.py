import pprint
import json
import os
import datetime


def main(key_words):
    from function import getPage, getVacancies_ID, skills_statistic, check_time_delta
    from function import create_data_base, create_table_sqlite, insert_date_table, read_date_table

    # ищем вакансии по заданным параметрам и записываем результат в базу данных
    DOMAIN = 'https://api.hh.ru/'
    url_vacancies = f'{DOMAIN}vacancies'

    # создаем и подключаем базу данных
    create_data_base('hh_parsing.db')
    # создаем таблицы
    query_table1 = '''CREATE TABLE vacancy (name_vacancies VARCHAR(64) UNIQUE,
                                                  id INTEGER PRIMARY KEY);'''
    create_table_sqlite('hh_parsing.db', query_table1)
    query_table2 = '''CREATE TABLE key_skills (
                                    id INTEGER PRIMARY KEY,
                                    name_skills VARCHAR(64) UNIQUE);'''
    create_table_sqlite('hh_parsing.db', query_table2)
    query_table3 = '''CREATE TABLE vacancy_key_skills (
                                    vacancies_id INTEGER,
                                    key_skills_id INTEGER,
                                    statistics INTEGER,
                                    date_recording timestamp,
                                    FOREIGN KEY (vacancies_id) REFERENCES vacancy (id),
                                    FOREIGN KEY (key_skills_id) REFERENCES key_skills (id),
                                    PRIMARY KEY (vacancies_id,key_skills_id) );'''
    create_table_sqlite('hh_parsing.db', query_table3)
    # добавляем данные в таблицы
    vacancy_name = []
    vacancy_name.append(key_words)
    insert_query1 = """INSERT OR IGNORE INTO vacancy 
                                  (name_vacancies)
                                  VALUES (?);"""
    insert_date_table('hh_parsing.db', insert_query1, vacancy_name)
    # узнаем id vacancy
    qury_select1 = """SELECT * from vacancy"""
    data_vacancy = read_date_table('hh_parsing.db', qury_select1)
    data_vacancy = dict(data_vacancy)
    print(data_vacancy)
    vacancies_id = data_vacancy[key_words]
    # запрос из бд итоговой таблицы
    qury_select3 = """SELECT k.name_skills, vk.statistics from vacancy v, key_skills k, vacancy_key_skills vk WHERE vk.vacancies_id=v.id and
     vk.key_skills_id=k.id and v.id=? ORDER BY statistics DESC"""
    result_list_skills = []
    result_list_skills = read_date_table('hh_parsing.db', qury_select3, [vacancies_id])
    # делаем запрос из итоговой таблицы по столбцу key_skills_id столбец date_recording
    qury_select4 = """SELECT vk.date_recording from vacancy v, vacancy_key_skills vk WHERE vk.vacancies_id=v.id and v.id=?"""
    list_time = read_date_table('hh_parsing.db', qury_select4, [vacancies_id])
    print(f'{check_time_delta(list_time)} дней назад были добавлены данные в таблицу')

    # если данных в базе еще нет или данные есть и были добавлены в таблицу больше чем 15 дней назад
    if not result_list_skills or check_time_delta(list_time) > 15:
        list_pages = []
        for i in range(10):
            res_pages = json.loads(getPage(i, url_vacancies, key_words))
            list_pages.append(res_pages)
        # считываем с каждой страницы вакансии и у каждой вакансии зарплату, определяем среднии начальную и мажсимальную зарплаты
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
        list_skills = []
        for skill_stat in result_list_skills:
            skill = (skill_stat[0],)
            list_skills.append(skill)
        print(list_skills)
        insert_query2 = """INSERT OR IGNORE INTO key_skills
                                              (name_skills)
                                              VALUES (?);"""
        insert_date_table('hh_parsing.db', insert_query2, list_skills)

        # получим список данных из таблицы для того что бы узнать id каждого значения skills
        qury_select2 = """SELECT * from key_skills"""
        list_tuple_skills = read_date_table('hh_parsing.db', qury_select2)
        list_skills_id = []
        for tuple in list_tuple_skills:
            list_skills_id.append(list(tuple))
        # print(list_skills_id)

        # подготовим список для заполнения итоговой таблицы в базе данных
        insert_query3 = """INSERT OR IGNORE INTO vacancy_key_skills
                                      (vacancies_id,key_skills_id, statistics, date_recording)
                                      VALUES (?,?,?,?);"""
        time_add = datetime.datetime.now()
        list_insert_date = []
        for row in list_skills:
            skill_id = 0
            for skill in list_skills_id:
                if row[0] == skill[1]:
                    skill_id = skill[0]
            count = list_skills.index(row)
            row_list = []
            row_list.append(vacancies_id)
            row_list.append(skill_id)
            row_list.append(int(result_list_skills[count][1]))
            row_list.append(time_add)
            list_insert_date.append(row_list)
        # print(list_insert_date)
        insert_date_table('hh_parsing.db', insert_query3, list_insert_date)

    return result_list_skills


if __name__ == '__main__':
    key_words = input('Введите вакансию по которой будем искать навыки: ')
    data_list = main(key_words)
    pprint.pprint(data_list)



# работа через файл _____________________________________________________________________________

# FILE_NAME_VACANCIES = f'vacancies_search_{key_words}.txt'
# list_pages = []
# list_directory = os.listdir()
# flag_vacancies_file = [i for i in list_directory if FILE_NAME_VACANCIES == i]
# if flag_vacancies_file and check_time_delta(FILE_NAME_VACANCIES) < 15:
#     print('Загружаю из файла..')
#     with open(FILE_NAME_VACANCIES, 'r') as f:
#         list_pages = json.load(f)
# else:
#     print('Загружаю с сайта..')
#     for i in range(10):
#         res_pages = json.loads(getPage(i, url_vacancies, key_words))
#         list_pages.append(res_pages)
#     with open(FILE_NAME_VACANCIES, 'w') as f:
#         json.dump(list_pages, f)
#
# # считываем с каждой страницы вакансии и у каждой вакансии зарплату, определяем среднии начальную и мажсимальную зарплаты
# list_items_pages = [page.get('items') for page in list_pages]
# # определяем навыки для вакансий и записываем в файл
# list_url_id = []
# for items in list_items_pages:
#     for item in items:
#         list_url_id.append(item.get('url'))
# FILE_NAME_SKILLS = f'skills_{key_words}.txt'
# list_key_skills = []
# flag_skills_file = [i for i in list_directory if FILE_NAME_SKILLS == i]
# if flag_skills_file and check_time_delta(FILE_NAME_SKILLS) < 15:
#     print('Загружаю из файла..')
#     with open(FILE_NAME_SKILLS, 'r') as f:
#         list_key_skills = json.load(f)
# else:
#     print('Загружаю с сайта..')
#     for url in list_url_id:
#         res_vac_id = json.loads(getVacancies_ID(url))
#         value = res_vac_id.get('key_skills')
#         list_key_skills.append(value)
#     with open(FILE_NAME_SKILLS, 'w') as f:
#         json.dump(list_key_skills, f)
#
# # собираем статистику по требованиям указанным в вакансиях и записываем итоговый файл
# result_list_skills = skills_statistic(list_key_skills)
# FILE_NAME_STATISTIC_SKILLS = 'statistic_skills.txt'
# with open(FILE_NAME_STATISTIC_SKILLS, 'w') as f:
#     json.dump(result_list_skills, f, indent=2)
# return result_list_skills
#     # list_items_pages

# def average_salary(list_items_pages):
#     from function import averageSalary
#     list_salary = [item.get('salary') for items in list_items_pages for item in items if item.get('salary') != None]
#     from_salary = []
#     to_salary = []
#     for i in list_salary:
#         if i.get('from') != None and i.get('currency') == 'RUR': from_salary.append(i.get('from'))
#         if i.get('to') != None and i.get('currency') == 'RUR': to_salary.append(i.get('to'))
#     print(f'Average from salary {key_words}: {averageSalary(from_salary)} RUR')
#     print(f'Average to salary {key_words}: {averageSalary(to_salary)} RUR')

# if __name__ == '__main__':
#     key_words = input('Введите вакансию по которой будем искать навыки и определять уровень зарплаты: ')
#     data_list = main(key_words)
#     # average_salary(data_list)
#     pprint.pprint(data_list)

import pprint
import json
import os


def main(key_words):
    from function import getPage, getVacancies_ID, skills_statistic, check_time_delta

    # ищем вакансии по заданным параметрам и записываем результат в файл
    DOMAIN = 'https://api.hh.ru/'
    url_vacancies = f'{DOMAIN}vacancies'
    FILE_NAME_VACANCIES = f'vacancies_search_{key_words}.txt'
    list_pages = []
    list_directory = os.listdir()
    flag_vacancies_file = [i for i in list_directory if FILE_NAME_VACANCIES == i]
    if flag_vacancies_file and check_time_delta(FILE_NAME_VACANCIES) < 15:
        print('Загружаю из файла..')
        with open(FILE_NAME_VACANCIES, 'r') as f:
            list_pages = json.load(f)
    else:
        print('Загружаю с сайта..')
        for i in range(10):
            res_pages = json.loads(getPage(i, url_vacancies, key_words))
            list_pages.append(res_pages)
        with open(FILE_NAME_VACANCIES, 'w') as f:
            json.dump(list_pages, f)

    # считываем с каждой страницы вакансии и у каждой вакансии зарплату, определяем среднии начальную и мажсимальную зарплаты
    list_items_pages = [page.get('items') for page in list_pages]
    # определяем навыки для вакансий и записываем в файл
    list_url_id = []
    for items in list_items_pages:
        for item in items:
            list_url_id.append(item.get('url'))
    FILE_NAME_SKILLS = f'skills_{key_words}.txt'
    list_key_skills = []
    flag_skills_file = [i for i in list_directory if FILE_NAME_SKILLS == i]
    if flag_skills_file and check_time_delta(FILE_NAME_SKILLS) < 15:
        print('Загружаю из файла..')
        with open(FILE_NAME_SKILLS, 'r') as f:
            list_key_skills = json.load(f)
    else:
        print('Загружаю с сайта..')
        for url in list_url_id:
            res_vac_id = json.loads(getVacancies_ID(url))
            value = res_vac_id.get('key_skills')
            list_key_skills.append(value)
        with open(FILE_NAME_SKILLS, 'w') as f:
            json.dump(list_key_skills, f)

    # собираем статистику по требованиям указанным в вакансиях и записываем итоговый файл
    result_list_skills = skills_statistic(list_key_skills)
    FILE_NAME_STATISTIC_SKILLS = 'statistic_skills.txt'
    with open(FILE_NAME_STATISTIC_SKILLS, 'w') as f:
        json.dump(result_list_skills, f, indent=2)
    return list_items_pages


def average_salary(list_items_pages):
    from function import averageSalary
    list_salary = [item.get('salary') for items in list_items_pages for item in items if item.get('salary') != None]
    from_salary = []
    to_salary = []
    for i in list_salary:
        if i.get('from') != None and i.get('currency') == 'RUR': from_salary.append(i.get('from'))
        if i.get('to') != None and i.get('currency') == 'RUR': to_salary.append(i.get('to'))
    print(f'Average from salary {key_words}: {averageSalary(from_salary)} RUR')
    print(f'Average to salary {key_words}: {averageSalary(to_salary)} RUR')


if __name__ == '__main__':
    key_words = input('Введите вакансию по которой будем искать навыки и определять уровень зарплаты: ')
    data_list = main(key_words)
    average_salary(data_list)
    with open('statistic_skills.txt', 'r') as f:
        result = json.load(f)
    pprint.pprint(result)

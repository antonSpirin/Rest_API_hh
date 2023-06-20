import requests
import pprint
import statistics
from statistics import mode, multimode
import gc
import json
import os
from function import getPage, averageSalary, getVacancies_ID,skills_statistic

# ищем вакансии по заданным параметрам и записываем ресультат в файл
DOMAIN = 'https://api.hh.ru/'
url_vacancies = f'{DOMAIN}vacancies'
FILE_NAME_VACANCIES = 'vacancies_search.txt'
list_pages = []
if os.path.exists(FILE_NAME_VACANCIES):
    with open(FILE_NAME_VACANCIES, 'r') as f:
        list_pages = json.load(f)
if not list_pages:
    for i in range(28):
        res_pages = json.loads(getPage(i, url_vacancies))
        list_pages.append(res_pages)
    with open(FILE_NAME_VACANCIES, 'w') as f:
        json.dump(list_pages, f)

# считываем с каждой страницы вакансии и у каждой вакансии зарплату, определяем среднии начальную и мажсимальную зарплаты
list_items_pages = [page.get('items') for page in list_pages]
list_salary = [item.get('salary') for items in list_items_pages for item in items if item.get('salary') != None]
# pprint.pprint(list_salary)
from_salary = []
to_salary = []
for i in list_salary:
    if i.get('from') != None and i.get('currency') == 'RUR': from_salary.append(i.get('from'))
    if i.get('to') != None and i.get('currency') == 'RUR': to_salary.append(i.get('to'))
print(f'Average from salary Python Developer: {averageSalary(from_salary)} RUR')
print(f'Average to salary Python Developer: {averageSalary(to_salary)} RUR')

# определзем требования вакансий и записываем в файл
list_url_id = []
for items in list_items_pages:
    for item in items:
        list_url_id.append(item.get('url'))

FILE_NAME_SKILLS = 'skills.txt'
list_key_skills = []
if os.path.exists(FILE_NAME_SKILLS):
    with open(FILE_NAME_SKILLS, 'r') as f:
        list_key_skills = json.load(f)
if not list_key_skills:
    for url in list_url_id:
        res_vac_id = json.loads(getVacancies_ID(url))
        list_key_skills.append(res_vac_id.get('key_skills'))
    with open(FILE_NAME_SKILLS, 'w') as f:
        json.dump(list_key_skills, f)

# собираем статистику по требованиям указанным в вакансиях и записываем итоговый файл
result_list_skills=skills_statistic(list_key_skills)
pprint.pprint(result_list_skills)

FILE_NAME_STATISTIC_SKILLS='statistic_skills.txt'
with open(FILE_NAME_STATISTIC_SKILLS, 'w') as f:
    json.dump(result_list_skills, f,indent=2)







import requests
from collections import Counter
import os
from datetime import datetime


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


def getVacancies_ID(url):
    result = requests.get(url)
    result_decode = result.content.decode()
    result.close()
    return result_decode


def averageSalary(list_salary):
    summ = 0
    for i in list_salary:
        summ += i
    average_salary = int(summ / len(list_salary))
    return average_salary


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
        value = f'count:{value_sort_skills[count]}, percent:{int(value_sort_skills[count] * 100 / count_skills)}%'
        dict_skills = {list_sort_key[count]: value}
        list_statistic_skills.append(dict_skills)
    return list_statistic_skills

def check_time_delta(file_name):
    create_file_time = os.path.getmtime(file_name)
    formatted_time = datetime.fromtimestamp(create_file_time)
    dt_mow = datetime.now()
    delta = (dt_mow - formatted_time).days
    return delta



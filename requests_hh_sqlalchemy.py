import pprint
import json
import os
import datetime

from function import check_time_delta


def main(key_words):
    from function import getPage, parsingVacancies, check_time_delta, getVacancies_ID, skills_statistic
    from sqlalchemy import Column, Integer, String, TIMESTAMP, create_engine, ForeignKey, desc
    from sqlalchemy.orm import declarative_base
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.exc import IntegrityError

    # ищем вакансии по заданным параметрам и записываем результат в базу данных
    DOMAIN = 'https://api.hh.ru/'
    url_vacancies = f'{DOMAIN}vacancies'

    # создаем и подключаем базу данных
    engine = create_engine('sqlite:///hh_parsing_orm.db', echo=True)
    Base = declarative_base()

    # проектируем таблицы с помощью классов
    class Vacansy(Base):
        __tablename__ = 'vacancy'
        name_vacancies = Column(String, unique=True)
        id = Column(Integer, primary_key=True)

        def __init__(self, name):
            self.name_vacancies = name

        def __str__(self):
            return self.name_vacancies

        # def __repr__(self)-> str:
        #     return f'{self.name_vacancies}'

    class Кey_skills(Base):
        __tablename__ = 'key_skills'
        id = Column(Integer, primary_key=True)
        name_skills = Column(String, unique=True)

        def __init__(self, name):
            self.name_skills = name

        def __str__(self):
            return f'{self.id}) {self.name_skills}'

    class Vacancy_key_skills(Base):
        __tablename__ = 'vacancy_key_skills'
        vacancies_id = Column(Integer, ForeignKey('vacancy.id'), primary_key=True)
        key_skills_id = Column(Integer, ForeignKey('key_skills.id'), primary_key=True)
        statistics = Column(Integer)
        date_recording = Column(TIMESTAMP)

        def __init__(self, vacancy_id, key_id, statistics, date_recording):
            self.vacancies_id = vacancy_id
            self.key_skills_id = key_id
            self.statistics = statistics
            self.date_recording = date_recording

        # def __str__(self):
        #     return f'{self.id}) {self.name_skills}'

    # создаем таблицы
    Base.metadata.create_all(engine)

    # добавляем данные в таблицы
    # vacancy_name = []
    # vacancy_name.append(key_words)
    with Session(engine) as session:
        # узнаем id vacancy
        # vacancy_query = session.query(Vacansy).filter(Vacansy.name_vacancies == key_words).first()
        # if not vacancy_query:
        #     vacancy = Vacansy(key_words)
        #     session.add(vacancy)
        #     session.commit()
        #     vacancy_query = session.query(Vacansy).filter(Vacansy.name_vacancies == key_words).first()
        vacancy = Vacansy(key_words)
        try:
            session.add(vacancy)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            print(f"Duplicate data: {e}")
        vacancy_query = session.query(Vacansy).filter(Vacansy.name_vacancies == key_words).first()
        vacancies_id = vacancy_query.id
        print(f'У вакансии {key_words} ID в базе = {vacancies_id}')

    # запрос из бд итоговой таблицы
    result_list_skills = []
    with Session(engine) as session:
        result_list_skills = session.query(
            Кey_skills.name_skills, Vacancy_key_skills.statistics).join(Кey_skills).join(Vacansy).filter(
            Vacansy.id == vacancies_id).order_by(
            desc(Vacancy_key_skills.statistics)).all()
        pprint.pprint(f'Печатаем итоговый список {result_list_skills}')

        # делаем запрос из итоговой таблицы по столбцу key_skills_id столбец date_recording
        list_time = session.query(
            Vacancy_key_skills.date_recording).filter(Vacancy_key_skills.vacancies_id == vacancies_id).all()

    # сколько прошло времени смомента предыдущего получения даных парсером и добавления их в таблицу
    time_delta = check_time_delta(list_time)
    print(f'{time_delta} дней назад были добавлены данные в таблицу')

    # если данных в базе еще нет или данные есть и были добавлены в таблицу больше чем 15 дней назад
    if not result_list_skills or time_delta > 15:
        list_pages = []
        for i in range(15):
            res_pages = json.loads(getPage(i, url_vacancies, key_words))
            list_pages.append(res_pages)

        # получаем вакансии и skills
        result_list_skills = parsingVacancies(list_pages)
        # pprint.pprint(result_list_skills)
        list_skills = []
        # for skill_stat in result_list_skills:
        #     skill = (skill_stat[0],)
        #     list_skills.append(skill)
        # print(list_skills)
        for skill_stat in result_list_skills:
            list_skills.append(skill_stat[0])
        # print(list_skills)

        # добавим skills v таблицу
        list_obj_skills = []
        for name_skills in list_skills:
            skill = Кey_skills(name_skills)
            # list_obj_skills.append(skill)
            with Session(engine) as session:
                try:
                    session.add(skill)
                    session.commit()
                except IntegrityError as e:
                    session.rollback()
                    print(f"Duplicate data: {e}")


        # получим список данных из таблицы для того что бы узнать id каждого значения skills
        with Session(engine) as session:
            skills_query = session.query(Кey_skills).all()
        list_skills_id = []
        for skill_obj in skills_query:
            list_skills_id.append([skill_obj.id, skill_obj.name_skills])
        # print(list_skills_id)

        # подготовим список для заполнения итоговой таблицы в базе данных
        time_add = datetime.datetime.now()
        list_insert_date = []
        for row in list_skills:
            skill_id = 0
            for skill in list_skills_id:
                if row == skill[1]:
                    skill_id = skill[0]
            count = list_skills.index(row)
            statistic_skill = int(result_list_skills[count][1])
            result_obj = Vacancy_key_skills(vacancies_id, skill_id, statistic_skill, time_add)
            list_insert_date.append(result_obj)
        # print(list_insert_date)
        with Session(engine) as session:
            session.add_all(list_insert_date)
            session.commit()

    return result_list_skills


if __name__ == '__main__':
    key_words = input('Введите вакансию по которой будем искать навыки: ')
    data_list = main(key_words)
    pprint.pprint(data_list)

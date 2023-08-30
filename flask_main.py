from flask import Flask, render_template, request,redirect,session
from function import read_date_table
import os

import requests_hh

app = Flask(__name__)
app.secret_key = 'my_secret_key'

@app.route("/")
def index():
    name_project = 'Parsing-HH.ru'
    return render_template('index.html', name_project=name_project)

@app.route('/search_form/', methods=['GET', 'POST'])
def input():
    if request.method == 'POST':
        text = request.form['input_text']
        session["text"] = text
        requests_hh.main(text.lower())
        return redirect('/results/')
    else:
        return render_template('search_form.html')

@app.route('/results/')
def results():
    text = session.get("text", None)
    # запрос из бд итоговой таблицы
    qury_select1 = """SELECT * from vacancy"""
    data_vacancy = read_date_table('hh_parsing.db', qury_select1)
    data_vacancy = dict(data_vacancy)
    print(data_vacancy)
    vacancies_id = data_vacancy[text]
    qury_select3 = """SELECT k.name_skills, vk.statistics from vacancy v, key_skills k, vacancy_key_skills vk WHERE vk.vacancies_id=v.id and
     vk.key_skills_id=k.id and v.id=? ORDER BY statistics DESC"""
    data = read_date_table('hh_parsing.db', qury_select3, [vacancies_id])
    return render_template('results.html', text=text, data=data, list=list)
@app.route('/contacts/')
def contats():
    return render_template('contacts.html')


if __name__ == "__main__":
    app.run(debug=True)

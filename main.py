from flask import Flask, render_template, request, url_for, redirect
import json, os

import requests_hh

app = Flask(__name__)

@app.route("/")
def index():
    name_project = 'Parsing-HH.ru'
    return render_template('index.html', name_project=name_project)

@app.route('/results/')
def results():
    if os.path.exists('main.txt'):
        with open('main.txt', 'r') as f:
            text = f.read()
    with open('statistic_skills.txt', 'r') as f:
        data = json.load(f)
    return render_template('results.html', text=text, data=data, list=list)

@app.route('/search_form/', methods=['GET', 'POST'])
def input():
    if request.method == 'POST':
        text = request.form['input_text']
        with open('main.txt', 'w') as f:
            f.write(f'{text}\n')
        requests_hh.main(text.lower())
        return redirect('/results/')
    else:
        return render_template('search_form.html')

@app.route('/contacts/')
def contats():
    return render_template('contacts.html')


if __name__ == "__main__":
    app.run(debug=True)

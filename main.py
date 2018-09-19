from wiktionaryparser import WiktionaryParser
from flask import Flask, request, json, Response
import random

parser = WiktionaryParser()
app = Flask(__name__)
print(__name__)

website_name = 'http://whateverwecallourwebsite.com'

def get_definition(word):
    return parser.fetch(word)[0]['definitions'][0]['text'][1]

def make_json_reponse(data):
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    resp.headers['Link'] = website_name
    return resp

@app.route('/api/getDefinition/<word>')
def query(word):
    data = {
        'definition' : get_definition(word)
    }
    return make_json_reponse(data)

@app.route('/api/getQuestion')
def get_question():
    fin = open("words.txt", "r")
    all_words = fin.readlines()
    words = []
    while len(words) < 4:
        word = random.choice(all_words).strip()
        if word not in words:
            words.append(word)
    ans = random.randint(0, 4)
    data = {
        'options' : words,
        'definition' : get_definition(words[ans]),
        'answer' : ans
    }
    return make_json_reponse(data)

from wiktionaryparser import WiktionaryParser
from flask import Flask, request, json, Response
import random

parser = WiktionaryParser()
app = Flask(__name__)
print(__name__)

website_name = 'http://whateverwecallourwebsite.com'

def get_definition(word):

    try:
        return parser.fetch(word)[0]['definitions'][0]['text'][1]
    except:
        return ""

def make_json_reponse(data, status):

    js = json.dumps(data)
    resp = Response(js, status=status, mimetype='application/json')
    resp.headers['Link'] = website_name
    return resp

@app.route('/api/getDefinition/<query>')
def query(query):

    words = query.split(',')
    data = {}
    error = False

    for word in words:
        data[word] = {'definition' : get_definition(word)}
        if data[word]['definition'] == "":
            print(word + " has an error")
            error = True
    
    return make_json_reponse(data, 400 if error else 200)

@app.route('/api/getQuestion')
def get_question():
    count = request.args.get('count')
    if count is None:
        count = 1
    count = int(count)

    fin = open("words.txt", "r")
    all_words = fin.readlines()

    data = []
    for i in range(count):
        words = []

        while len(words) < 4:
            word = random.choice(all_words).strip()
            if word not in words:
                words.append(word)
        ans = random.randint(0, 3)

        data.append({
            'options' : words,
            'definition' : get_definition(words[ans]),
            'answer' : ans
        })

    return make_json_reponse(data, 200)

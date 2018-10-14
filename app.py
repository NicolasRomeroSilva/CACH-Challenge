from wiktionaryparser import WiktionaryParser
from flask import Flask, request, json, Response, redirect, url_for
from werkzeug.contrib.cache import SimpleCache
import random
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
import pymongo
import os

parser = WiktionaryParser()

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

cache = SimpleCache()

# GOOGLE LOGIN
google_blueprint = make_google_blueprint(
    client_id=os.environ['GOOGLE_ID'],
    client_secret=os.environ['GOOGLE_SECRET'],
    scope=[
        'https://www.googleapis.com/auth/plus.me',
        'https://www.googleapis.com/auth/userinfo.email',
    ],
    redirect_to='google_login'
)
app.register_blueprint(google_blueprint, url_prefix='/api/login')

# FACEBOOK LOGIN
facebook_blueprint = make_facebook_blueprint(
    client_id=os.environ['FACEBOOK_ID'],
    client_secret=os.environ['FACEBOOK_SECRET'],
    scope=['email'],
    redirect_to='facebook_login'
)
app.register_blueprint(facebook_blueprint, url_prefix='/api/login')

mongo = pymongo.MongoClient(os.environ['DB'], maxPoolSize=50, connect=False)
db = pymongo.database.Database(mongo, 'users')
users = pymongo.collection.Collection(db, 'users')

website_name = 'https://lingo-backend.herokuapp.com'

word_data_items = [
    'definition',
    'part_of_speech',
    'etymology',
    'examples',
    'synonyms'
]

class Word:
    def __init__(self, data):
        self.definition = [data[0]['definitions'][0]['text'][1]]
        self.part_of_speech = [data[0]['definitions'][0]['partOfSpeech']]
        self.etymology = [data[0]['etymology']]

        self.examples = []
        self.synonyms = []
        for example in data[0]['definitions'][0]['examples']:
            if example.startswith('Synonym'):
                self.synonyms.append(example.split(': ')[1].split(', '))
            else: self.examples.append(example)
    
    def get_random_hint(self):
        info = random.choice(list(self.__dict__.items()))
        while info[0] == 'definition' or not info[1]:
            info = random.choice(list(self.__dict__.items()))
        return {info[0]: info[1]}
    
    def get_hint(self, item):
        return {item: self.__dict__[item]}

# a helper function that gets information
# for a word and stores it in the cache,
# that is if it's not already there
#
# returns an instance of the Word class
def get_info(word):
    data = cache.get(word)
    if data is None:
        data = Word(parser.fetch(word))
        cache.set(word, data, timeout=5 * 60) # cache for five minutes
    return data

def make_json_response(data, status):
    js = json.dumps(data)
    resp = Response(js, status=status, mimetype='application/json')
    resp.headers['Link'] = website_name
    return resp

@app.route('/terms')
def terms():
    return "We won't sell or misuse your data in any way. Just don't dox us please."

@app.route('/api/getDefinition/<query>')
def get_definition(query):
    words = query.split(',')
    data = {}
    error = False

    for word in words:
        data[word] = {'definition' : get_info(word).definition}
        if not data[word]['definition']:
            print(word + ' has an error')
            error = True
    
    return make_json_response(data, 400 if error else 200)

@app.route('/api/getQuestion')
def get_question():
    count = request.args.get('count')
    if count is None:
        count = 1
    count = int(count)

    fin = open('words.txt', 'r')
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
            'definition' : get_info(words[ans]).definition,
            'answer' : ans
        })

    return make_json_response(data, 200)

@app.route('/api/getHint/<query>')
def get_hint(query):
    info = request.args.get('info')
    if info and request.args.get('info') not in word_data_items:
        return make_json_response({}, 500)
    
    data = get_info(query)
    if not info:
        return make_json_response(data.get_random_hint(), 200)
    return make_json_response(data.get_hint(info), 200)

@app.route('/login/google')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/oauth2/v2/userinfo')
    assert resp.ok, resp.text

    username = resp.json()['email']
    if not users.find_one({ "username": username }):
        users.insert_one({
            "username": username,
            "words": []
        })
    return make_json_response({ "username": username }, 200)

@app.route('/login/facebook')
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    resp = facebook.get('/oauth2/v2/userinfo')
    assert resp.ok, resp.text

    username = resp.json()['email']
    if not users.find_one({ "username": username }):
        users.insert_one({
            "username": username,
            "words": []
        })
    return make_json_response({ "username": username }, 200)

@app.route('/api/<user>/getWords')
def get_words(user):
    document = users.find_one({ "username": user})
    if document:
        return make_json_response({ "words": document["words"]}, 200)
    return make_json_response({ "words": []}, 200)

@app.route('/api/<user>/addWord/<word>')
def add_words(user, word):
    users.update_one({'username': user}, {'$push': {'words': word}})
    return "success"
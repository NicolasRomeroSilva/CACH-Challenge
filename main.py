from wiktionaryparser import WiktionaryParser
from flask import Flask, request, json, Response

parser = WiktionaryParser()
app = Flask(__name__)

def query():
    data = parser.fetch(request.args.get('w'))
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    resp.headers['Link'] = 'http://whateverwecallourwebsite.com'
    return resp
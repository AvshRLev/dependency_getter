from flask import Flask, request
from flask.templating import render_template
from data.npm import get_from_node_api
from data.redis import get_from_cache, cache_for_one_day
from utils import clean_version, extract_deps
import json

app = Flask(__name__)

@app.route("/",  methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
            
@app.route("/<string:package>/<string:version>", methods=['GET'])
def get_dep(package, version):
    version = clean_version(version)
    response = handle_get_request(f'{package}/{version}')
    return response

@app.route("/<string:namespace>/<string:package>/<string:version>", methods=['GET'])
def get_namespace_dep(namespace, package, version):
    version = clean_version(version)
    response = handle_get_request(f'{namespace}/{package}/{version}')
    return response

def handle_get_request(path):
    response = get_from_cache(path)
    if response is None:
        response = get_from_node_api(f'{path}') 
        cache_for_one_day(path, response)       
        return extract_deps(response.json())
    return extract_deps(json.loads(response))

if __name__ == '__main__':
    app.run(debug=True)

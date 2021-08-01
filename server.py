from flask import Flask, request
from flask.templating import render_template
from data.npm import get_from_node_api
from data.redis import get_from_cache, cache_for_one_day
from utils import clean_version, extract_deps
import redis
import requests
import json
import os


redis_host = os.environ.get('REDIS', default='localhost')
redis_port = 6379
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

npm_base_url = os.environ.get('NPM_BASE_URL', default='https://registry.npmjs.org')


app = Flask(__name__)

@app.route("/",  methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        package_name = request.form.get('package_name')
        package_version = request.form.get('package_version')
        dependencies = requests.get(f'http://localhost:5000/{package_name}/{package_version}')
        if dependencies.status_code != 200:
            return render_template('index.html', message="Could not retrieve the requested dependency")
        dependencies = dependencies.json()
        return render_template('index.html', dependencies=dependencies)

        
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
    response = get_from_cache(path, redis_client)
    if response is None:
        response = get_from_node_api(f'{npm_base_url}/{path}') 
        cache_for_one_day(path, response, redis_client)       
        return extract_deps(response.json())
    return extract_deps(json.loads(response))




if __name__ == '__main__':
    app.run(debug=True)

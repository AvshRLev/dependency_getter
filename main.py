from flask import Flask, request
from flask.templating import render_template
from dotenv import load_dotenv
import redis
import requests
import json
import os

load_dotenv()
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
    response = get_from_cache(path)
    if response is None:
        response = get_from_node_api(f'{npm_base_url}/{path}') 
        cache_for_one_day(path, response)       
        return extract_deps(response.json())
    return extract_deps(json.loads(response))


def get_from_node_api(path):
    response = requests.get(path)
    if response.status_code != 200:
        return {"code": response.status_code, "response": response.json()}    
    return response

def cache_for_one_day(path_string, response):
    redis_client.setex(path_string , 86400, json.dumps(response.json()))

def get_from_cache(path_string):
    return redis_client.get(path_string)

def clean_version(version):
    if version == "*":
        version = "latest"
        return version
    if version[0] == "^" or version[0] == "~":
        version = version[1:] 
        return version
    if version[0] == ">":
        version = "latest"
        return version
    if version[-1] == "x":
        version = version.replace("x", "0")
        return version
    return version

def extract_deps(response):
    deps = {}
    devDeps = {}
    if 'dependencies' in response:
        deps = response['dependencies']
    if 'devDependencies' in response:
        devDeps = response['devDependencies']
    return {
        "deps": deps,
        "devDeps": devDeps
    }


if __name__ == '__main__':
    app.run(debug=True)

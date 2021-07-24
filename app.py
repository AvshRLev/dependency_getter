from flask import Flask, request
from flask.templating import render_template
import redis
import requests
import json

redis_host = 'localhost'
redis_port = 6379

redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)


app = Flask(__name__)

@app.route("/",  methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template(index.html)
        
@app.route("/<string:package>/<string:version>")
def get_dep(package, version):
    response = redis_client.get(f'{package}/{version}')
    print(f'{response} from cache')
    if response is None:
        response = requests.get(f'https://registry.npmjs.org/{package}/{version}')
        print(f'{response} from node api') 
        redis_client.set(f'{package}/{version}', json.dumps(response.json()))
        return response.json()
    return response
    


if __name__ == '__main__':
    app.run(debug=True)

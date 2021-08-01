import requests
import os

npm_base_url = os.environ.get('NPM_BASE_URL', default='https://registry.npmjs.org')

def get_from_node_api(path):
    response = requests.get(f'{npm_base_url}/{path}')
    if response.status_code != 200:
        return {"code": response.status_code, "response": response.json()}    
    return response
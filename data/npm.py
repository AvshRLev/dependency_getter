import requests

def get_from_node_api(path):
    response = requests.get(path)
    if response.status_code != 200:
        return {"code": response.status_code, "response": response.json()}    
    return response
import requests

base_url = 'http://127.0.0.1:5000'

# Use a Session with trust_env disabled so requests ignores any system/corporate
# proxy environment variables (HTTP_PROXY, HTTPS_PROXY, etc). Without this, requests
# will try to route even localhost calls through a configured proxy, which can
# reject them (e.g. with a bare 403) even though the local server is working fine -
# confirmed here since curl (which doesn't route localhost through the proxy) got
# a clean 200 while requests was getting 403.
session = requests.Session()
session.trust_env = False

# GET requests
def get_api_data(endpoint, params = {}):
    response = session.get(f'{base_url}{endpoint}', params=params)
    return response

# POST requests
def post_api_data(endpoint, data):
    response = session.post(f'{base_url}{endpoint}', json=data)
    return response

# PATCH requests
def patch_api_data(endpoint, data):
    response = session.patch(f'{base_url}{endpoint}', json=data)
    return response

import requests
from requests.exceptions import RequestException
import json

url_get = "https://jsonplaceholder.typicode.com/posts/1"
url_post = "https://jsonplaceholder.typicode.com/posts"
nuevo_post = {"title": "Aprender Python", "body": "Contenido", "userId": 1}

print("MÉTODO GET")
try:
    resp = requests.get(url_get, timeout=10)
    resp.raise_for_status()
    content = resp.json()
    print(f"\nCódigo: {resp.status_code}")
    print(f"\nDatos: {json.dumps(content, indent=4, sort_keys=True)}")
    # Headers añadidos
    print(f"\nHeaders: {json.dumps(dict(resp.headers), indent=4)}")
except RequestException as e:
    print(f"\nError GET: {e}")

print("\n\n\nMÉTODO POST:")
try:
    resp = requests.post(url_post, json=nuevo_post, timeout=10)
    resp.raise_for_status()
    print(f"\nCódigo: {resp.status_code}")
    print(f"\nPost creado: {json.dumps(resp.json(), indent=4)}")
    # Headers añadidos
    print(f"\nHeaders: {json.dumps(dict(resp.headers), indent=4)}")
except RequestException as e:
    print(f"\nError POST: {e}")
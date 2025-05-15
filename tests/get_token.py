
import requests

def get_token():
    response = requests.post("http://localhost:17000/auth", json={
        'username': 'fatima20',
        'password': 'hola123'
    })
    if response.status_code != 200:
        raise Exception("No se pudo obtener el token de autenticación")
    return response.json().get('token')
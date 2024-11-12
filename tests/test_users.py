import unittest as U
import requests as R

class AxoBackendTestCase(U.TestCase):
    token = None

    @staticmethod
    def _post_request(url, json_data=None, headers=None):
        try:
            response = R.post(url, json=json_data, headers=headers)
            response.raise_for_status()
            return response
        except R.exceptions.RequestException as e:
            print(f"Error en la solicitud: {e}")
            raise

    def test_login(self):
        response = self._post_request("http://localhost:17000/auth", json_data={
            "username": "prueba1", 
            "password": "hola123",
            "grant_type": "password"
        })

        token_data = response.json()
        self.assertIn("token", token_data)
        AxoBackendTestCase.token = token_data["token"]
        self.assertIsNotNone(AxoBackendTestCase.token)

    def test_validate_token(self):
        if not AxoBackendTestCase.token:
            self.fail("Token no obtenido, ejecutar 'test_login' primero")

        response = self._post_request("http://localhost:17000/auth/validate-token", headers={
            "Authorization": f"Bearer {AxoBackendTestCase.token}"
        })

        self.assertIn(response.status_code, [200, 204])

    def test_register_user(self):
        user_data = {
            "user": {
                "username": "newuser",
                "email": "newuser@gmail.com",
                "first_name": "prueba",
                "last_name": "register"
            },
            "credentials": {
                "password": "hola123"
            }
        }

        response = self._post_request("http://localhost:17000/auth/signup", json_data=user_data)
        self.assertEqual(response.status_code, 204)

if __name__ == "__main__":
    U.main()

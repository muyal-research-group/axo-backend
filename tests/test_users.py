
import unittest as U
import requests as R

class AxoBackendTestCase(U.TestCase):
    token = None
    
    @staticmethod
    def _post_request(url, json_data=None, headers=None):
        return R.post(url, json=json_data, headers=headers)
    
    def test_login(self):
        response = self._post_request("http://localhost:17000/auth", json_data={
            "username": "fatima20", 
            "password": "hola123",
            "grant_type": "password"
        })
        
        print(response.text)  

        token_data = response.json()
        self.assertIn("token", token_data)
        AxoBackendTestCase.token = token_data["token"]
        self.assertIsNotNone(AxoBackendTestCase.token)
        
        self.assertTrue(response.ok)
    
    def test_validate_token(self):
        if not AxoBackendTestCase.token:
            self.fail("Token not obtained, run 'test_login' first")

        response = self._post_request("http://localhost:17000/auth/validate-token", headers={
            "Authorization": f"Bearer {AxoBackendTestCase.token}"
        })
        self.assertIn(response.status_code, [200, 204])
        print(response)
        self.assertTrue(response.ok)
    
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
            print(response)
            self.assertTrue(response.ok)

if __name__ == "__main__":
    U.main()

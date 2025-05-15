import unittest as U
import requests as R

class UsersTest(U.TestCase):

    def _post_request(self, url, json_data=None, headers=None):
        try:
            response = R.post(url, json=json_data, headers=headers)
            response.raise_for_status()
            return response
        except R.exceptions.RequestException as e:
            print(f"Error in request: {e}")
            raise

    # @U.skip("")
    def _get_token(self):
        response = self._post_request("http://localhost:17000/auth", json_data={
            "username": "fatima20", 
            "password": "hola123",
            "grant_type": "password"
        })
        token_data = response.json()
        return token_data.get("token")

    # @U.skip("")
    def test_login(self):
        token = self._get_token()
        print(token)
        self.assertIsNotNone(token, "Failed to get token")

    # @U.skip("")
    def test_validate_token(self):
        token = self._get_token() 
        response = self._post_request("http://localhost:17000/auth/validate-token", headers={
            "Authorization": f"Bearer {token}"
        })
        self.assertIn(response.status_code, [200, 204])

    @U.skip("YOU MUST EXECUTE THIS TEST FIRST.")
    def test_register_user(self):
        user_data = {
            "user": {
                "username": "fatima20",
                "email": "fatima20@gmail.com",
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

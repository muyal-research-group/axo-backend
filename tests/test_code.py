import unittest as U
import requests as R
from tests.get_token import get_token

class CodeTestCase(U.TestCase):
    BASE_URL = "http://localhost:17000/code"
    code_id = None

    @classmethod
    def setUp(cls):
        cls.token = get_token()
        cls.headers = {
            'Authorization': f'Bearer {cls.token}',
            'Content-Type': 'application/json'
        }
        if not cls.code_id:
            response = R.post(cls.BASE_URL, headers=cls.headers, json={
            "code": "string",
            "axo_id": "",
            })
            if response.status_code == 200:
                cls.code_id = response.json().get('code_id')

    def test_0_create_code(self):
        response = R.post(self.BASE_URL, headers=self.headers, json={
        "code": "string",
        "axo_id": "",
        })
        self.assertEqual(response.status_code, 200)
        self.code_id = response.json().get('code_id')
        self.assertIsNotNone(self.code_id)

    def test_1_get_all_codes(self):
        response = R.get(self.BASE_URL, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        codes = response.json().get('code')
        self.assertIsInstance(codes, list)
        self.assertGreater(len(codes), 0)

    def test_2_get_code_by_id(self):
        self.assertIsNotNone(self.code_id)
        response = R.get(f"{self.BASE_URL}/{self.code_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        code = response.json().get('code')
        self.assertIsNotNone(code)

    def test_3_update_code(self):
        self.assertIsNotNone(self.code_id)
        response = R.put(f"{self.BASE_URL}/{self.code_id}", headers=self.headers, json={
                "code": "updated",
                "axo_id": "",})
        self.assertEqual(response.status_code, 200)

    def test_4_delete_code(self):
        self.assertIsNotNone(self.code_id)
        response = R.delete(f"{self.BASE_URL}/{self.code_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_check = R.get(f"{self.BASE_URL}/{self.code_id}", headers=self.headers)
        self.assertEqual(response_check.status_code, 403)

if __name__ == "__main__":
    U.main()

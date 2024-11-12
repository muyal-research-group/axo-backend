import unittest as U
import requests as R
from tests.get_token import get_token

class ResultsTestCase(U.TestCase):
    BASE_URL = "http://localhost:17000/results"
    result_id = None

    @classmethod
    def setUp(cls):
        cls.token = get_token()
        cls.headers = {
            'Authorization': f'Bearer {cls.token}',
            'Content-Type': 'application/json'
        }
        if not cls.result_id:
            response = R.post(cls.BASE_URL, headers=cls.headers, json={
                "axos_id": "",
                "hash": ""
            })
            if response.status_code == 200:
                cls.result_id = response.json().get('result_id')

    def test_0_create_result(self):
        response = R.post(self.BASE_URL, headers=self.headers, json={
                "axos_id": "",
                "hash": ""
        })
        self.assertEqual(response.status_code, 200)
        self.result_id = response.json().get('result_id')
        self.assertIsNotNone(self.result_id)

    def test_1_get_results(self):
        response = R.get(self.BASE_URL, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results')
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_2_get_result_by_id(self):
        self.assertIsNotNone(self.result_id)
        response = R.get(f"{self.BASE_URL}/{self.result_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        result = response.json().get('result')
        self.assertIsNotNone(result)

    def test_3_update_result(self):
        self.assertIsNotNone(self.result_id)
        response = R.put(f"{self.BASE_URL}/{self.result_id}", headers=self.headers, json={
                "axos_id": "1",
                "hash": "1"})
        self.assertEqual(response.status_code, 200)

    def test_4_delete_result(self):
        self.assertIsNotNone(self.result_id)
        response = R.delete(f"{self.BASE_URL}/{self.result_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_check = R.get(f"{self.BASE_URL}/{self.result_id}", headers=self.headers)
        self.assertEqual(response_check.status_code, 403)

if __name__ == "__main__":
    U.main()

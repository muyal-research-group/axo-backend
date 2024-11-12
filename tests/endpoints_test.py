import unittest as U
import requests as R
from tests.get_token import get_token

class EndpointsTest(U.TestCase):
    BASE_URL = "http://localhost:17000/endpoints"
    e_id = None
    
    def setUp(self):
        self.token = get_token()
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        if not self.e_id:
            response = R.post(f"{self.BASE_URL}", headers=self.headers, json={
                "ve_id": "",
                "cpu": "4",
                "memory": "32"
            })
            if response.status_code == 200:
                response_data = response.json()
                if isinstance(response_data, list):
                    response_data = response_data[0]
                if isinstance(response_data, dict):
                    self.e_id = response_data.get('e_id')

    def test_0_create_endpoint(self):
        response = R.post(f"{self.BASE_URL}", headers=self.headers, json={
            "ve_id": "",
            "cpu": "2",
            "memory": "8"
        })
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        if isinstance(response_data, list):
            response_data = response_data[0]
        if isinstance(response_data, dict):
            self.e_id = response_data.get('e_id')
            self.assertIsNotNone(self.e_id)

    def test_1_get_endpoints(self):
        response = R.get(f"{self.BASE_URL}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertIsInstance(response_data.get('endpoints'), list)
        self.assertGreater(len(response_data.get('endpoints', [])), 0)

    def test_2_get_endpoint_by_id(self):
        if self.e_id is None:
            response = R.post(f"{self.BASE_URL}", headers=self.headers, json={
                "ve_id": "",
                "cpu": "4",
                "memory": "32"
            })
            response_data = response.json()
            self.assertEqual(response.status_code, 200)
            self.e_id = response_data[0].get('e_id')
        
        self.assertIsNotNone(self.e_id)
        response = R.get(f"{self.BASE_URL}/{self.e_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_3_update_endpoint(self):
        self.assertIsNotNone(self.e_id)
        response = R.put(f"{self.BASE_URL}/{self.e_id}", headers=self.headers, json={
            "cpu": "8",
            "memory": "32"
        })
        self.assertEqual(response.status_code, 200)

    def test_4_delete_endpoint(self):
        self.assertIsNotNone(self.e_id)
        response = R.delete(f"{self.BASE_URL}/{self.e_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        response_check = R.get(f"{self.BASE_URL}/{self.e_id}", headers=self.headers)
        self.assertEqual(response_check.status_code, 403)

if __name__ == "__main__":
    U.main()

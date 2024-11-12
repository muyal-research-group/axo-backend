import unittest as U
import requests as R
from tests.get_token import get_token

class EnvironmentsTest(U.TestCase):
    BASE_URL = "http://localhost:17000/virtual-environments"
    ve_id = None
    
    def setUp(self):
        self.token = get_token()
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        if not self.ve_id:
            response = R.post(f"{self.BASE_URL}", headers=self.headers, json={
                "name": "new_virtual_environment",
                "cpu": "2",
                "memory": "8"
            })
            response_data = response.json()
            if isinstance(response_data, list):
                response_data = response_data[0]
                if isinstance(response_data, dict):
                    self.ve_id = response_data.get('ve_id')

    def test_0_create_virtual_environment(self):
        response = R.post(f"{self.BASE_URL}", headers=self.headers, json={
            "name": "new_virtual_environment",
            "cpu": "2",
            "memory": "16"
        })
        
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        
        if isinstance(response_data, list):
            response_data = response_data[0]
            if isinstance(response_data, dict):
                self.ve_id = response_data.get('ve_id')
                self.assertIsNotNone(self.ve_id)

    def test_1_get_virtual_environments(self):
        response = R.get(f"{self.BASE_URL}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertIsInstance(response_data.get('environments'), list)
        self.assertGreater(len(response_data.get('environments', [])), 0)

    def test_2_get_virtual_environment_by_id(self):
        self.assertIsNotNone(self.ve_id)
        response = R.get(f"{self.BASE_URL}/{self.ve_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_3_update_virtual_environment(self):
        self.assertIsNotNone(self.ve_id)
        response = R.put(f"{self.BASE_URL}/{self.ve_id}", headers=self.headers, json={
            "name": "updated_virtual_environment",
            "cpu": "8",
            "memory": "32"
        })
        self.assertEqual(response.status_code, 200)

    def test_4_delete_virtual_environment(self):
        self.assertIsNotNone(self.ve_id)
        response = R.delete(f"{self.BASE_URL}/{self.ve_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        response_check = R.get(f"{self.BASE_URL}/{self.ve_id}", headers=self.headers)
        self.assertEqual(response_check.status_code, 403)

if __name__ == "__main__":
    U.main()

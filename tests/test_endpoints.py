import unittest as U
import requests as R
from tests.get_token import get_token

class EndpointsTestCase(U.TestCase):
    BASE_URL = "http://localhost:17000/endpoints"
    e_id = None
    
    @classmethod
    def setUp(cls):
        cls.token = get_token()
        cls.headers = {
            'Authorization': f'Bearer {cls.token}',
            'Content-Type': 'application/json'
        }

        # Crear un endpoint solo si e_id es None
        if not cls.e_id:
            response = R.post(f"{cls.BASE_URL}", headers=cls.headers, json={
                "ve_id": "",
                "cpu": "4",
                "memory": "32"
            })
            if response.status_code == 200:
                response_data = response.json()
                if isinstance(response_data, list):
                    response_data = response_data[0]
                if isinstance(response_data, dict):
                    cls.e_id = response_data.get('e_id')

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
            self.assertIsNotNone(self.e_id, "El ID del endpoint no debería ser None")

    def test_1_get_endpoints(self):
        response = R.get(f"{self.BASE_URL}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertIsInstance(response_data.get('endpoints'), list)
        self.assertGreater(len(response_data.get('endpoints', [])), 0, "Debe haber al menos un endpoint")

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
        
        self.assertIsNotNone(self.e_id, "El ID del endpoint no debería ser None")
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

import unittest as U
import requests as R
from tests.get_token import get_token

class AxoObjectsTestCase(U.TestCase):
    BASE_URL = "http://localhost:17000/axo-objects"
    axo_id = None

    @classmethod
    def setUp(cls):
        cls.token = get_token()
        cls.headers = {
            'Authorization': f'Bearer {cls.token}',
            'Content-Type': 'application/json'
        }
        if not cls.axo_id:
            response = R.post(cls.BASE_URL, headers=cls.headers, json={"code_id": ""})
            if response.status_code == 200:
                cls.axo_id = response.json().get('axo_id')

    def test_0_create_object(self):
        response = R.post(self.BASE_URL, headers=self.headers, json={"code_id": ""})
        self.assertEqual(response.status_code, 200)
        self.axo_id = response.json().get('axo_id')
        self.assertIsNotNone(self.axo_id, "El ID del objeto no debería ser None")

    def test_1_get_objects(self):
        response = R.get(self.BASE_URL, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        objects = response.json().get('axo objects')
        self.assertIsInstance(objects, list)
        self.assertGreater(len(objects), 0, "Debe haber al menos un objeto")

    def test_2_get_object_by_id(self):
        self.assertIsNotNone(self.axo_id)
        response = R.get(f"{self.BASE_URL}/{self.axo_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_3_update_object(self):
        self.assertIsNotNone(self.axo_id)
        response = R.put(f"{self.BASE_URL}/{self.axo_id}", headers=self.headers, json={"code_id": "1"})
        self.assertEqual(response.status_code, 200)

    def test_4_delete_object(self):
        self.assertIsNotNone(self.axo_id)
        response = R.delete(f"{self.BASE_URL}/{self.axo_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_check = R.get(f"{self.BASE_URL}/{self.axo_id}", headers=self.headers)
        self.assertEqual(response_check.status_code, 403)

if __name__ == "__main__":
    U.main()

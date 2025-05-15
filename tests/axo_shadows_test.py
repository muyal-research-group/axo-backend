import unittest as U
import requests as R
from tests.get_token import get_token

class AxoShadowsTest(U.TestCase):
    BASE_URL = "http://localhost:17000/axo-object-shadows"
    axos_id = None

    def setUp(self):
        self.token = get_token()
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        if not self.axos_id:
            response = R.post(self.BASE_URL, headers=self.headers, json={"e_id": "","axo_id": "", "ve_id": "",})
            if response.status_code == 200:
                self.axos_id = response.json().get('axos_id')

    def test_0_create_shadow(self):
        response = R.post(self.BASE_URL, headers=self.headers, json={"e_id": "","axo_id": "", "ve_id": "",})
        self.assertEqual(response.status_code, 200)
        self.axos_id = response.json().get('axos_id')
        self.assertIsNotNone(self.axos_id)

    def test_1_get_shadows(self):
        response = R.get(self.BASE_URL, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        shadows = response.json().get('axo object shadows')
        self.assertIsInstance(shadows, list)
        self.assertGreater(len(shadows), 0)

    def test_2_get_shadow_by_id(self):
        self.assertIsNotNone(self.axos_id)
        response = R.get(f"{self.BASE_URL}/{self.axos_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_3_update_shadow(self):
        self.assertIsNotNone(self.axos_id)
        response = R.put(f"{self.BASE_URL}/{self.axos_id}", headers=self.headers, json={"e_id": "1","axo_id": "1", "ve_id": "1",})
        self.assertEqual(response.status_code, 200)

    def test_4_delete_shadow(self):
        self.assertIsNotNone(self.axos_id)
        response = R.delete(f"{self.BASE_URL}/{self.axos_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_check = R.get(f"{self.BASE_URL}/{self.axos_id}", headers=self.headers)
        self.assertEqual(response_check.status_code, 403)

if __name__ == "__main__":
    U.main()

import unittest as U
import requests as R
from tests.get_token import get_token

class AxosObjectShadowsTestCase(U.TestCase):
    BASE_URL = "http://localhost:17000/axo-object-shadows"
    axos_id = None

    @classmethod
    def setUp(cls):
        cls.token = get_token()
        cls.headers = {
            'Authorization': f'Bearer {cls.token}',
            'Content-Type': 'application/json'
        }
        # Crear un Axos Object Shadow solo si axos_id es None
        if not cls.axos_id:
            response = R.post(cls.BASE_URL, headers=cls.headers, json={"e_id": "","axo_id": "", "ve_id": "",})
            if response.status_code == 200:
                cls.axos_id = response.json().get('axos_id')

    def test_0_create_shadow(self):
        response = R.post(self.BASE_URL, headers=self.headers, json={"e_id": "","axo_id": "", "ve_id": "",})
        self.assertEqual(response.status_code, 200)
        self.axos_id = response.json().get('axos_id')
        self.assertIsNotNone(self.axos_id, "El ID del shadow no debería ser None")

    def test_1_get_shadows(self):
        response = R.get(self.BASE_URL, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        shadows = response.json().get('axo object shadows')
        self.assertIsInstance(shadows, list)
        self.assertGreater(len(shadows), 0, "Debe haber al menos un shadow")

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

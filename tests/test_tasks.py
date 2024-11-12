import unittest as U
import requests as R
from tests.get_token import get_token

class TasksTestCase(U.TestCase):
    BASE_URL = "http://localhost:17000/tasks"
    task_id = None

    @classmethod
    def setUp(cls):
        cls.token = get_token()
        cls.headers = {
            'Authorization': f'Bearer {cls.token}',
            'Content-Type': 'application/json'
        }
        if not cls.task_id:
            response = R.post(cls.BASE_URL, headers=cls.headers, json={"axos_id": "","source_bucket_id": "", "sink_bucket_id": "",})
            if response.status_code == 200:
                cls.task_id = response.json().get('task_id')

    def test_0_create_task(self):
        response = R.post(self.BASE_URL, headers=self.headers, json={"axos_id": "","source_bucket_id": "","sink_bucket_id": "",})
        self.assertEqual(response.status_code, 200)
        self.task_id = response.json().get('task_id')
        self.assertIsNotNone(self.task_id, "El ID del task no debería ser None")

    def test_1_get_tasks(self):
        response = R.get(self.BASE_URL, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        tasks = response.json().get('tasks')
        self.assertIsInstance(tasks, list)
        self.assertGreater(len(tasks), 0)

    def test_2_get_task_by_id(self):
        self.assertIsNotNone(self.task_id)
        response = R.get(f"{self.BASE_URL}/{self.task_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        

    def test_3_update_task(self):
        self.assertIsNotNone(self.task_id)
        response = R.put(f"{self.BASE_URL}/{self.task_id}", headers=self.headers, json={
"axos_id": "1",
"source_bucket_id": "1",
"sink_bucket_id": "1"})
        self.assertEqual(response.status_code, 200)

    def test_4_delete_task(self):
        self.assertIsNotNone(self.task_id)
        response = R.delete(f"{self.BASE_URL}/{self.task_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_check = R.get(f"{self.BASE_URL}/{self.task_id}", headers=self.headers)
        self.assertEqual(response_check.status_code, 403)

if __name__ == "__main__":
    U.main()

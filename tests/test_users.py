import unittest as U
import requests as R
class AxoBackendTestCase(U.TestCase):
    
    def test_login(self):
        response = R.post("http://localhost:17000/auth",json={
              "username":"fatimacm", 
              "password":"fatima123",
        })
        print(response)
        return self.assertTrue(response.ok)
    
if __name__ =="__main__":
    U.main()
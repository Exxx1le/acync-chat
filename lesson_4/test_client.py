import unittest
import re
from client import create_presence_message, send_message



class TestClient(unittest.TestCase):
    def test_create_presence_message(self):
        expected_message = {
            "action": "presence",
            "type": "status",
            "user": {
                "account_name": "my_username",
                "status": "Online"
            }
        }
        self.assertEqual(create_presence_message(), expected_message)

    def test_for_response(self):
        self.assertNotEqual(send_message, "В соединеннии отказано")


if __name__ == '__main__':
    unittest.main()

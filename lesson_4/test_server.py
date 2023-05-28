import unittest
from server import start_server

class TestServer(unittest.TestCase):
    def test_start_server(self):
        server_socket = start_server("0.0.0.0", 7777)
        self.assertIsNotNone(server_socket)
 

if __name__ == '__main__':
    unittest.main()

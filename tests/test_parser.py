from datetime import datetime
import unittest
from parser import Parser


class ParserTest(unittest.TestCase):
    def test_correct_parsing(self):
        complete_resource_url = '127.0.0.1 - james [09/May/2018:16:00:39 +0000] "GET /report/user HTTP/1.0" 200 123'
        self.assertEqual(Parser.parse_log_line(complete_resource_url), {
            "host": "127.0.0.1",
            "remote_user": "-",
            "auth_user": "james",
            "date": datetime.strptime("09/May/2018:16:00:39 +0000", '%d/%b/%Y:%H:%M:%S %z'),
            "method": "GET",
            "url": "/report/user",
            "section": "/report",
            "http_version": "HTTP/1.0",
            "status": 200,
            "bytes": 123,
        })

        empty_resource_url = '127.0.0.1 - james [09/May/2018:16:00:39 +0000] "GET /report HTTP/1.0" 200 123'
        self.assertEqual(Parser.parse_log_line(empty_resource_url), {
            "host": "127.0.0.1",
            "remote_user": "-",
            "auth_user": "james",
            "date": datetime.strptime("09/May/2018:16:00:39 +0000", '%d/%b/%Y:%H:%M:%S %z'),
            "method": "GET",
            "url": "/report",
            "section": "/report",
            "http_version": "HTTP/1.0",
            "status": 200,
            "bytes": 123,
        })

    def test_invalid_parsing(self):
        line = 'Invalid line'
        parsed_line = Parser.parse_log_line(line)
        self.assertEqual(parsed_line, None)


if __name__ == '__main__':
    unittest.main()

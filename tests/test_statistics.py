import unittest
import re
from statistics import Statistics
from parser import Parser


class StatisticsTest(unittest.TestCase):
    def setUp(self):
        self.statistics = Statistics()

    def test_queue_data_succes(self):
        # Setup
        valid_data = '127.0.0.1 - james [09/May/2018:16:00:39 +0000] "GET /report/user HTTP/1.0" 200 123'

        # Precheck
        self.assertEqual(len(self.statistics.activity_queue), 0)
        self.assertEqual(self.statistics.traffic_monitor_counter, 0)

        # Update
        self.statistics.queue_data(valid_data)

        # Postcheck
        self.assertEqual(len(self.statistics.activity_queue), 1)
        self.assertEqual(self.statistics.traffic_monitor_counter, 1)

    def test_queue_data_failure(self):
            # Setup
        invalid_data = 'Invalid data'

        # Precheck
        self.assertEqual(len(self.statistics.activity_queue), 0)
        self.assertEqual(self.statistics.traffic_monitor_counter, 0)

        # Update
        self.statistics.queue_data(invalid_data)

        # Postcheck
        self.assertEqual(len(self.statistics.activity_queue), 0)
        self.assertEqual(self.statistics.traffic_monitor_counter, 0)

    def test_alert_traffic_trigger(self):
        # Setup
        self.statistics.traffic_monitor_counter = 10000

        # Precheck
        self.assertEqual(len(self.statistics.alert_logs), 0)

        # Update
        self.statistics.update_traffic_alert_status()

        # Postcheck
        self.assertTrue(self.statistics.is_alert_on)
        self.assertEqual(len(self.statistics.alert_logs), 1)
        self.assertRegex(
            self.statistics.alert_logs[-1],
            "High traffic - (.*) hits - Triggered at (.*)"
        )
        self.assertEqual(self.statistics.traffic_monitor_counter, 0)

    def test_alert_traffic_recovery(self):
        # Setup
        self.statistics.is_alert_on = True
        self.statistics.traffic_monitor_counter = 1

        # Precheck
        self.assertEqual(len(self.statistics.alert_logs), 0)

        # Update
        self.statistics.update_traffic_alert_status()

        # Postcheck
        self.assertFalse(self.statistics.is_alert_on)
        self.assertEqual(len(self.statistics.alert_logs), 1)
        self.assertRegex(
            self.statistics.alert_logs[-1],
            "Normal traffic - (.*) hits - Recovered at (.*)"
        )
        self.assertEqual(self.statistics.traffic_monitor_counter, 0)

    def test_alert_error_trigger(self):
        # Setup
        self.statistics.errors_monitor_counter = 10000

        # Precheck
        self.assertEqual(len(self.statistics.alert_logs), 0)

        # Update
        self.statistics.update_error_alert_status()

        # Postcheck
        self.assertEqual(len(self.statistics.alert_logs), 1)
        self.assertRegex(
            self.statistics.alert_logs[-1],
            "Too many errors - Errors: (.*) - Triggered at (.*)"
        )
        self.assertEqual(self.statistics.errors_monitor_counter, 0)

    def test_alert_normal_activity(self):
            # Setup
        self.statistics.is_alert_on = False
        self.statistics.traffic_monitor_counter = 0

        # Precheck
        self.assertEqual(len(self.statistics.alert_logs), 0)

        # Update
        self.statistics.update_traffic_alert_status()

        # Postcheck
        self.assertFalse(self.statistics.is_alert_on)
        self.assertEqual(len(self.statistics.alert_logs), 0)
        self.assertEqual(self.statistics.traffic_monitor_counter, 0)

    def test_update_activity_statistics(self):
        # Setup
        parsed_line_1 = Parser.parse_log_line(
            '127.0.0.1 - james [09/May/2018:16:00:39 +0000] "GET /report HTTP/1.0" 200 123')
        parsed_line_2 = Parser.parse_log_line(
            '127.0.0.1 - jill [09/May/2018:16:00:41 +0000] "GET /api/event HTTP/1.0" 200 234')
        parsed_line_3 = Parser.parse_log_line(
            '127.0.0.1 - frank [09/May/2018:16:00:42 +0000] "POST /api/user/profile HTTP/1.0" 400 34')
        parsed_line_4 = Parser.parse_log_line(
            '127.0.0.1 - mary [09/May/2018:16:00:42 +0000] "POST /api/user HTTP/1.0" 503 12')
        self.statistics.activity_queue = [
            parsed_line_1,
            parsed_line_2,
            parsed_line_3,
            parsed_line_4,
        ]

        # Precheck
        self.assertEqual(len(self.statistics.activity_queue), 4)
        self.assertEqual(self.statistics.section_activity, {})

        # Update
        self.statistics.update_activity_statistics()

        # Postcheck
        self.assertDictEqual(
            self.statistics.section_activity,
            {
                '/report': {
                    'errors_count': 0,
                    'heaviest_request': 123,
                    'hits': 1,
                    'section': '/report',
                },
                '/api': {
                    'errors_count': 2,
                    'heaviest_request': 234,
                    'hits': 3,
                    'section': '/api',
                }
            }
        )
        self.assertEqual(len(self.statistics.activity_queue), 0)

    def test_get_sorted_section_activity(self):
        # Setup
        self.statistics.section_activity = {
            '/report': {
                'errors_count': 0,
                'heaviest_request': 123,
                'hits': 1,
                'section': '/report',
            },
            '/user': {
                'errors_count': 4,
                'heaviest_request': 456,
                'hits': 4,
                'section': '/api',
            },
            '/api': {
                'errors_count': 2,
                'heaviest_request': 234,
                'hits': 3,
                'section': '/api',
            },
            '/event': {
                'errors_count': 2,
                'heaviest_request': 234,
                'hits': 2,
                'section': '/api',
            },
        }

        # Check
        self.assertListEqual(
            self.statistics.get_sorted_section_activity(),
            [
                {
                    'errors_count': 4,
                    'heaviest_request': 456,
                    'hits': 4,
                    'section': '/api',
                },
                {
                    'errors_count': 2,
                    'heaviest_request': 234,
                    'hits': 3,
                    'section': '/api',
                },
                {
                    'errors_count': 2,
                    'heaviest_request': 234,
                    'hits': 2,
                    'section': '/api',
                },
                {
                    'errors_count': 0,
                    'heaviest_request': 123,
                    'hits': 1,
                    'section': '/report',
                },
            ]
        )


if __name__ == '__main__':
    unittest.main()

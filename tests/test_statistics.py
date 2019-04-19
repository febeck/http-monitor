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
        valid_data = '127.0.0.1 - john [09/May/2018:16:00:39 +0000] "GET /report/user HTTP/1.0" 200 123'
        valid_data_error_status = '127.0.0.1 - james [09/May/2018:16:00:39 +0000] "GET /stats/user HTTP/1.0" 500 123'

        # Precheck
        self.assertEqual(len(self.statistics.section_activity), 0)
        self.assertEqual(
            self.statistics.traffic_monitor.count_elements(), 0)
        self.assertEqual(
            self.statistics.errors_monitor.count_elements(), 0)

        # Update
        self.statistics.queue_data(valid_data)
        self.statistics.queue_data(valid_data_error_status)

        # Postcheck
        # Section activity has 2 entries because logs concern 2 section (/report and /stats)
        self.assertEqual(len(self.statistics.section_activity), 2)
        self.assertEqual(
            self.statistics.traffic_monitor.count_elements(), 2)
        self.assertEqual(
            self.statistics.errors_monitor.count_elements(), 1)

    def test_queue_data_failure(self):
            # Setup
        invalid_data = 'Invalid data'

        # Precheck
        self.assertEqual(len(self.statistics.section_activity), 0)
        self.assertEqual(
            self.statistics.traffic_monitor.count_elements(), 0)
        self.assertEqual(
            self.statistics.errors_monitor.count_elements(), 0)

        # Update
        self.statistics.queue_data(invalid_data)

        # Postcheck
        self.assertEqual(len(self.statistics.section_activity), 0)
        self.assertEqual(
            self.statistics.traffic_monitor.count_elements(), 0)
        self.assertEqual(
            self.statistics.errors_monitor.count_elements(), 0)

    def test_alert_traffic_trigger(self):
        # Setup
        for i in range(1, 10000):
            self.statistics.traffic_monitor.push()

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

    def test_alert_traffic_recovery(self):
        # Setup
        self.statistics.is_alert_on = True
        self.statistics.traffic_monitor.push()

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

    def test_alert_error_trigger(self):
        # Setup
        for i in range(1, 10000):
            self.statistics.errors_monitor.push()

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

    def test_alert_normal_activity(self):
            # Setup
        self.statistics.is_alert_on = False

        # Precheck
        self.assertEqual(len(self.statistics.alert_logs), 0)

        # Update
        self.statistics.update_traffic_alert_status()

        # Postcheck
        self.assertFalse(self.statistics.is_alert_on)
        self.assertEqual(len(self.statistics.alert_logs), 0)

    def test_update_section_activity_existing_section(self):
        # Setup
        self.statistics.section_activity = {
            '/report': {
                'errors_count': 0,
                'heaviest_request': 123,
                'hits': 1,
                'section': '/report',
            },
            '/api': {
                'errors_count': 2,
                'heaviest_request': 234,
                'hits': 1,
                'section': '/api',
            }
        }
        parsed_line = Parser.parse_log_line(
            '127.0.0.1 - james [09/May/2018:16:00:39 +0000] "GET /report HTTP/1.0" 500 999')

        # Precheck
        self.assertEqual(len(self.statistics.section_activity), 2)

        # Update
        self.statistics.update_activity_statistics(parsed_line)

        # Postcheck
        self.assertDictEqual(
            self.statistics.section_activity,
            {
                '/report': {
                    'errors_count': 1,
                    'heaviest_request': 999,
                    'hits': 2,
                    'section': '/report',
                },
                '/api': {
                    'errors_count': 2,
                    'heaviest_request': 234,
                    'hits': 1,
                    'section': '/api',
                }
            }
        )
        self.assertEqual(len(self.statistics.section_activity), 2)

    def test_update_section_activity_new_section(self):
        # Setup
        self.statistics.section_activity = {
            '/api': {
                'errors_count': 2,
                'heaviest_request': 234,
                'hits': 1,
                'section': '/api',
            }
        }
        parsed_line = Parser.parse_log_line(
            '127.0.0.1 - james [09/May/2018:16:00:39 +0000] "GET /report HTTP/1.0" 500 999')

        # Precheck
        self.assertEqual(len(self.statistics.section_activity), 1)

        # Update
        self.statistics.update_activity_statistics(parsed_line)

        # Postcheck
        self.assertDictEqual(
            self.statistics.section_activity,
            {
                '/report': {
                    'errors_count': 1,
                    'heaviest_request': 999,
                    'hits': 1,
                    'section': '/report',
                },
                '/api': {
                    'errors_count': 2,
                    'heaviest_request': 234,
                    'hits': 1,
                    'section': '/api',
                }
            }
        )
        self.assertEqual(len(self.statistics.section_activity), 2)

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

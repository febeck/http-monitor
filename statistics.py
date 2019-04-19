from datetime import datetime
from operator import itemgetter
from config import config
from parser import Parser
from sliding_window import SlidingWindow


class Statistics:

    def __init__(self):
        self.activity_queue = []
        self.alert_logs = []
        self.is_alert_on = False
        self.section_activity = {}
        self.traffic_monitor = SlidingWindow(
            config['TRAFFIC_ALERT_TIME_WINDOW'])
        self.errors_monitor_counter = 0

    def queue_data(self, data):
        parsed_data = Parser.parse_log_line(data)
        if(parsed_data is not None):
            if parsed_data['status'] >= 400:
                self.errors_monitor_counter += 1
            self.traffic_monitor.push()
            self.activity_queue.append(parsed_data)

    def update_traffic_alert_status(self):
        self.traffic_monitor.update()
        alert_monitor_items_count = self.traffic_monitor.count_elements()
        average_traffic = alert_monitor_items_count / \
            config.get('TRAFFIC_ALERT_TIME_WINDOW')
        if(average_traffic > config.get('AVERAGE_TRAFFIC_TRESHOLD')):
            self.is_alert_on = True
            self.alert_logs.append(
                "High traffic - {} hits - Triggered at {}".format(
                    alert_monitor_items_count,
                    datetime.now()
                )
            )
        if (average_traffic < config.get('AVERAGE_TRAFFIC_TRESHOLD') and self.is_alert_on):
            self.is_alert_on = False
            self.alert_logs.append(
                "Normal traffic - {} hits - Recovered at {}".format(
                    alert_monitor_items_count,
                    datetime.now()
                )
            )

    def update_error_alert_status(self):
        max_error = self.errors_monitor_counter / \
            config.get('ERRORS_ALERT_INTERVAL')
        if(max_error > config.get('MAX_ERRORS_TRESHOLD')):
            self.alert_logs.append(
                "Too many errors - Errors: {} - Triggered at {}".format(
                    max_error,
                    datetime.now()
                )
            )
        self.errors_monitor_counter = 0

    def update_activity_statistics(self):
        self.section_activity = {}
        for data in self.activity_queue:
            section = self.section_activity.get(data['section'], {
                'errors_count': 0,
                'heaviest_request': 0,
                'hits': 0,
                'section': data['section'],
            })
            updated_section = {
                'errors_count': section['errors_count'] + 1 if data['status'] >= 400 else section['errors_count'],
                'heaviest_request': data['bytes'] if data['bytes'] > section['heaviest_request'] else section['heaviest_request'],
                'hits': section['hits'] + 1,
                'section': data['section'],
            }
            self.section_activity[data['section']] = updated_section
        self.activity_queue = []

    def get_sorted_section_activity(self):
        return sorted(
            list(self.section_activity.values()),
            key=itemgetter('hits'),
            reverse=True
        )

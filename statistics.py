from datetime import datetime
from operator import itemgetter
from config import config
from parser import Parser
from sliding_window import SlidingWindow


class Statistics:

    def __init__(self):
        self.alert_logs = []
        self.is_alert_on = False
        self.section_activity = {}
        self.traffic_monitor = SlidingWindow(
            config['TRAFFIC_ALERT_TIME_WINDOW'])
        self.errors_monitor = SlidingWindow(
            config['ERRORS_ALERT_TIME_WINDOW'])

    def queue_data(self, data):
        parsed_data = Parser.parse_log_line(data)
        if(parsed_data is not None):
            if parsed_data['status'] >= 400:
                self.errors_monitor.push()
            self.traffic_monitor.push()
            self.update_activity_statistics(parsed_data)

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
        self.errors_monitor.update()
        errors_monitor_items_count = self.errors_monitor.count_elements()
        max_error = errors_monitor_items_count / \
            config.get('ERRORS_ALERT_TIME_WINDOW')
        if(max_error > config.get('MAX_ERRORS_TRESHOLD')):
            self.alert_logs.append(
                "Too many errors - Errors: {} - Triggered at {}".format(
                    errors_monitor_items_count,
                    datetime.now()
                )
            )

    def update_activity_statistics(self, data):
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

    def clean_section_activity(self):
        self.section_activity = {}

    def get_sorted_section_activity(self):
        return sorted(
            list(self.section_activity.values()),
            key=itemgetter('hits'),
            reverse=True
        )

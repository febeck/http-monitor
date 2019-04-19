import threading
from config import config


class Scheduler(threading.Thread):

    def __init__(self, interval, event, callback):
        threading.Thread.__init__(self)
        self.stopped = event

        self.interval = interval
        self.callback = callback

    def run(self):
        while not self.stopped.wait(self.interval):
            self.callback()


class UpdatesScheduler:
    def __init__(self, statistics):
        self.stop_event = threading.Event()

        self.statistics_timer = Scheduler(
            config.get('STATISTICS_INTERVAL'),
            self.stop_event,
            statistics.clean_section_activity
        )
        self.statistics_timer.start()

        self.traffic_alert_timer = Scheduler(
            config.get('TRAFFIC_ALERT_UPDATE_RATE'),
            self.stop_event,
            statistics.update_traffic_alert_status
        )
        self.traffic_alert_timer.start()

        self.error_alert_timer = Scheduler(
            config.get('ERRORS_ALERT_UPDATE_RATE'),
            self.stop_event,
            statistics.update_error_alert_status
        )
        self.error_alert_timer.start()

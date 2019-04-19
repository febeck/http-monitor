from datetime import datetime, timedelta


class SlidingWindow:
    def __init__(self, time_window):
        self.time_window = time_window
        self.data = []

    def push(self):
        self.data.append(datetime.now())

    def update(self):
        self.data = list(filter(
            lambda x: x > datetime.now() - timedelta(seconds=self.time_window),
            self.data
        ))

    def count_elements(self):
        return len(self.data)

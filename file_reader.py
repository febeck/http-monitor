import time
from config import config


class FileReader():

    def __init__(self, statistics):
        file_to_read = open(config['INPUT_LOG_FILE_PATH'], "r")
        loglines = self.tail_file(file_to_read)
        for line in loglines:
            statistics.queue_data(line)

    def tail_file(self, file):
        file.seek(0, 2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

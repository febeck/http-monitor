import sys
import threading
from config import config
from scheduler import Scheduler


class Colors:
    @staticmethod
    def succes(text): return '\033[92m' + text + '\033[0m'

    @staticmethod
    def warning(text): return '\033[93m' + text + '\033[0m'

    @staticmethod
    def danger(text): return '\033[91m' + text + '\033[0m'

    @staticmethod
    def info(text): return '\033[94m' + text + '\033[0m'


class Display(object):

    def __init__(self, statistics):
        self.statistics = statistics
        self.first_col_width = 25
        self.second_col_tab = '\r' + '\t' * int(self.first_col_width / 4)
        self.second_col_width = 80
        self.table_len = 40           # number of lines

        self.first_col_title = "Website Section Statistics"
        self.second_col_title = "Traffic Alert History"

        self.stop_event = threading.Event()

        self.refresh_timer = Scheduler(
            config.get('REFRESH_RATE'),
            self.stop_event,
            self.refresh
        )
        self.refresh_timer.start()

    @staticmethod
    def clear_console():
        print('\033c')

    @staticmethod
    def move_cursor_up(number_of_lines):
        for _ in range(number_of_lines):
            sys.stdout.write("\033[F")  # Cursor up n line

    @staticmethod
    def jump_lines(number_of_lines):
        print('\n' * number_of_lines)

    def refresh(self):
        self.clear_console()

        # Print header section
        alert_on_off_text = Colors.danger(
            " (High traffic alert is activated)"
        ) if self.statistics.is_alert_on else Colors.succes(" (Normal traffic)")

        table_header = self.first_col_title[0:self.first_col_width] + \
            self.second_col_tab + \
            self.second_col_title[0:self.second_col_width] + \
            alert_on_off_text

        print(table_header)

        # Print sections activity block
        self.jump_lines(1)

        ordered_section = self.statistics.get_sorted_section_activity()
        sections_text = ''
        for section in ordered_section:
            sections_text += ' ' + Colors.info(section['section']) + '\n'
            sections_text += '\t' + 'hits:             ' + \
                str(section['hits']) + '\n'
            sections_text += '\t' + 'errors_count:     ' + \
                str(section['errors_count']) + '\n'
            sections_text += '\t' + 'heaviest_request: ' + \
                str(section['heaviest_request']) + '\n\n'

        print(sections_text)

        # Print alert logs
        self.move_cursor_up(5 * len(ordered_section) + 1)

        alert_text = ''
        alerts = self.statistics.alert_logs[::-1]
        alerts = alerts[0:self.table_len - 2]
        for alert in alerts:
            alert_text += self.second_col_tab + \
                Colors.warning(alert[0:self.second_col_width]) + '\n'

        print(alert_text)

        # Adjust cursor position at bottom
        max_len = max(len(alerts) + 1,  5 * len(ordered_section) + 1)
        if (len(alerts) + 1 < 5 * len(ordered_section) + 1):
            self.jump_lines(5 * len(ordered_section) + 1 - (len(alerts) + 1))

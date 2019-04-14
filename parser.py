import re
from datetime import datetime


class Parser:

    @staticmethod
    def parse_log_line(data):
        try:
            line_regex = '(.*) (.*) (.*) \[(.*)\] "(.*) (.*) (.*)" (.*) (.*)'
            line_match_group = re.match(line_regex, data)

            return {
                "host": line_match_group.group(1),
                "remote_user": line_match_group.group(2),
                "auth_user": line_match_group.group(3),
                "date": datetime.strptime(line_match_group.group(4), '%d/%b/%Y:%H:%M:%S %z'),
                "method": line_match_group.group(5),
                "url": line_match_group.group(6),
                "section": '/' + line_match_group.group(6).split('/')[1],
                "http_version": line_match_group.group(7),
                "status": int(line_match_group.group(8)),
                "bytes": int(line_match_group.group(9)),
            }
        except:
            pass

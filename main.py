from scheduler import UpdatesScheduler
from statistics import Statistics
from file_reader import FileReader
from display import Display


def main():
    statistics = Statistics()
    scheduler = UpdatesScheduler(statistics)
    ui = Display(statistics)
    file_reader = FileReader(statistics)


if __name__ == '__main__':
    main()

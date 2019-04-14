# HTTP MONITOR

## Features

- Traffic statistics about the use of different sections of the website (number of hits, number of errors 4xx and 5xx and heaviest document transferred) in a given time span

- Alerts for high traffic in the website (trigger and recovery) with number of hits and timestamp

- EXTRA FEATURE: Alerts for too many errors (4xx and 5xx) in a time span

## Configure the monitor

All configuration can be altered in the `config.py` file.

```python
{
    # Treshold (in request/second) before firing the alarm
    'AVERAGE_TRAFFIC_TRESHOLD': 10,

    # Interval of time (in seconds) to check for error alarm
    'ERRORS_ALERT_INTERVAL': 10,

    # Path of log file
    'INPUT_LOG_FILE_PATH': '/var/log/access.log',

    # Treshold of failed request (4xx and 5xx HTTP status) in time span to send alert
    'MAX_ERRORS_TRESHOLD': 10,

    # Time (in seconds) before UI refresh
    'REFRESH_RATE': 1,

    # Interval (in seconds) before updating statistics
    'STATISTICS_INTERVAL': 10,

    # Interval of time (in seconds) to check for traffic alarm status
    'TRAFFIC_ALERT_INTERVAL': 120,
}
```

## Run the project

In order to run this project you must have Docker installed in your machine

```bash
# Build your docker container
docker build --tag http-monitor .

# Run the code in the container
docker run -it http-monitor
```

To stop the program you have to make a Ctrl + C a few times until is stops...

## Run the tests

In order to run the tests you must have `python3`

```bash
python3 -m unittest discover
```

## Program design improvements

- Use a more robust UI strategy than printing directly to the console. I tried using npyscreen however it blocked the thread and I didn't manage to get updates from the file read. Even trying to use different threads for both jobs I still didn't manage to make it work.

- Configure an email address, slack bot or some other channels to notify on both traffic and error treshold alam trigger

- Interactive user interface to set config parameters to prevent having to set it directly in the config file

- More graceful shutdown

- Using the information from IP adresses: it would allow knowing (in the long run) from which part of the world is the heaviest traffic, to better position servers to decrease server response time

- Using the time information: it would allow knowing at what time of the day there is a heavier use of the server, which would allow fine tune server scaling to save ressources

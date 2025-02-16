from enum import Enum
import datetime

class LogLevel(Enum):
    INFO=1
    WARNING=2
    ERROR=3
    FATAL=4

def logger(topic, body, level=LogLevel.INFO):
    now = datetime.datetime.now()

    print(f"{now} [{level.name}] :: [{topic}]: {body}")


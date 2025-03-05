import sys
import json
import logging

# https://stackoverflow.com/questions/16757578/what-is-pythons-default-logging-formatter
# https://docs.python.org/3/library/logging.html#logger
# https://stackoverflow.com/questions/900392/getting-the-caller-function-name-inside-another-function-in-python
# https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%M-%D %H:%M:%S",
)

class RCConfig:
    def __init__(self, config_path):
        self.json = self._load_file(config_path)

        # Config logger
        self._config_logger()

        for key in self.json:
            logging.debug(f"Config entry found for: [{key}]")

    def _config_logger(self):
        if "log" in self.json:
            log_conf = self.json.get("log")
            if "logLevel" in log_conf:
                log_level = log_conf.get("logLevel")
               
                logger = logging.getLogger()
                match log_level:
                    case "DEBUG": logger.setLevel(logging.DEBUG)
                    case "INFO": logger.setLevel(logging.INFO)
                    case "WARNING": logger.setLevel(logging.WARNING)
                    case "ERROR": logger.setLevel(logging.ERROR)
                    case "CRITICAL": logger.setLevel(logging.CRITICAL)
                    case _: logger.setLevel(logging.NOTSET)

    def _load_file(self, fn):
        try:
            logging.info(f"Loading config: {fn}..")
            with open(fn) as f:
                data = json.load(f)
        except Exception as e:
            logging.critical(f"Could not json file: {e}")
            sys.exit(1)

        return data
    
    def get(self, key):
        return self.json.get(key)
    
    def keys(self):
        return self.json.keys()

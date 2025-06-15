import time


class Logging:
    PRIORITIES = {
        "debug": 1,
        "info": 2,
        "warning": 3,
        "error": 4
    }

    def __init__(self, function: callable, log_level: str = "info"):
        self.function = function
        self.log_level = self.PRIORITIES.get(log_level.lower(), 1)

    def _log(self, level: str, message: str):
        if self.PRIORITIES[level.lower()] >= self.log_level:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            self.function(f"{timestamp} [{level}] {message}")

    def debug(self, message: str):
        self._log("Debug", message)

    def info(self, message: str):
        self._log("Info", message)

    def warning(self, message: str):
        self._log("Warning", message)

    def error(self, message: str):
        self._log("Error", message)


if __name__ == "__main__":
    logger = Logging(print, "warning")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

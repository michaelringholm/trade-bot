import datetime

DEBUG = 10
INFO  = 20
WARN  = 30
ERROR = 40

class AppLogger:
    def __init__(self, LOG_LEVEL: int = INFO):
        self._level = LOG_LEVEL
        self._emojis = {
            DEBUG: "🔍",
            INFO:  "ℹ️",
            WARN:  "⚠️",
            ERROR: "❌",
        }
        self._labels = {
            DEBUG: "DEBUG",
            INFO:  "INFO",
            WARN:  "WARN",
            ERROR: "ERROR",
        }

    def _log(self, level: int, msg: str):
        if level < self._level:
            return
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emoji = self._emojis.get(level, "📝")
        label = self._labels.get(level, "LOG")
        print(f"{now} {emoji} [{label}] {msg}")

    def debug(self, msg: str): self._log(DEBUG, msg)
    def info(self, msg: str):  self._log(INFO, msg)
    def warn(self, msg: str):  self._log(WARN, msg)
    def error(self, msg: str): self._log(ERROR, msg)

logger = AppLogger(INFO)

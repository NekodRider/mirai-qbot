from graia.application import AbstractLogger
from logging.handlers import TimedRotatingFileHandler
import logging
from pathlib import Path


class DefaultLogger(AbstractLogger):

    def __init__(self, level=logging.INFO, fmt_str=None):
        self.logger = logging.getLogger()
        self.logger.setLevel(level)

        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(level)

        log_path = Path(__file__).parent.parent.joinpath(
            'logs', 'mirai_bot.log')
        self.file_handler = TimedRotatingFileHandler(log_path,
                                                     when='h',
                                                     interval=12,
                                                     backupCount=5,
                                                     encoding='utf-8')
        self.file_handler.setLevel(level)

        formatter = logging.Formatter(
            fmt_str or "%(asctime)s - %(levelname)s: %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S')
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)
        self.console_handler.setFormatter(formatter)
        self.logger.addHandler(self.console_handler)

    def info(self, msg):
        msg = msg.replace("\n", r"\n")
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg, exc_info=True)

    def debug(self, msg):
        self.logger.debug(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def exception(self, msg):
        self.logger.exception(msg, exc_info=True)

    def close(self):
        self.logger.removeHandler(self.console_handler)
        self.logger.removeHandler(self.file_handler)
        self.file_handler.close()
        self.console_handler.close()
        logging.shutdown()


defaultLogger = DefaultLogger()

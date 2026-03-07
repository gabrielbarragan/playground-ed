import logging


class LoggerHandler:
    def __init__(self):
        self.name = "Wompi"
        self.logger = self.__get_logger()

    def __get_logger(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(level=logging.DEBUG)
        # set formatter
        log_file_formatter = logging.Formatter(
            '{{"timestamp": "%(asctime)s","level": "%(levelname)s", "message": "%(message)s"}}',
            "%Y-%m-%d %H:%M:%S")
        # Formatter para consola
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            "%Y-%m-%d %H:%M:%S")


        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(level=logging.DEBUG)

        if logger.handlers:
            logger.handlers = []
        logger.addHandler(console_handler)
        return logger

    def get_logger(self):
        return self.logger

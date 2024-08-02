import logging
import os
import time
from glob import glob


class RuntimeLog:
    def __init__(self):
        self.log_folder = r'C:\ProgramData\idv-login\guiLog'
        self.ensure_log_folder_exists()
        self.log_file = self.generate_log_file_name()
        self.configure_logging()
        self.cleanup_logs()

    def ensure_log_folder_exists(self):
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

    def generate_log_file_name(self):
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(self.log_folder, f"{timestamp}.log")

    def configure_logging(self):
        logging.basicConfig(filename=self.log_file,
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            encoding='utf-8',
                            )

    def info(self, message):
        logging.info(message)
        print(message)

    def exception(self, message):
        logging.exception(message)
        print(message)

    def error(self, message):
        logging.error(message)
        print(message)

    def warning(self, message):
        logging.warning(message)
        print(message)

    def debug(self, message):
        logging.debug(message)
        print(message)

    def critical(self, message):
        logging.critical(message)
        print(message)

    def cleanup_logs(self):
        logs = glob(os.path.join(self.log_folder, '*.log'))
        if len(logs) > 10:
            logs.sort(key=os.path.getmtime)
            for log in logs[:-10]:
                os.remove(log)


runtime_log = RuntimeLog()
runtime_log.info('日记记录器初始化完成')

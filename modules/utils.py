#---------------------------------------------------------------------
# This .py is used to defined general functions.

#---------------------------------------------------------------------

from enum import Enum
import os
from datetime import datetime

print("--> Importing Utility Functions from 'utils.py'.")

# REVISIT: Define a global logger path, to securely set it.

class LogLevel(Enum):
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    NONE = ''

class Logger:
    def __init__(self, log_file_path: str = 'log.txt'):
        self.log_file_path = log_file_path
        if not os.path.exists(log_file_path):
            open(log_file_path, 'w').close()
        
        self.width: int = 125
        
    def _write_to_file(self, text: str):
        with open(self.log_file_path, 'a') as f:
            f.write(text + '\n')
    
    def _print_and_log(self, text: str):
        print(text)
        self._write_to_file(text)

    def log(self, message: str, log_level: LogLevel = LogLevel.INFO):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp}\t{log_level:<10}\t{message}"
        self._print_and_log(log_entry)
    
    def print_log_separator(self, text: str = 'Separator'):
        separator_line = '-' * self.width
        self._print_and_log(separator_line)
        self.log(text, log_level = LogLevel.NONE)
        self._print_and_log(separator_line)
    
    def log_start(self, text: str = 'Start'):
        start_line = '-' * self.width
        self._print_and_log(start_line)
        self.log(text, log_level = LogLevel.NONE)
        

    def log_end(self, text: str = 'End'):
        end_line = '-' * self.width
        self.log(text, log_level = LogLevel.NONE)
        self._print_and_log(end_line)

    def reset_log(self):
        open(self.log_file_path, 'w').close()



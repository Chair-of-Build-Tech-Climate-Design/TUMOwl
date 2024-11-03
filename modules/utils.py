#---------------------------------------------------------------------
# This .py is used to defined general functions.

#---------------------------------------------------------------------


import os
from datetime import datetime

print("--> Importing Utility Functions from 'utils.py'.")

# REVISIT: Adjust Loggins to proper format, with datetime, Method, Type and Message.
# REVISIT: Define a global logger path, to securely set it.

class Logger:
    def __init__(self, log_file_path: str = 'log.txt'):
        self.log_file_path = log_file_path
        # Create log file if it doesn't exist
        if not os.path.exists(log_file_path):
            open(log_file_path, 'w').close()
        
    def _write_to_file(self, text: str):
        with open(self.log_file_path, 'a') as f:
            f.write(text + '\n')
    
    def _print_and_log(self, text: str):
        print(text)
        self._write_to_file(text)
    
    def print_log_separator(self, text: str = 'Separator'):
        width = 125
        separator_line = width * '-'
        self._print_and_log(separator_line)
        self._print_and_log(text)
        self._print_and_log(separator_line)
    
    def log_start(self, text: str = 'Start'):
        width = 125
        start_line = width * '-'
        self._print_and_log(start_line)
        self._print_and_log(text)

    def log_end(self, text: str = 'End'):
        width = 125
        end_line = width * '-'
        self._print_and_log(text)
        self._print_and_log(end_line)

    def basic_log(self, message: str):
        """Log with a timestamp, writes to file, and prints to console."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - {message}"
        self._print_and_log(log_entry)

    def reset_log(self):
        """Clears the contents of the log file."""
        open(self.log_file_path, 'w').close()
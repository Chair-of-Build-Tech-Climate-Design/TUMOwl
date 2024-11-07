
#---------------------------------------------------------------------
# This .py is used to defined everything regarding the waether files
# import and data handling.

#---------------------------------------------------------------------

import os

from modules.WeatherFile.WeatherFile import WeatherFile 
from modules.WeatherFile.importers.EpwImporter import EPWImporter
from modules.utils import *

class Importer:
    def __init__(self, file_path: str, log_file_path: str = 'log.txt'):
        self.file_path = file_path
        self.logger = Logger(log_file_path)
        self.importers = {
            '.epw': EPWImporter,
            # Add other importers for additional file types
        }

    def import_file(self) -> WeatherFile:
        file_extension = os.path.splitext(self.file_path)[1].lower()
        importer_class = self.importers.get(file_extension)

        if not importer_class:
            self.logger.log(f"Unsupported file type: '{file_extension}'", log_level=LogLevel.ERROR)
            raise ValueError(f"Unsupported file type: '{file_extension}'")

        importer = importer_class(self.file_path, self.logger)
        return importer.import_file()
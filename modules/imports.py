#---------------------------------------------------------------------
# This .py is used to defined for data import functions.

#---------------------------------------------------------------------

import pandas as pd
import json
from pandas import DataFrame

from modules.utils import *

print("--> Importing Import Functions from 'imports.py'.")

# REVISIT: Create more profiles and adjsut it to a proper import, considering the units as a secondary column.
# REVISIT: Remove all undefined erros, by defining variables properly.

class SimulationResultsImporter:
    def __init__(self, file_path: str, json_config_path: str, separator: str = '\t', data_type: str = 'Trnsys', log_file_path: str = 'log.txt'):
        self.file_path = file_path
        self.json_config_path = json_config_path
        self.separator = separator  
        self.df = None
        self.logger = Logger(log_file_path)
        self.data_type = data_type

    def loadFile(self) -> DataFrame:
        self.df = pd.read_csv(self.file_path, header=[0, 1], sep=self.separator)
        
        # Maybe this as an extra method.
        self.df.columns = pd.MultiIndex.from_tuples(
            [(str(col[0]).strip(), str(col[1]).strip()) for col in self.df.columns]
        )
        
        return self.df

    def processDataFrame(self) -> DataFrame:
        self.df = self.df.apply(pd.to_numeric, errors='coerce')
        return self.df

    def renameColumnsFromJson(self):
        # Load JSON configuration
        with open(self.json_config_path, 'r') as f:
            config = json.load(f)
        
        # Retrieve configuration for the specified data type
        type_config = config.get(self.data_type)

        if not type_config:
            self.logger.log(f"No configuration found for Type: {self.data_type}. No columns renamed.", log_level=LogLevel.ERROR)
            return

        if not type_config.get("Settings", {}).get("RenameColumns", False):
            self.logger.log(f"> Settings: RenameColumns is DISABLED for Type: {self.data_type} in the JSON configuration.")
            return
        else:
            self.logger.log(f"> Settings: RenameColumns is ENABLED for Type: {self.data_type} in the JSON configuration.")

        # Build the renaming dictionary from RenameDictionary
        rename_dict = {item["Column"]: item["Rename"] for item in type_config.get("RenameDictionary", [])}
        existing_columns = set(self.df.columns.get_level_values(0))
        rename_count = sum(1 for col in rename_dict if col in existing_columns)
        
        # Apply renaming and log results
        self.df.rename(columns=rename_dict, level=0, inplace=True)
        self.logger.log(f"Renamed {rename_count} out of {len(self.df.columns)} columns based on the JSON configuration.")

    def import_file(self) -> DataFrame:
        self.logger.log_start("Process Started")   
        self.loadFile()   
        self.renameColumnsFromJson()  
        self.processDataFrame()        
        self.logger.log_end("Process Finished") 
        return self.df

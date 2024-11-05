#---------------------------------------------------------------------
# This .py is used to defined for data import functions.

#---------------------------------------------------------------------

import pandas as pd
import json
from pandas import DataFrame

from modules.utils import *

print("--> Importing Import Functions from 'imports.py'.")

# REVISIT: Create more profiles and adjsut it to a proper import, considering the units as a secondary column or attach them directly to the column?
# REVISIT: Remove all undefined erros, by defining variables properly.

class SimulationResultsImporter:
    def __init__(self, file_path: str, json_config_path: str, data_type: str = 'Trnsys', log_file_path: str = 'log.txt'):
        self.file_path = file_path
        self.json_config_path = json_config_path
        self.data_type = data_type
        self.logger = Logger(log_file_path)
        
        self.config: dict = loadJsonConfig(json_config_path)     
        self.separator = self.getSeperator()

        self.df = None

    # def loadJsonConfig(self) -> dict:
    #     """Loads the JSON configuration file."""
    #     try:
    #         with open(self.json_config_path, 'r') as f:
    #             config = json.load(f)
    #             self.logger.log(f"Configuration loaded successfully from {self.json_config_path}.")
    #             return config
    #     except FileNotFoundError:
    #         self.logger.log(f"Configuration file not found at {self.json_config_path}.", log_level=LogLevel.ERROR)
    #         return {}
    #     except json.JSONDecodeError:
    #         self.logger.log(f"Invalid JSON format in configuration file at {self.json_config_path}.", log_level=LogLevel.ERROR)
    #         return {}

    def getSeperator(self) -> str:
        """Retrieves the separator setting from the loaded config."""
        type_config = self.config.get(self.data_type)

        if not type_config:
            self.logger.log(f"No configuration found for Type: {self.data_type}. Using default separator '\\t'.", log_level=LogLevel.WARNING)
            return "\t"
        
        separator = type_config.get("Settings", {}).get("Separator", "\t")
        self.logger.log(f"Separator set to '{separator}' for Type: {self.data_type}.")
        return separator

    def loadFile(self) -> DataFrame:
        self.df = pd.read_csv(self.file_path, header=[0, 1], sep=self.separator)
        
        self.df.columns = pd.MultiIndex.from_tuples(
            [(str(col[0]).strip(), str(col[1]).strip()) for col in self.df.columns]
        )
        
        return self.df

    def processDataFrame(self) -> DataFrame:
        self.df = self.df.apply(pd.to_numeric, errors='coerce')
        return self.df

    def renameColumnsFromJson(self):
        type_config = self.config.get(self.data_type)

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
        
        self.df.rename(columns=rename_dict, level=0, inplace=True)
        self.logger.log(f"Renamed {rename_count} out of {len(self.df.columns)} columns based on the JSON configuration.")

    def import_file(self) -> DataFrame:
        self.logger.log_start("Process Started")   
        self.loadFile()   
        self.renameColumnsFromJson()  
        self.processDataFrame()        
        self.logger.log_end("Process Finished") 
        return self.df


def loadJsonConfig(json_config_path: str) -> dict:
    """Loads the JSON configuration file."""
    logger = Logger("log.txt")

    try:
        with open(json_config_path, 'r') as f:
            config = json.load(f)
            logger.log(f"Configuration loaded successfully from {json_config_path}.")
            return config
    except FileNotFoundError:
        logger.log(f"Error: Configuration file not found at {json_config_path}.")
        return {}
    except json.JSONDecodeError:
        logger.log(f"Error: Invalid JSON format in configuration file at {json_config_path}.")
        return {}

def printAvailableTypes(json_config_path: str):
    """Prints all available types defined in the JSON configuration."""
    logger = Logger("log.txt")

    config = loadJsonConfig(json_config_path)
    if not config:
        logger.log("No configuration loaded. Unable to print available types.")
        return

    available_types = list(config.keys())
    types_list = ", ".join(available_types)  # Join types as a comma-separated string
    logger.log(f"Available types in the JSON configuration: [{types_list}]")


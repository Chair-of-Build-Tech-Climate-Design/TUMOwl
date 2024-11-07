
#---------------------------------------------------------------------
# This .py is used to defined everything regarding the waether files
# import and data handling.

#---------------------------------------------------------------------

import pandas as pd
import json
from pandas import DataFrame
import numpy as np

from modules.utils import *

class Metadata:
    def __init__(self, longitude=0.0, latitude=200.0, elevation=4.0):
        self.longitude = longitude
        self.latitude = latitude
        self.elevation = elevation
        # Add more metadata attributes as needed

class WeatherFile:
    def __init__(self, file_path: str, data: pd.DataFrame, metadata: Metadata):
        self.file_path = file_path
        self.data = data
        self.metadata = metadata

class Importer:
    def __init__(self, file_path: str, log_file_path: str = 'log.txt'):
        self.file_path = file_path
        self.logger = Logger(log_file_path)
        self.supported_filetypes = {
            '.epw': self._read_epw,
            # Add more file extensions and methods as needed
        }

    def import_file(self) -> WeatherFile:
        """Loads the weather data based on file extension and returns a WeatherFile object."""
        file_extension = os.path.splitext(self.file_path)[1].lower()
        
        if file_extension in self.supported_filetypes:
            data, metadata = self.supported_filetypes[file_extension]()
        else:
            self.logger.log(f"Unsupported file type: '{file_extension}'. Supported types are: {list(self.supported_filetypes.keys())}", log_level=LogLevel.ERROR)
            raise ValueError(f"Unsupported file type: '{file_extension}'")
        
        return WeatherFile(self.file_path, data, metadata)

    def _read_epw(self) -> pd.DataFrame:
        """Reads EPW file format with ',' as the separator, handles missing values, and checks data validity."""
        self.logger.log("Reading EPW file format, checking data based on the given EPW Data Dictionary: https://bigladdersoftware.com/epx/docs/8-3/auxiliary-programs/energyplus-weather-file-epw-data-dictionary.html#energyplus-weather-file-epw-data-dictionary .")

        column_metadata = {
        "Year":                                     {"name": "Year", "error_value": None, "unit": "YYYY"},
        "Month":                                    {"name": "Month", "error_value": None, "unit": "MM"},
        "Day":                                      {"name": "Day", "error_value": None, "unit": "DD"},
        "Hour":                                     {"name": "Hour", "error_value": None, "unit": "HH"},
        "Minute":                                   {"name": "Minute", "error_value": None, "unit": "mm"},
        "Source":                                   {"name": "Source", "error_value": None, "unit": "", "dtype": "str"},
        "Dry Bulb Temperature":                     {"name": "Dry Bulb Temperature", "error_value": 99.9, "unit": "C", "min_value": -70, "max_value": 70, "dtype": "float"},
        "Dew Point Temperature":                    {"name": "Dew Point Temperature", "error_value": 99.9, "unit": "C", "min_value": -70, "max_value": 70, "dtype": "float"},
        "Relative Humidity":                        {"name": "Relative Humidity", "error_value": 999, "unit": "%", "min_value": 0, "max_value": 110},
        "Atmospheric Station Pressure":             {"name": "Atmospheric Station Pressure", "error_value": 999999, "unit": "Pa", "min_value": 31000, "max_value": 120000},
        "Extraterrestrial Horizontal Radiation":    {"name": "Extraterrestrial Horizontal Radiation", "error_value": 9999, "unit": "W/m2", "min_value": 0},
        "Extraterrestrial Direct Normal Radiation": {"name": "Extraterrestrial Direct Normal Radiation", "error_value": 9999, "unit": "W/m2", "min_value": 0},
        "Horizontal Infrared Radiation Intensity":  {"name": "Horizontal Infrared Radiation Intensity", "error_value": 9999, "unit": "W/m2", "min_value": 0},
        "Global Horizontal Radiation":              {"name": "Global Horizontal Radiation", "error_value": 9999, "unit": "W/m²", "min_value": 0},
        "Direct Normal Radiation":                  {"name": "Direct Normal Radiation", "error_value": 9999, "unit": "W/m2", "min_value": 0},
        "Diffuse Horizontal Radiation":             {"name": "Diffuse Horizontal Radiation", "error_value": 9999, "unit": "W/m2", "min_value": 0},
        "Global Horizontal Illuminance":            {"name": "Global Horizontal Illuminance", "error_value": 999999, "unit": "lux", "min_value": 0},
        "Direct Normal Illuminance":                {"name": "Direct Normal Illuminance", "error_value": 999999, "unit": "lux", "min_value": 0},
        "Diffuse Horizontal Illuminance":           {"name": "Diffuse Horizontal Illuminance", "error_value": 999999, "unit": "lux", "min_value": 0},
        "Zenith Luminance":                         {"name": "Zenith Luminance", "error_value": 9999, "unit": "cd/m2", "min_value": 0},
        "Wind Direction":                           {"name": "Wind Direction", "error_value": 999, "unit": "degrees", "min_value": 0, "max_value": 360},
        "Wind Speed":                               {"name": "Wind Speed", "error_value": 999, "unit": "m/s", "min_value": 0, "max_value": 40},
        "Total Sky Cover":                          {"name": "Total Sky Cover", "error_value": 99, "unit": "", "min_value": 0, "max_value": 10},
        "Opaque Sky Cover":                         {"name": "Opaque Sky Cover", "error_value": 99, "unit": "", "min_value": 0, "max_value": 10},
        "Visibility":                               {"name": "Visibility", "error_value": 9999, "unit": "km"},
        "Ceiling Height":                           {"name": "Ceiling Height", "error_value": 99999, "unit": "m"},
        "Present Weather Observation":              {"name": "Present Weather Observation", "error_value": None, "unit": ""},
        "Present Weather Codes":                    {"name": "Present Weather Codes", "error_value": None, "unit": ""},
        "Precipitable Water":                       {"name": "Precipitable Water", "error_value": 999, "unit": "mm"},
        "Aerosol Optical Depth":                    {"name": "Aerosol Optical Depth", "error_value": .999, "unit": "thousandths"},
        "Snow Depth":                               {"name": "Snow Depth", "error_value": 999, "unit": "cm"},
        "Days Since Last Snowfall":                 {"name": "Days Since Last Snowfall", "error_value": 99, "unit": "D"},
        "Albedo":                                   {"name": "Albedo", "error_value": 999, "unit": ""},
        "Liquid Precipitation Depth":               {"name": "Liquid Precipitation Depth", "error_value": 999, "unit": "mm"},
        "Liquid Precipitation Quantity":            {"name": "Liquid Precipitation Quantity", "error_value": 99, "unit": "hr"}
        }

        column_names = list(column_metadata.keys())

        metadata = Metadata(
            longitude=0.0,  
            latitude=500.0,
            elevation=3.0,
            # Add other metadata
        )

        try:
            df = pd.read_csv(self.file_path, sep=',', header=None, skiprows=8)
            df.columns = column_names[:df.shape[1]]

            # Apply transformations
            self._applyDataTypes(df, column_metadata)
            self._replace_error_values(df, column_metadata)
            self._validate_ranges(df, column_metadata)
            self._log_missing_values(df, column_metadata)

            self.logger.log("EPW file read and processed successfully.")
            return df, metadata

        except Exception as e:
            self.logger.log(f"Failed to read EPW file: {e}", log_level=LogLevel.ERROR)
            raise

    def _applyDataTypes(self, df, column_metadata):
        """Enforces data types for each column based on column metadata, defaulting to int if dtype is unspecified."""
        for col, meta in column_metadata.items():
            if col in df.columns:
                dtype = meta.get("dtype", "int")
                try:
                    df[col] = df[col].astype(dtype)
                except ValueError:
                    self.logger.log(f"Could not convert {col} to {dtype} due to incompatible values. Applying coercion.")
                    if dtype in ["float", "int"]:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                    else:
                        df[col] = df[col].astype("str")

    def _replace_error_values(self, df, column_metadata):
        for col, meta in column_metadata.items():
            if col in df.columns and meta["error_value"] is not None:
                df[col] = df[col].replace(meta["error_value"], np.nan)

    def _validate_ranges(self, df, column_metadata):
        for col, meta in column_metadata.items():
            out_of_bounds = pd.Series([False] * len(df))
            
            if col in df.columns:
                if "min_value" in meta:
                    out_of_bounds |= (df[col] < meta["min_value"])
                if "max_value" in meta:
                    out_of_bounds |= (df[col] > meta["max_value"])
                
                out_of_bounds_count = out_of_bounds.sum()
                
                df.loc[out_of_bounds, col] = np.nan

                if out_of_bounds_count > 0:
                    total_count = len(df[col])
                    self.logger.log(f"{meta['name']} has {out_of_bounds_count} out-of-range values out of {total_count} total values.")

    def _log_missing_values(self, df, column_metadata):
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                total_count = len(df[col])
                self.logger.log(f"{column_metadata[col]['name']} has {missing_count} missing values out of {total_count} total values.")



            # DWD Daten Import
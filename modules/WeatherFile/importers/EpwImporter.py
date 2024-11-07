import pandas as pd
import numpy as np
from modules.utils import *
from typing import TypedDict, Optional, Dict, Union

from modules.utils import Logger
from modules.WeatherFile.WeatherFile import Metadata, WeatherFile

class ColumnMetadata(TypedDict, total=False):
    name: str
    error_value: Optional[Union[int, float]]
    unit: str
    dtype: Optional[str]
    min_value: Optional[float]
    max_value: Optional[float]

class EPWImporter:
    def __init__(self, file_path: str, logger: Logger):
        self.file_path = file_path
        self.logger = logger

    def import_file(self) -> WeatherFile:
        """Reads EPW file, processes data, and returns a WeatherFile object."""
        self.logger.log("Reading EPW file format...")

        column_metadata: Dict[str, ColumnMetadata] = {
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

        metadata = Metadata(longitude=0.0, latitude=500.0, elevation=3.0)  

        try:
            df = pd.read_csv(self.file_path, sep=',', header=None, skiprows=8)
            df.columns = list(column_metadata.keys())[:df.shape[1]]
            self._apply_data_types(df, column_metadata)
            self._replace_error_values(df, column_metadata)
            self._validate_ranges(df, column_metadata)
            self._log_missing_values(df, column_metadata)

            self.logger.log("EPW file read and processed successfully.")
            return WeatherFile(self.file_path, df, metadata)
        except Exception as e:
            self.logger.log(f"Failed to read EPW file: {e}", log_level=LogLevel.ERROR)
            raise

    def _apply_data_types(self, df, column_metadata):
        for col, meta in column_metadata.items():
            if col in df.columns:
                dtype = meta.get("dtype", "int")
                try:
                    if dtype in ["float", "int"]:
                        df[col] = pd.to_numeric(df[col], errors="coerce").astype(dtype)
                    else:
                        df[col] = df[col].astype(dtype)
                except ValueError:
                    self.logger.log(f"Could not convert {col} to {dtype}. Applying coercion.", log_level=LogLevel.ERROR)

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
                df.loc[out_of_bounds, col] = np.nan

    def _log_missing_values(self, df, column_metadata):
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                self.logger.log(f"{col} has {missing_count} missing values.", log_level=LogLevel.ERROR)

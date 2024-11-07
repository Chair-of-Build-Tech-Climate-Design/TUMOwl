# modules/weather_file.py
import pandas as pd

class Metadata:
    def __init__(self, longitude: float=0.0, latitude: float=0.0, elevation: float=0.0):
        self.longitude = longitude
        self.latitude = latitude
        self.elevation = elevation
        # Add more metadata attributes as needed

class WeatherFile:
    def __init__(self, file_path: str, data: pd.DataFrame, metadata: Metadata):
        self.file_path = file_path
        self.data = data
        self.metadata = metadata

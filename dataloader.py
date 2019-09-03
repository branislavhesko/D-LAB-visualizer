import numpy as np
import pandas as pd


class DataLoader:

    def __init__(self):
        self.data = None

    def load(self, file_to_load):
        self.data = pd.read_csv(file_to_load, delimiter="\t")
        print(self.data.columns)

    def gps_on_time(self):
        keys = "rec_time", "GPS_Altitude", "GPS_Latitude", "GPS_Longitude", "GPS_Time"
        out = self.data.loc[:, keys]
        out = out[pd.notnull(out.loc[:, "GPS_Time"])].copy()
        return self.transform_rec_time_to_seconds(out)

    @staticmethod
    def transform_rec_time_to_seconds(dataframe: pd.DataFrame):
        assert "rec_time" in dataframe.columns, "rec_time not found in column names!"

        def transform(rec_time_str: str):
            values = rec_time_str.split(":")
            return float(values[-1]) + float(values[-2]) * 60 + float(values[-3]) * 60 * 60

        for i in dataframe.index:
            dataframe.loc[i, "rec_time"] = transform(dataframe.loc[i, "rec_time"])
        dataframe.rec_time = dataframe.rec_time.astype(np.float64)
        return dataframe

if __name__ == "__main__":
    file = "./data/michalrerucha_3. Recording 7242019 41055 PM_CsvData.txt"

    loader = DataLoader()
    loader.load(file)
    print(loader.gps_on_time())
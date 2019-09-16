import numpy as np
import pandas as pd
from tqdm import tqdm

class DataLoader:
    SIGNAL_KEYS = [
        "Can_Details Lane (0x669)_Distance to Left Lane",
        "Can_Details Lane (0x669)_Distance to Right Lane",
        "Can_Car Signals (0x760)_Speed"]


    def __init__(self):
        self.data = None
        self._gps_signals = None
        self._car_signals = None

    def load(self, file_to_load):
        self.data = pd.read_csv(file_to_load, delimiter="\t")
        self._gps_signals = self.gps_on_time()
        self._car_signals = self.car_signals_on_time()
        print(self.data.columns)

    def gps_on_time(self):
        keys = "rec_time", "GPS_Altitude", "GPS_Latitude", "GPS_Longitude", "GPS_Time"
        gps_data = self.data.loc[:, keys]
        gps_data = gps_data[pd.notnull(gps_data.loc[:, "GPS_Time"])].copy()
        gps_data["rec_time"] = gps_data["rec_time"].apply(self.transform)
        return gps_data

    def car_signals_on_time(self):
        car_signals = []
        for key in tqdm(self.SIGNAL_KEYS):
            out = self.data.loc[:, ["rec_time", key]]
            out = out[pd.notnull(out.loc[:, key])].copy()
            out["rec_time"] = out["rec_time"].apply(self.transform)
            car_signals.append(out)
        return car_signals

    # TODO: process all signals and store them in a dict...
    def get_car_signals_in_time_window(self, central_time, interval=30):
        signals_in_time_window = []
        for car_signal in self._car_signals:
            signals_in_time_window.append(car_signal.iloc[
                np.abs(car_signal["rec_time"].values - central_time) < interval, :])
        return signals_in_time_window

    @staticmethod
    def transform(rec_time_str: str):
        values = rec_time_str.split(":")
        return float(values[-1]) + float(values[-2]) * 60 + float(values[-3]) * 60 * 60

    @staticmethod
    def format_time_to_hours(seconds: float):
        hours = seconds // 3600
        seconds = seconds - hours * 3600
        minutes = seconds // 60
        return "{:02d}:{:02d}:{:.3f}".format(int(hours), int(minutes), seconds - minutes * 60)


if __name__ == "__main__":
    file = "./data/michalrerucha_3. Recording 7242019 41055 PM_CsvData.txt"

    loader = DataLoader()

    loader.load(file)
    from matplotlib import pyplot as plt
    plt.plot(loader.get_car_signals_in_time_window(100, 30)[DataLoader.SIGNAL_KEYS[0]])
    plt.show()
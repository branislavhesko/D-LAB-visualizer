import numpy as np
import pandas as pd
from tqdm import tqdm

from biosignalsplux_loader import BiosignalsPluxLoader, BiosignalsPluxNew
from config import Configuration, CanSignals


class DataLoader:
    def __init__(self):
        self.data = None
        self._gps_signals = None
        self._car_signals = None
        self.bio_signals = None

    def load(self):
        self.data = pd.read_csv(Configuration.CAN_SIGNAL_FILE, delimiter="\t")
        self._gps_signals = self.gps_on_time()
        self._car_signals = self.car_signals_on_time()
        self.bio_signals = BiosignalsPluxNew()
        self._load_biosignals(Configuration.BIOSIGNAL_FILE)
        print(self.data.columns)

    def _load_biosignals(self, bio_file):
        self.bio_signals.load_file(bio_file)
        self.bio_signals.normalize_data()
        self.bio_signals.generate_rec_time()

    def gps_on_time(self):
        keys = "rec_time", "GPS_Altitude", "GPS_Latitude", "GPS_Longitude", "GPS_Time"
        gps_data = self.data.loc[:, keys]
        gps_data = gps_data[pd.notnull(gps_data.loc[:, "GPS_Time"])].copy()
        gps_data["rec_time"] = gps_data["rec_time"].apply(self.transform)
        return gps_data

    def car_signals_on_time(self):
        car_signals = []
        for key in tqdm(CanSignals.SIGNAL_KEYS):
            out = self.data.loc[:, ["rec_time", key]]
            out = out[pd.notnull(out.loc[:, key])].copy()
            out["rec_time"] = out["rec_time"].apply(self.transform)
            car_signals.append(out)
        return car_signals

    # TODO: process all signals and store them in a dict...
    def get_car_signals_in_time_window(self, central_time, interval=30):
        signals_in_time_window = []
        for car_signal in self._car_signals[:-1]:
            signals_in_time_window.append(car_signal.iloc[
                np.abs(car_signal["rec_time"].values - central_time) < interval, :])
        return signals_in_time_window

    def get_time_utc(self, time):
        return self._car_signals[-1].iloc[np.argmin(
            np.abs(self._car_signals[-1]["rec_time"].values - time)), 1]

    def get_biosignals_in_time_window(self, central_time, interval=30, signal_names=None):
        if signal_names is None:
            signal_names = self.bio_signals.sensor
        bio_signals = []
        for sensor in signal_names:
            bio_signals.append(self.bio_signals.data.loc[
                                   np.abs(self.bio_signals.data["rec_time"].values - central_time) < interval,
                                   ("rec_time", sensor)])
        return bio_signals

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
    bioo_file = "opensignals_0007803B46AE_2018-11-28_14-36-55.txt"
    loader = DataLoader()

    loader.load(file, bioo_file)
    from matplotlib import pyplot as plt
    plt.plot(loader.get_car_signals_in_time_window(100, 30)[CanSignals.SIGNAL_KEYS[0]])
    plt.show()

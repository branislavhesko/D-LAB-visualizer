import os

import numpy as np
import pandas as pd


class SynchronizationManager:

    def __init__(self, path_to_synchronization_file):
        self._synchronization_time = None
        self._load(path_to_synchronization_file)

    @property
    def synchronization_time(self):
        return self._synchronization_time / 1000. if self._synchronization_time is not None else 0.

    def _load(self, path):
        if not os.path.exists(path):
            return
        data = pd.read_csv(path, delimiter="\t")
        if "client_utc" in data.columns and "server_utc" in data.columns:
            self._synchronization_time = np.median(
                data.server_utc.astype("int64").values - data.client_utc.astype("int64").values)
        else:
            pass


if __name__ == "__main__":
    sync = SynchronizationManager("./data/synchronization.txt")
    print(sync.synchronization_time)
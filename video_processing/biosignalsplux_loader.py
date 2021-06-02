import numpy as np

import pandas as pd


class BiosignalsPluxLoader:

    def __init__(self):
        self.filename = None
        self.data = None
        self.header = None
        self.device_name = None

    def load_file(self, filename):
        self.filename = filename
        self._load_header()
        self._load_data()

    def normalize_data(self):
        resulutions = self.header["resolution"]
        for index, resulution in enumerate(resulutions[-1::-1]):
            self.data.iloc[:, -1 - index] = self.data.iloc[:, -1 - index] / float(2 ** resulution)

    def _load_header(self):
        with open(self.filename, "r") as f:
            header_line = f.readlines()[1]

        header = eval(header_line[2:])
        self.device_name = list(header.keys())[0]
        self.header = header[self.device_name]

    def _load_data(self):
        self.data = pd.read_csv(self.filename, delimiter="\t", skiprows=3, names=self.columns + ["+"]).iloc[:, :-1]
        self.data.columns = self.columns[:-len(self.sensor)] + self.sensor

    def generate_rec_time(self, time_):
        self.data["rec_time"] = self.data["nSeq"] / self.sampling_rate + time_

    @property
    def device(self):
        return self.header["channels"]

    @property
    def columns(self):
        return self.header["column"]

    @property
    def sampling_rate(self):
        return self.header["sampling rate"]

    @property
    def sensor(self):
        return self.header["sensor"]

    def __str__(self):
        formatted_dict = "HEADER: \n" + "\n".join(["\t"+ key + " : " + str(self.header[key]) for key in self.header.keys()])
        return "DEVICE: " + self.device_name + "\n" + formatted_dict

    def save(self, file_path):
        with open(file_path, "w") as f:
            f.write(str(self.header) + "\n")
        self.data.to_csv(file_path, header=self.header, mode="a", sep="\t", index=None)


if __name__ == "__main__":
    from glob import glob
    for file in glob("./data/ope*.txt"):
        bs = BiosignalsPluxLoader()
        bs.load_file(file)
        bs.normalize_data()
        bs.generate_rec_time()
        print(bs)

    from matplotlib import pyplot as plt
    plt.plot(bs.data.values[:, -1])
    plt.show()

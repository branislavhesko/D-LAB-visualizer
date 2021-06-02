import datetime
import pytz
import time
import os
date = "2019-7-24,23:37:22.98"
import pandas as pd
import glob

x = datetime.datetime(year=2020, month=9, day=14, hour=23, minute=13, second=46, microsecond=int(0 * 1e4))
print((x - datetime.datetime(1970, 1, 1)).total_seconds())


class PostProcessBiosignalData:

    def __init__(self, base_path, output_path):
        self.base_path = base_path
        self.output_path = output_path

    def execute(self):
        folders = next(os.walk(self.base_path))[1]
        
        for folder in folders:
            subfolders = next(os.walk(os.path.join(self.base_path, folder)))[1]
            for subfolder in subfolders:
                subsubfolders = next(os.walk(os.path.join(self.base_path, folder, subfolder)))[1]
                for subsubfolder in subsubfolders:
                    path = os.path.join(self.base_path, folder, subfolder, subsubfolder, "biosignals.csv")
                    if not os.path.exists(path):
                        continue
                    print(path)
                    header = _load_header(path)
                    utc_time_start = _get_utc_time(header).total_seconds()
                    data = pd.read_csv(path, sep="\t", skiprows=1)
                    data["UTC"] = utc_time_start + data["rec_time"]
                    file_path = path[:-4] + "_WITH_UTC.csv"
                    with open(file_path, "w") as f:
                        f.write(str(header) + "\n")
                    data.to_csv(file_path, header=header, mode="a", sep="\t", index=None)

def _get_utc_time(header):
    date_ = list(map(int, header["date"].split("-")))
    time_ = list(map(int, header["time"].split(".")[0].split(":")))
    return datetime.datetime(year=date_[0], month=date_[1], day=date_[2], hour=time_[0], 
                             minute=time_[1], second=time_[2], microsecond=1000 * int(header["time"].split(".")[1])) - datetime.datetime(1970, 1, 1, hour=2)



def _load_header(path):
    with open(path, "r") as f:
        header_line = f.readlines()[0]

    header = eval(header_line)
    return header


if __name__ == "__main__":
    p = PostProcessBiosignalData("/media/brani/DATA/BIORIDIC_PROCESSED", "/media/brani/DATA/BIORIDIC_PROCESSED")
    p.execute()
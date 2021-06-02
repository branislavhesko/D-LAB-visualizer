import datetime
import pytz
import time
import os
date = "2019-7-24,23:37:22.98"
import pandas as pd
import glob



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

file_path = "./biosignals_WITH_UTC.csv"
path = "./biosignals.csv"


header = _load_header(path)
utc_time_start = _get_utc_time(header).total_seconds()
data = pd.read_csv(path, sep="\t", skiprows=1)
data["UTC"] = utc_time_start + data["rec_time"]
with open(file_path, "w") as f:
    f.write(str(header) + "\n")
data.to_csv(file_path, header=header, mode="a", sep="\t", index=None)

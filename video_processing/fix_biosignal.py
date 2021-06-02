import pandas as pd
import numpy as np
import glob
from biosignalsplux_loader import BiosignalsPluxLoader
from utils import get_time
from copy import deepcopy
import os

base_path = "/home/brani/Desktop/BIORIDICE_PROCESSED/5/"

biosignals = sorted(glob.glob(os.path.join(base_path, "opensignal*.txt")))
biosignal_output = None
start_time = None
for biosignal in biosignals:
    loader = BiosignalsPluxLoader()
    loader.load_file(biosignal)
    time_ = get_time(loader.header["time"])
    start_time = time_ if start_time is None else start_time
    loader.generate_rec_time(time_ - start_time)
    if biosignal_output is None:
        biosignal_output = deepcopy(loader)
        start_time = get_time(biosignal_output.header["time"])
    else:
        biosignal_output.data = pd.concat([biosignal_output.data, loader.data], sort=False)
if biosignal_output is not None:
    
    biosignal_output.save("biosignals.csv")
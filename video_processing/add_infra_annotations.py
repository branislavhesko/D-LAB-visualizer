import glob
import pandas as pd
import numpy as np
import os
import geopy.distance

from utils import haversine


legend = {
	"D": "dalnice najezd",
	"D1": "dalnice",
	"D1-END": "konec dalnice",
	"ZO": "zacatek obce",
	"ZO-END": "konec obce",
	"X": "krizovatka",
	"KO": "kruhovy objezd",
	"PR": "prechod"
}

krizovatka = {
	"S": "so svetelnou signalizaciou",
	"B": "bez svetelnej signalizacie",
	"L": "vlavo",
	"P": "vpravo",
	"R": "rovne",
	"T": "stykova",
	"X": "prusecna",
	"Y": "vidlicova",
	"H-H": "hlavni-hlavni",
	"H-V": "hlavni-vedlejsi",
	"V-V": "vedlejsi-vedlejsi",
	"V-H": "vedlejsi-hlavni"
}

crossing = {
	"S": "nasvetleny",
	"N": "nenasvetleny",
	"S": "so svetelnou signalizaciou",
	"B": "bez svetelnej signalizacie"
}

def parse_crossing(record):
	pass


def parse_crossroads(record):
	pass


def parse_roundabout(record):
	pass


def parse_record(record):
	if record[0] == "X":
		return parse_crossroads(record)
	elif record[:2] == "KO":
		return parse_roundabout(record)
	elif record[:2] == "PR":
		return parse_crossing(record)
	else:
		return legend.get(record, None)	 



class AddInfraAnnotations():

    def __init__(self):
        super().__init__()
        self._can_14n = pd.read_csv("./CAN2.csv", delimiter=",")
        self._can_14n = self._can_14n[pd.notnull(self._can_14n.loc[:, "GPS_Time"])].reset_index(drop=True)
        self._base_path = None
        self.annotations = self._load_annotations()

    
    def _load_annotations(self):
        gps_annots = pd.DataFrame([], columns=["gps_longitude", "gps_latitude", "utc", "mark"])
        annotations = pd.read_csv("./annotation.txt", delimiter="\t", names=["1", "2", "3", "4"])
        for row in annotations.iterrows():
            
            if "14n" in row[1]["1"]:
                annotation = row[1]["4"]
                if annotation.split("-")[0] in legend:
                    utc = row[1]["3"]
                    position = (self._can_14n["UTC"] - utc).abs().argsort()[0]
                    gps_latitude = self._can_14n["GPS_Latitude"].iloc[position]
                    gps_longitude = self._can_14n["GPS_Longitude"].iloc[position]

                    gps_annots = pd.concat([gps_annots, pd.DataFrame([[gps_longitude, gps_latitude, utc, annotation]], columns=["gps_longitude", "gps_latitude", "utc", "mark"])])
        return gps_annots


    def execute(self, input_path):
        self._base_path = input_path
        folders = next(os.walk(self._base_path))[1]

        for folder in folders:
                subfolders = next(os.walk(os.path.join(self._base_path, folder)))[1]
                for subfolder in subfolders:
                    subsubfolders = next(os.walk(os.path.join(self._base_path, folder, subfolder)))[1]
                    for subsubfolder in subsubfolders:
                        gps_annotation = pd.DataFrame([], columns=["gps_longitude", "gps_latitude", "utc", "mark", "dist[m]"])
                        folder_path = os.path.join(self._base_path, folder, subfolder, subsubfolder)
                        print("Processing: {}".format(folder_path))
                        if os.path.exists(os.path.join(self._base_path, folder, subfolder, subsubfolder, "infrastructure_annotations.csv")):
                            continue
                        can_file = os.path.join(folder_path, "CAN2.csv")
                        data = pd.read_csv(can_file)
                        data = data.loc[:, ("UTC", "GPS_Latitude", "GPS_Longitude")]
                        data = data[pd.notnull(data.loc[:, "GPS_Longitude"])].reset_index(drop=True)
                        for row in self.annotations.itertuples():
                            latitude, longitude = row.gps_latitude, row.gps_longitude
                            distances = []
                            for _, drow in data.iterrows():
                                latitude_can, longitude_can = drow["GPS_Latitude"].copy(), drow["GPS_Longitude"].copy()
                                distances.append(geopy.distance.distance((latitude_can, longitude_can), (latitude, longitude)).m)
                            if len(distances):
                                rop = row.mark
                                print(f"{rop}: {np.amin(distances)}: {np.argmin(distances)}")
                                index = np.argmin(distances)
                                gps_annotation = pd.concat([gps_annotation, pd.DataFrame([[
                                    data["GPS_Longitude"].iloc[index], data["GPS_Latitude"].iloc[index], 
                                    data["UTC"].iloc[index], row.mark, np.amin(distances)]], columns=["gps_longitude", "gps_latitude", "utc", "mark", "dist[m]"])])
                        gps_annotation.to_csv(os.path.join(self._base_path, folder, subfolder, subsubfolder, "infrastructure_annotations.csv"), sep="\t", index=False)
AddInfraAnnotations().execute("/media/brani/DATA/BIORIDIC_PROCESSED")
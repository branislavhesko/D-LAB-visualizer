class Configuration:
    BIOSIGNAL_FILE = "./data/biosignals.csv"
    VIDEO_FILE = "./data/michalrerucha_3. Recording 7242019 41055 PM_Dikablis Glasses 3_Scene Cam_Original_Eye Tracking Video.mp4"
    CAN_SIGNAL_FILE = "./data/michalrerucha_3. Recording 7242019 41055 PM_CsvData.txt"
    BIOSIGNAL_LOADER = "NEW"  # OLD


class CanSignals:
    SIGNAL_KEYS = [
        "Can_Details Lane (0x669)_Distance to Left Lane",
        "Can_Details Lane (0x669)_Distance to Right Lane",
        "Can_Car Signals (0x760)_Speed", "UTC"]
class Configuration:
    BIOSIGNAL_FILE = "./data/biosignals.csv"
    VIDEO_FILE = "./data/output_video_objects.mkv"
    CAN_SIGNAL_FILE = "./data/CAN2.csv"
    BIOSIGNAL_LOADER = "NEW"  # OLD


class CanSignals:
    SIGNAL_KEYS = [
        "Can_Car Signals (0x760)_Brakes",
        "Can_Car Signals (0x760)_Speed", "UTC"]

class Configuration:
    BIOSIGNAL_FILE = "./data/biosignals.csv"
    VIDEO_FILE = "./data/output_video.mp4"
    CAN_SIGNAL_FILE = "./data/CAN2.csv"
    BIOSIGNAL_LOADER = "NEW"  # OLD


class CanSignals:
    SIGNAL_KEYS = [
        "Can_Details Lane (0x669)_Distance to Left Lane",
        "Can_Details Lane (0x669)_Distance to Right Lane",
        "Can_Car Signals (0x760)_Speed", "UTC"]
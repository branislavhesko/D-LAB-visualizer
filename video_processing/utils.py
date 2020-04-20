import datetime


def from_seconds_to_datetime(seconds_from_epoch):
    return datetime.datetime.fromtimestamp(seconds_from_epoch)


def sort_function(string: str):
    recording_start = string.find("Recording")
    string_part = string[recording_start - 4: recording_start - 1]
    string_part = ''.join(i for i in string_part if i.isdigit())
    return float(string_part)


def get_time(time):
    time_parts = time.split(":")
    time_parts = [float(t) for t in time_parts]
    time_parts[0] = time_parts[0] if time_parts[0] > 12 else time_parts[0] + 24
    return time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
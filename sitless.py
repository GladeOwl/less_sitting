from time import sleep
from notification import send_windows_notification, send_telegram_notification
from ctypes import Structure, windll, c_uint, sizeof, byref

ALLOWED_SITTING_DURATION: int = 3300
BREAK_DURATION: int = 300
CURRENT_DURATION: int = 0

FORCE_BREAK: bool = False
KEEP_RUNNING: bool = True
IDLE: bool = True


class LASTINPUTINFO(Structure):
    _fields_ = [
        ("cbSize", c_uint),
        ("dwTime", c_uint),
    ]


def get_idle_duration():
    last_input_info: LASTINPUTINFO = LASTINPUTINFO()
    last_input_info.cbSize: int = sizeof(last_input_info)
    windll.user32.GetLastInputInfo(byref(last_input_info))
    millis: float = windll.kernel32.GetTickCount() - last_input_info.dwTime
    return millis / 1000.0


previous_idle_duration: float = 0
while KEEP_RUNNING:
    idle_duration: float = get_idle_duration()

    if not IDLE and idle_duration > BREAK_DURATION:
        IDLE = True
        CURRENT_DURATION = 0
        print("No Activity Dectected. We're now IDLE.")
    elif IDLE and idle_duration < BREAK_DURATION:
        IDLE = False
        print(f"Activity Detected. We were idle for {previous_idle_duration} seconds")

    if not IDLE and not FORCE_BREAK and CURRENT_DURATION >= ALLOWED_SITTING_DURATION:
        FORCE_BREAK = True
        print("Duration Exceeded Allowed Sitting Time. Sending Notification.")
        send_windows_notification()
        send_telegram_notification(
            "Take a Break. You've been sitting for a quite a while."
        )

    if not IDLE:
        CURRENT_DURATION += 1

    if FORCE_BREAK and IDLE:
        FORCE_BREAK = False
        send_telegram_notification("We're good. You may sit again.")

    previous_idle_duration = idle_duration
    sleep(1)

from time import sleep
from notification import send_windows_notification, send_telegram_notification
from ctypes import Structure, windll, c_uint, sizeof, byref

ALLOWED_SITTING_DURATION: int = 3300
BREAK_DURATION: int = 300
GRACE_PERIOD: int = 10

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


current_grace: int = 0
current_duration: int = 0
previous_idle_duration: float = 0
while KEEP_RUNNING:
    idle_duration: float = get_idle_duration()

    if not IDLE and idle_duration > BREAK_DURATION:
        IDLE = True
        current_duration = 0
        print("No Activity Dectected. We're now IDLE.")
    elif IDLE and idle_duration < BREAK_DURATION:
        IDLE = False
        print(f"Activity Detected. We were idle for {previous_idle_duration} seconds")

    if not IDLE and not FORCE_BREAK and current_duration >= ALLOWED_SITTING_DURATION:
        if current_grace >= GRACE_PERIOD:
            current_grace = 0
            FORCE_BREAK = False

        if not FORCE_BREAK:
            FORCE_BREAK = True
            print(
                "Duration Exceeded Allowed Sitting Time or Grace Period. Sending Notification."
            )
            send_windows_notification()
            send_telegram_notification(
                "Take a Break. You've been sitting for a quite a while."
            )

        current_grace += 1

    if not IDLE:
        current_duration += 1

    if FORCE_BREAK and IDLE:
        FORCE_BREAK = False
        send_telegram_notification("We're good. You may sit again.")

    previous_idle_duration = idle_duration
    sleep(1)

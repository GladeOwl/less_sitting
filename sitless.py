import datetime
from time import sleep
from notification import send_windows_notification, send_telegram_notification
from ctypes import Structure, windll, c_uint, sizeof, byref

ALLOWED_SITTING_DURATION: int = 3300
BREAK_DURATION: int = 300
GRACE_PERIOD: int = 10

FORCE_BREAK: bool = False
KEEP_RUNNING: bool = True
IDLE: bool = True
REPEAT_NAG: bool = False


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
    now: str = f"[{str(datetime.datetime.now().strftime('%I:%M:%S'))}]"
    idle_duration: float = get_idle_duration()

    if not IDLE and idle_duration > BREAK_DURATION:
        IDLE = True
        current_duration = 0
        print(f"{now} No Activity Dectected. We're now IDLE.")
    elif IDLE and idle_duration < BREAK_DURATION:
        IDLE = False
        print(
            f"{now} Activity Detected. We were idle for {previous_idle_duration} seconds"
        )

    if not IDLE and current_duration >= ALLOWED_SITTING_DURATION:
        if not FORCE_BREAK:
            FORCE_BREAK = True
            print(
                f"{now} Duration Exceeded Allowed Sitting Time or Grace Period. Sending Notification."
            )
            send_windows_notification()
            send_telegram_notification(
                f"{now} Take a Break. You've been sitting for a quite a while."
            )

        if current_grace >= GRACE_PERIOD and idle_duration < GRACE_PERIOD - 3:
            current_grace = 0
            REPEAT_NAG = True
            # print(f"{now} Grace Period Expired.")

        if REPEAT_NAG:
            print(f"{now} No Touchy! Come on!")
            send_windows_notification()
            send_telegram_notification(f"{now} No Touchy! Get off now!")
            REPEAT_NAG = False

        current_grace += 1

    if not IDLE:
        current_duration += 1

    if FORCE_BREAK and IDLE:
        FORCE_BREAK = False
        send_telegram_notification(f"{now} We're good. You may sit again.")

    previous_idle_duration = idle_duration
    sleep(1)

import os
from dotenv import load_dotenv
import telegram
from win10toast import ToastNotifier

load_dotenv()
toast = ToastNotifier()


def send_windows_notification():
    toast.show_toast(
        title="Take a Break",
        msg="You been sitting for a bit.",
        icon_path=None,
        duration=5,
        threaded=True,
    )


def send_telegram_notification(message):
    key = os.environ.get("BOTTOKEN")
    userid = os.environ.get("USERID")
    bot = telegram.Bot(token=key)
    bot.send_message(chat_id=userid, text=message)

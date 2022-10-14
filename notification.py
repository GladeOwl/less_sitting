from win10toast import ToastNotifier

toast = ToastNotifier()


def send_windows_notification():
    toast.show_toast(
        title="Take a Break",
        msg="You been sitting for a bit.",
        icon_path=None,
        duration=5,
        threaded=True,
    )

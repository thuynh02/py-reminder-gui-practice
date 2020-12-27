import time
from utils.system_tray import init_tray
from datetime import datetime

ON_STATE = True
ACTION_CONFIG_KEY = "action"
TIME_CONFIG_KEY = "time"
DEFAULT_FADE_IN = 100
DEFAULT_FADE_OUT = 1000


def handle_tray_events(tray, menu_config):
    while ON_STATE:
        event = tray.read(timeout=1)
        if event in menu_config:
            menu_config[event][ACTION_CONFIG_KEY]()

        if datetime.now().second % 30 == 0:
            tray.show_message(
                title="Scheduled Event",
                message=f"The time is: {datetime.now().ctime()}",
                time=(DEFAULT_FADE_IN, DEFAULT_FADE_OUT),
            )


def handle_test_option():
    print("pressed test")


def handle_exit():
    global ON_STATE
    ON_STATE = False


def main():
    menu_config = {
        "Test": {
            ACTION_CONFIG_KEY: handle_test_option,
            TIME_CONFIG_KEY: (DEFAULT_FADE_IN, DEFAULT_FADE_OUT),
        },
        "Exit": {ACTION_CONFIG_KEY: handle_exit, TIME_CONFIG_KEY: (0, 0)},
    }
    tray = init_tray(
        list(menu_config.keys()), "D:\\Projects\\python\\notifier\\icon.png"
    )
    handle_tray_events(tray, menu_config)


if __name__ == "__main__":
    main()

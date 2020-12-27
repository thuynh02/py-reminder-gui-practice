import time
import os
import yaml
from datetime import datetime
from utils.system_tray import init_tray

ON_STATE = True
ACTION_CONFIG_KEY = "action"
TIME_CONFIG_KEY = "time"
DEFAULT_FADE_IN = 100
DEFAULT_FADE_OUT = 2000


def handle_tray_events(tray, menu_config):
    prompted = False
    while ON_STATE:

        # react to events using the given config
        event = tray.read(timeout=1)
        if event in menu_config:
            menu_config[event][ACTION_CONFIG_KEY]()

        # do some action at a repeating interval
        on_interval = datetime.now().minute % 2 == 0
        if (on_interval) and (not prompted):
            handle_interval_action(tray, menu_config)
            prompted = True
        elif not on_interval and prompted:
            prompted = False


def handle_interval_action(tray, menu_config):
    tray.show_message(
        title="Scheduled Event",
        message=f"The time is: {datetime.now().ctime()}",
        time=(DEFAULT_FADE_IN, DEFAULT_FADE_OUT),
    )

    evaluate_current_tasks()


def evaluate_current_tasks():
    print("evaluating")


def handle_test_option():
    print("pressed test")


def handle_exit():
    global ON_STATE
    ON_STATE = False


def get_watchlist_actions(watchlist_path):
    watchlist_obj = {}
    with open(watchlist_path, "r") as watchlist_f:
        watchlist_content = watchlist_f.read()
        watchlist_obj = yaml.safe_load(watchlist_content)

    return watchlist_obj


def main():
    dirname = os.path.dirname(__file__)
    menu_config = {
        "Test": {
            ACTION_CONFIG_KEY: handle_test_option,
            TIME_CONFIG_KEY: (DEFAULT_FADE_IN, DEFAULT_FADE_OUT),
        },
        "Exit": {ACTION_CONFIG_KEY: handle_exit, TIME_CONFIG_KEY: (0, 0)},
    }
    icon_path = os.path.join(dirname, "./icon.png")
    menu_options = list(menu_config.keys())

    watchlist_path = os.path.join(dirname, "./watchlist.yml")
    watchlist_actions = get_watchlist_actions(watchlist_path)
    print(watchlist_actions)

    tray = init_tray(menu_options=menu_options, watchlist_options=watchlist_actions icon_path=icon_path)
    handle_tray_events(tray, menu_config)


if __name__ == "__main__":
    main()

import time
import os
import yaml
import re
import subprocess
from datetime import datetime
from utils.system_tray import init_tray

ON_STATE = True
ACTION_CONFIG_KEY = "action"
TIME_CONFIG_KEY = "time"
DEFAULT_FADE_IN = 100
DEFAULT_FADE_OUT = 2000


def handle_tray_events(tray, menu_config, watchlist_config):
    prompted = False
    while ON_STATE:

        # react to events using the given config
        event = tray.read(timeout=1)
        if event in menu_config:
            menu_config[event][ACTION_CONFIG_KEY]()

        # do some action at a repeating interval
        on_interval = datetime.now().minute % 2 == 0
        if (on_interval) and (not prompted):
            handle_interval_action(tray, menu_config, watchlist_config)
            prompted = True
        elif not on_interval and prompted:
            prompted = False


def handle_interval_action(tray, menu_config, watchlist_config):
    tray.show_message(
        title="Scheduled Event",
        message=f"The time is: {datetime.now().ctime()}",
        time=(DEFAULT_FADE_IN, DEFAULT_FADE_OUT),
    )
    evaluate_current_tasks(watchlist_config)


def get_tasklist():
    tasks = str(subprocess.check_output(["tasklist"])).split("\\r\\n")
    p = []
    for task in tasks:
        m = re.match("(.+?) +(\d+) (.+?) +(\d+) +(\d+.* K).*", task)
        if m is not None:
            p.append(m.group(1))
    return p


def evaluate_current_tasks(watchlist_config):
    print(f"evaluating: {watchlist_config}")

    tasklist = get_tasklist()
    print(tasklist)


def handle_test_option():
    print("pressed test")


def handle_exit():
    global ON_STATE
    ON_STATE = False


def get_watchlist_config(watchlist_path):
    watchlist_obj = {}
    with open(watchlist_path, "r") as watchlist_f:
        watchlist_content = watchlist_f.read()
        watchlist_obj = yaml.safe_load(watchlist_content)

    return watchlist_obj


def main():
    dirname = os.path.dirname(__file__)

    # set vars for tray + its menu
    menu_config = {
        "Test": {
            ACTION_CONFIG_KEY: handle_test_option,
            TIME_CONFIG_KEY: (DEFAULT_FADE_IN, DEFAULT_FADE_OUT),
        },
        "Exit": {ACTION_CONFIG_KEY: handle_exit, TIME_CONFIG_KEY: (0, 0)},
    }
    icon_path = os.path.join(dirname, "./icon.png")
    menu_options = list(menu_config.keys())
    tray = init_tray(menu_options=menu_options, icon_path=icon_path)

    # set vars for watchlist
    watchlist_path = os.path.join(dirname, "./watchlist.yml")
    watchlist_config = get_watchlist_config(watchlist_path)

    # make the tray do stuff!
    handle_tray_events(
        tray=tray, menu_config=menu_config, watchlist_config=watchlist_config
    )


if __name__ == "__main__":
    main()

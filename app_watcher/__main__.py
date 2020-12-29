import time
import os
import yaml
import psutil
import ahocorasick
import utils.checklist as utils_cl
from datetime import datetime
from utils.system_tray import init_tray


ON_STATE = True
ACTION_CONFIG_KEY = "action"
TIME_CONFIG_KEY = "time"
WATCHLIST_CHECKLIST_KEY = "checklist"
TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%Y_%m_%d"
DEFAULT_FADE_IN = 100
DEFAULT_FADE_OUT = 2000
CHECKLIST_MEMO = {}


# ================================================================
# Handlers (Orchestration of process)
# ================================================================


def main():
    dirname = os.path.dirname(__file__)

    # set vars for tray + its menu
    menu_config = {
        "Exit": {ACTION_CONFIG_KEY: do_exit, TIME_CONFIG_KEY: (0, 0)},
    }
    icon_path = os.path.join(dirname, "./icon.png")
    menu_options = list(menu_config.keys())
    tray = init_tray(menu_options=menu_options, icon_path=icon_path)

    # set vars for watchlist
    watchlist_path = os.path.join(dirname, "./watchlist.yml")
    watchlist = get_watchlist(watchlist_path)

    # make the tray do stuff!
    handle_tray_events(tray=tray, menu_config=menu_config, watchlist=watchlist)


def handle_tray_events(tray, menu_config, watchlist):
    prompted = False
    while ON_STATE:

        # react to events using the given config
        event = tray.read(timeout=1)
        if event in menu_config:
            menu_config[event][ACTION_CONFIG_KEY]()

        # do some action at a repeating interval
        on_interval = datetime.now().second % 5  # every minute
        if (on_interval) and (not prompted):
            handle_interval_action(tray, menu_config, watchlist)
            prompted = True
        elif not on_interval and prompted:
            prompted = False

        # give cpu time to breath
        time.sleep(0.001)


def handle_interval_action(tray, menu_config, watchlist):
    # currently only checking task list on intervals
    process_watchlist(watchlist)


# ================================================================
# Actions
# ================================================================


def do_exit():
    global ON_STATE
    ON_STATE = False


def process_watchlist(watchlist):
    # index tasks by
    task_list = get_task_list()

    # define a dictionary for how to react to each watchlist type
    watchlist_actions = {WATCHLIST_CHECKLIST_KEY: process_checklist_type}
    for watchlist_type, watchlist_type_config in watchlist.items():
        watchlist_actions[watchlist_type](watchlist_type_config, task_list)


def process_checklist_type(checklists, task_list):
    global CHECKLIST_MEMO

    for checklist in checklists:
        checklist_target_apps = checklist[utils_cl.APPS_CONFIG_KEY]
        checklist_name = checklist[utils_cl.NAME_CONFIG_KEY]

        trimmed_apps = [trim_extension(app) for app in checklist_target_apps]
        app_is_present = lhs_has_items_in_rhs(lhs=trimmed_apps, rhs=task_list)
        should_trigger = checklist_should_trigger(checklist, CHECKLIST_MEMO)

        if app_is_present and should_trigger:
            CHECKLIST_MEMO[checklist_name] = datetime.now()
            utils_cl.display(config=checklist)


def checklist_should_trigger(checklist, checklist_memo):
    # assume the checklist value is in the right TIME_FORMAT
    checklist_name = checklist[utils_cl.NAME_CONFIG_KEY]
    checklist_start = checklist[utils_cl.START_TIME_CONFIG_KEY]
    current_invocation = datetime.now()

    after_start_time = checklist_start <= current_invocation.strftime(TIME_FORMAT)
    already_triggered_today = checklist_was_triggered_today(
        checklist_name, checklist_memo
    )
    result = after_start_time and not already_triggered_today

    return result


def checklist_was_triggered_today(checklist_name, checklist_memo):
    previous_invocation_str = None
    current_invocation_str = datetime.now().strftime(DATE_FORMAT)

    if checklist_name in checklist_memo:
        previous_invocation_str = checklist_memo[checklist_name].strftime(DATE_FORMAT)

    return previous_invocation_str == current_invocation_str


# ================================================================
# Getters
# ================================================================


def get_task_list():
    p = set()

    # get list of distinct tasks
    for proc in psutil.process_iter(["name"]):
        p.add(trim_extension(proc.info["name"]))  # remove extension
    p = list(p)
    p.sort()

    return p


def get_watchlist(watchlist_path):
    watchlist_obj = {}
    with open(watchlist_path, "r") as watchlist_f:
        watchlist_content = watchlist_f.read()
        watchlist_obj = yaml.safe_load(watchlist_content)

    return watchlist_obj


# ================================================================
# Misc
# ================================================================


def lhs_has_items_in_rhs(lhs, rhs):
    result = False
    # create Aho-Corasick string matching automaton for quick lookup of rhs items in lhs
    auto = ahocorasick.Automaton()
    for substr in lhs:
        auto.add_word(substr, substr)
    auto.make_automaton()

    # go through rhs items to see if they exist in lhs (using automaton)
    for astr in rhs:

        # if the iterator has items, we have a match, so break
        for _, _ in auto.iter(astr):
            result = True
            break

    return result


def trim_extension(filename):
    return filename.lower().rsplit(".", 1)[0]


if __name__ == "__main__":
    main()

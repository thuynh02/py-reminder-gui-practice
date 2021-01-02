import os
import sys
import time
import yaml
import psutil
import ahocorasick
import cronex
from datetime import datetime
from .utils import checklist as utils_cl
from .utils import files
from .utils.system_tray import init_tray


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
    # set vars for watchlist
    watchlist_path = files.resource_path(
        relative_path=f".{os.path.sep}watchlist.yml",
        relative_to=os.path.abspath(__file__),
    )
    watchlist = get_watchlist(watchlist_path)

    # menu options to manually trigger each checklist prompt (preemptive completion)
    menu_config = {}
    for checklist in watchlist[WATCHLIST_CHECKLIST_KEY]:
        checklist_name = checklist[utils_cl.NAME_CONFIG_KEY]
        menu_config[f'Open "{checklist_name}"'] = {
            ACTION_CONFIG_KEY: lambda: do_manual_checklist(checklist),
            TIME_CONFIG_KEY: (0, 0),
        }

    # menu option to exit the watcher
    menu_config["Exit"] = {ACTION_CONFIG_KEY: do_exit, TIME_CONFIG_KEY: (0, 0)}

    # setting up the tray
    icon_path = files.resource_path(
        relative_path=f".{os.path.sep}icon.png", relative_to=os.path.abspath(__file__)
    )
    menu_options = list(menu_config.keys())
    tray = init_tray(menu_options=menu_options, icon_path=icon_path)

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
        on_interval = datetime.now().second % 10 == 0
        if (on_interval) and (not prompted):
            handle_interval_action(tray, menu_config, watchlist)
            prompted = True
        elif not on_interval and prompted:
            prompted = False

        # give cpu time to breath
        time.sleep(0.01)


def handle_interval_action(tray, menu_config, watchlist):
    # currently only checking task list on intervals
    process_watchlist(watchlist)


# ================================================================
# Actions
# ================================================================


def do_exit():
    global ON_STATE
    ON_STATE = False


def do_manual_checklist(checklist):
    global CHECKLIST_MEMO
    utils_cl.display(
        config=checklist,
        can_cancel=True,
        done_callback=lambda: update_checklist_memo(
            checklist[utils_cl.NAME_CONFIG_KEY]
        ),
    )


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
        checklist_target_apps = checklist.get(utils_cl.APPS_CONFIG_KEY, [])
        checklist_name = checklist[utils_cl.NAME_CONFIG_KEY]

        trimmed_apps = [files.trim_extension(app) for app in checklist_target_apps]
        empty_target_apps = len(trimmed_apps) == 0

        app_is_present = (
            lhs_has_items_in_rhs(lhs=trimmed_apps, rhs=task_list)
            if not empty_target_apps
            else False
        )
        should_trigger = checklist_should_trigger(checklist, CHECKLIST_MEMO)

        if (empty_target_apps or app_is_present) and should_trigger:
            utils_cl.display(
                config=checklist,
                done_callback=lambda: update_checklist_memo(checklist_name),
            )


def update_checklist_memo(checklist_name):
    global CHECKLIST_MEMO
    print(f'updating checklist memo for "{checklist_name}"')
    CHECKLIST_MEMO[checklist_name] = datetime.now()


def checklist_should_trigger(checklist, checklist_memo):
    checklist_name = checklist[utils_cl.NAME_CONFIG_KEY]
    checklist_cron = checklist[utils_cl.CRON_CONFIG_KEY]
    current_invocation = time.gmtime(time.time())[:5]

    # check if the current invocation would fall in the range of this cron expression
    cron_eval = cronex.CronExpression(checklist_cron.strip())
    should_trigger = cron_eval.check_trigger(current_invocation)

    # check if we already triggered this today
    already_triggered_today = checklist_was_triggered_today(
        checklist_name, checklist_memo
    )
    result = should_trigger and not already_triggered_today

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
        p.add(files.trim_extension(proc.info["name"]))  # remove extension
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


if __name__ == "__main__":
    main()

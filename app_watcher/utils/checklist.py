import PySimpleGUI as sg

APPS_CONFIG_KEY = "apps"
ITEMS_CONFIG_KEY = "items"
CRON_CONFIG_KEY = "cron"
NAME_CONFIG_KEY = "name"


def display(config, can_cancel=False, done_callback=None, cancel_callback=None):
    layout = []
    for item in config[ITEMS_CONFIG_KEY]:
        layout.append([sg.Checkbox(text=item, enable_events=True)])
    layout.append([sg.Exit(button_text="Done!", key="done", disabled=True)])

    if can_cancel:
        layout.append([sg.Cancel(key="cancel")])

    window = sg.Window(
        title=config[NAME_CONFIG_KEY],
        layout=layout,
        keep_on_top=True,
        disable_minimize=True,
        disable_close=True,
    )

    while True:
        event, values = window.read()
        print(event)
        if event == sg.WIN_CLOSED or event == "done":
            done_callback()
            break

        if event == "cancel":
            break

        if all([val for (key, val) in values.items()]):
            window.find_element("done").update(disabled=False)

    window.close()

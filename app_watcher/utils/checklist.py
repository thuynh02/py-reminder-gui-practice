import PySimpleGUI as sg

APPS_CONFIG_KEY = "apps"
ITEMS_CONFIG_KEY = "items"
START_TIME_CONFIG_KEY = "start_time"
NAME_CONFIG_KEY = "name"


def display(config):
    layout = []
    for item in config[ITEMS_CONFIG_KEY]:
        layout.append([sg.Checkbox(text=item, enable_events=True)])
    layout.append([sg.Exit(button_text="Done!", key="done", disabled=True)])
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
            break

        if all([val for (key, val) in values.items()]):
            window.find_element("done").update(disabled=False)

    window.close()

from flask import Flask, render_template, request  # from module import Class.


import os

import hfpy_utils
import swim_utils


app = Flask(__name__)


@app.get("/")
@app.get("/getswimmers")
def get_swimmers_names():
    files = os.listdir(swim_utils.FOLDER)
    names = set()

    for swimmer in files:
        names.add(swim_utils.get_swimmers_data(swimmer)[0])

    events = [(x, x) for x in sorted(names)]

    return render_template(
        "select.html",
        title="Select a swimmer to chart",
        label_text="Choose a swimmer:",
        data_list=events,
        action="/displayevents",
    )


@app.post("/displayevents")
def get_swimmer_events():
    chosen_name = request.form["swimmer"]
    files = os.listdir(swim_utils.FOLDER)
    events = []

    swimmer_age = 0

    for swimmer in files:
        (
            name,
            age,
            distance,
            stroke,
            the_times,
            converts,
            the_average,
        ) = swim_utils.get_swimmers_data(swimmer)
        if name == chosen_name:
            events.append((f"{swimmer}", f"{distance}-{stroke}"))

    return render_template(
        "select.html",
        title="Select a event to chart",
        label_text="Choose an event:",
        data_list=events,
        action="/chart",
    )


@app.post("/chart")
def display_chart():
    (
        name,
        age,
        distance,
        stroke,
        the_times,
        converts,
        the_average,
    ) = swim_utils.get_swimmers_data(request.form["swimmer"])

    converts.reverse()
    the_times.reverse()

    the_title = f"{name} (Under {age}) {distance} {stroke}"
    from_max = max(converts) + 50
    the_converts = [hfpy_utils.convert2range(n, 0, from_max, 0, 350) for n in converts]

    the_data = zip(the_converts, the_times)

    return render_template(
        "chart.html",
        title=the_title,
        average=the_average,
        data=the_data,
    )


if __name__ == "__main__":
    app.run(debug=True)  # Starts a local (test) webserver, and waits... forever.

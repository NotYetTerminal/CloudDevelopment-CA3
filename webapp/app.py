from flask import Flask, render_template, request  # from module import Class.


import os
import hfpy_utils
import swim_utils


app = Flask(__name__)


@app.get("/")
@app.get("/selectdate")
def select_swim_date():
    dates: list = [(x, x.strftime("%Y-%m-%d")) for x in swim_utils.query_dates()]

    return render_template(
        "select.html",
        title="Select a swim session",
        label_text="Please select a chosen_date:",
        data_list=dates,
        action="/getswimmers",
    )


@app.post("/getswimmers")
def get_swimmers_names():
    chosen_date: str = request.form["select_data"]
    swimmers: list = swim_utils.query_swimmers(chosen_date)

    return render_template(
        "select.html",
        title="Select a swimmer to chart",
        label_text="Choose a swimmer:",
        data_list=swimmers,
        action="/displayevents",
    )


@app.post("/displayevents")
def get_swimmer_events():
    date, swimmer_id = request.form["select_data"].split(";")
    events: list = swim_utils.query_events(date, int(swimmer_id))

    return render_template(
        "select.html",
        title="Select a event to chart",
        label_text="Choose an event:",
        data_list=events,
        action="/chart",
    )


@app.post("/chart")
def display_chart():
    date, swimmer_id, event_id = request.form["select_data"].split(";")
    times: list = [
        str(x[0])
        .removeprefix("0:")
        .removeprefix("0")
        .removeprefix("0:")
        .removesuffix("0000")
        for x in swim_utils.query_times(date, int(swimmer_id), int(event_id))
    ]

    converts: list = [swim_utils.convert2hundreths(x) for x in times]
    the_average: str = swim_utils.build_time_string(swim_utils.mean(converts))

    converts.reverse()
    times.reverse()

    other_data: tuple = swim_utils.query_other_data(int(swimmer_id), int(event_id))

    the_title = (
        f"{other_data[0]} (Under {other_data[1]}) {other_data[2]} {other_data[3]}"
    )
    from_max = max(converts) + 50
    the_converts = [hfpy_utils.convert2range(n, 0, from_max, 0, 350) for n in converts]

    the_data = zip(the_converts, times)

    return render_template(
        "chart.html",
        title=the_title,
        average=the_average,
        data=the_data,
    )


if __name__ == "__main__":
    app.run(debug=True)  # Starts a local (test) webserver, and waits... forever.

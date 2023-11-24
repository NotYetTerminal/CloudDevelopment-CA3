from flask import Flask, render_template, request  # from module import Class.


import os
import DBcm
import hfpy_utils
import swim_utils


config = {
    "user": "swimuser",
    "password": "swimuserpasswd",
    "database": "SwimclubDB",
    "host": "localhost",
}


app = Flask(__name__)


@app.get("/")
@app.get("/selectdate")
def select_swim_date():
    convert2hundreths(3)
    dates: list = [(x.split(" ")[0], x) for x in query_dates()]

    return render_template(
        "select.html",
        title="Select a swim session",
        label_text="Please select a chosen_date:",
        data_list=dates,
        action="/getswimmers",
    )


@app.get("/getswimmers")
def get_swimmers_names():
    chosen_date: str = request.form["select_data"]
    swimmers: list = query_swimmers(chosen_date)

    return render_template(
        "select.html",
        title="Select a swimmer to chart",
        label_text="Choose a swimmer:",
        data_list=swimmers,
        action="/displayevents",
    )


@app.post("/displayevents")
def get_swimmer_events():
    date, swimmer_id = request.form["select_data"].split("-")
    events: list = query_events(date, int(swimmer_id))

    return render_template(
        "select.html",
        title="Select a event to chart",
        label_text="Choose an event:",
        data_list=events,
        action="/chart",
    )


@app.post("/chart")
def display_chart():
    date, swimmer_id, event_id = request.form["select_data"].split("-")
    times: list = query_events(date, int(swimmer_id), int(event_id))

    converts: list = [convert2hundreths(x.removeprefix("00:")) for x in times]
    average: str = build_time_string(mean(converts))

    converts.reverse()
    times.reverse()

    the_title = f"{name} (Under {age}) {distance} {stroke}"
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

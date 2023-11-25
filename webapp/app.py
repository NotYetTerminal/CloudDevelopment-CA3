from flask import Flask, render_template, request  # from module import Class.


import os
import hfpy_utils
import swim_utils


app = Flask(__name__)


@app.get("/")
def run_all_app():
    select_names: list = ["select_date", "select_swimmer", "select_event"]
    label_texts: list = ["Choose a date:", "Choose a swimmer:", "Choose an event:"]
    datas: list = [
        [[x, x.strftime("%Y-%m-%d")] for x in swim_utils.query_dates()],
        [["", ""]],
        [["", ""]],
    ]
    datas[0].insert(0, ("", "Select date"))
    actions: list = ["select_swimmer", "select_event", "chart"]
    data = zip(select_names, label_texts, datas, actions)

    return render_template(
        "all.html",
        title="Generate chart for swimmer",
        data_list=data,
    )


@app.get("/select_swimmer")
def get_swimmers_names():
    chosen_date: str = dict(request.args)["select_date"]
    if chosen_date != "":
        swimmers: list = swim_utils.query_swimmers(chosen_date)
        swimmers.insert(0, ["", "Select swimmer"])
    else:
        swimmers: list = [["", ""]]

    return render_template(
        "options.html",
        data_list=swimmers,
    )


@app.get("/select_event")
def get_swimmer_events():
    data = dict(request.args)["select_swimmer"]
    if data != "":
        date, swimmer_id = data.split(";")
        events: list = swim_utils.query_events(date, int(swimmer_id))
        events.insert(0, ["", "Select event"])
    else:
        events: list = [["", ""]]

    return render_template(
        "options.html",
        data_list=events,
    )


@app.get("/chart")
def display_chart():
    data = dict(request.args)["select_event"]
    times: list = []
    if data != "":
        date, swimmer_id, event_id = data.split(";")

        for value in swim_utils.query_times(date, int(swimmer_id), int(event_id)):
            value = (
                str(value[0])
                .removeprefix("0:")
                .removeprefix("0")
                .removeprefix("0:")
                .removesuffix("0000")
            )
            if "." not in value:
                value += ".00"
            times.append(value)

        if len(times) != 0:
            converts: list = [swim_utils.convert2hundreths(x) for x in times]
            the_average: str = swim_utils.build_time_string(swim_utils.mean(converts))

            converts.reverse()
            times.reverse()

            from_max = max(converts) + 50
            the_converts = [
                hfpy_utils.convert2range(n, 0, from_max, 0, 350) for n in converts
            ]

            other_data: tuple = swim_utils.query_other_data(
                int(swimmer_id), int(event_id)
            )

            the_title: str = f"{other_data[0]} (Under {other_data[1]}) {other_data[2]} {other_data[3]} - {date.split(' ')[0]}"
        else:
            the_converts: list = []
            the_average: str = ""
            the_title: str = "Select all fields"
    else:
        the_converts: list = []
        the_average: str = ""
        the_title: str = "Select all fields"

    the_data = zip(the_converts, times)

    return render_template(
        "chart.html",
        chart_title=the_title,
        average=the_average,
        chart_data=the_data,
    )


if __name__ == "__main__":
    app.run(debug=True)  # Starts a local (test) webserver, and waits... forever.

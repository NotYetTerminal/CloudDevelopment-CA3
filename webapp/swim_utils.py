from statistics import mean


import DBcm
import hfpy_utils


def convert2hundreths(timestring):
    """Given a string which represents a time, this function converts the string
    to a number (int) representing the string's hundredths of seconds value, which is
    returned.
    """
    if ":" in timestring:
        mins, rest = timestring.split(":")
        secs, hundredths = rest.split(".")
    else:
        mins = 0
        secs, hundredths = timestring.split(".")

    return int(hundredths) + (int(secs) * 100) + ((int(mins) * 60) * 100)


def build_time_string(num_time):
    """ """
    secs, hundredths = str(round(num_time / 100, 2)).split(".")
    mins = int(secs) // 60
    seconds = int(secs) - mins * 60
    return f"{mins}:{seconds}.{hundredths}"


def get_swimmers_data(filename):
    """ """
    name, age, distance, stroke = filename.removesuffix(".txt").split("-")
    name = name.split("/")[-1]
    with open(filename) as fh:
        data = fh.read()
    times = data.strip().split(",")
    converts = []  # empty list
    for t in times:
        converts.append(convert2hundreths(t))
    average = build_time_string(mean(converts))

    return name, age, distance, stroke, times, converts, average


config = {
    "user": "swimuser",
    "password": "swimuserpasswd",
    "database": "SwimclubDB",
    "host": "localhost",
}


def query_dates() -> list:
    SQL: str = f""" SELECT DISTINCT ts FROM times;"""
    with DBcm.UseDatabase(config) as db:
        db.execute(SQL)
        data: list = db.fetchall()

    return [row[0] for row in data]


def query_swimmers(date) -> list:
    SQL: str = f""" SELECT DISTINCT swimmers.swimmer_id, name, age
                    FROM swimmers
                    INNER JOIN times ON times.swimmer_id = swimmers.swimmer_id
                    WHERE times.ts = "{date}"
                    ORDER BY name;"""

    with DBcm.UseDatabase(config) as db:
        db.execute(SQL)
        data: list = db.fetchall()

    return [[date + ";" + str(row[0]), row[1] + "-" + str(row[2])] for row in data]


def query_events(date, swimmer_id: int) -> list:
    SQL: str = f""" SELECT DISTINCT events.event_id, distance, stroke
                    FROM events
                    INNER JOIN times ON times.event_id = events.event_id
                    INNER JOIN swimmers ON swimmers.swimmer_id = times.swimmer_id
                    WHERE times.ts = "{date}" AND times.swimmer_id = {swimmer_id}
                    ORDER BY distance;"""

    with DBcm.UseDatabase(config) as db:
        db.execute(SQL)
        data: list = db.fetchall()

    return [
        [date + ";" + str(swimmer_id) + ";" + str(row[0]), row[1] + "-" + str(row[2])]
        for row in data
    ]


def query_times(date, swimmer_id: int, event_id: int) -> list:
    SQL: str = f""" SELECT time
                    FROM times
                    INNER JOIN events ON events.event_id = times.event_id 
                    INNER JOIN swimmers ON swimmers.swimmer_id = times.swimmer_id
                    WHERE times.ts = "{date}" AND times.swimmer_id = {swimmer_id} AND times.event_id = {event_id};"""

    with DBcm.UseDatabase(config) as db:
        db.execute(SQL)
        data: list = db.fetchall()

    return data


def query_other_data(swimmer_id: int, event_id: int) -> tuple:
    SQL: str = f""" SELECT DISTINCT name, age, distance, stroke
                    FROM times
                    INNER JOIN events ON events.event_id = times.event_id 
                    INNER JOIN swimmers ON swimmers.swimmer_id = times.swimmer_id
                    WHERE times.swimmer_id = {swimmer_id} AND times.event_id = {event_id};"""

    with DBcm.UseDatabase(config) as db:
        db.execute(SQL)
        data: list = db.fetchall()

    return data[0]

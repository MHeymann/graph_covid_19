#! /usr/bin/python3

import sys
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import Locator as locator
import numpy as np

### Constants ##################################################################

POS = "pos"
TESTS = "tests"
POSTESTS = "postests"
RECOV = "recov"
DEATHS = "deaths"
GRAPH_TYPES = np.array([POS, TESTS, POSTESTS, RECOV, DEATHS])

### Commandline Arguments ######################################################

def get_default_settings():
    settings = {}

    settings["graphtype"] = "cummulative"
    settings["yscale"] = "log"
    settings["dataset"] = POS
    settings["filename"] = "covid19_tests.txt"
    settings["n_day_av"] = 1
    settings["start_date"] = None
    settings["end_date"] = None


    return settings

def check_graph_type(arg):
    if arg == "cummulative" or \
            arg == "daily":
        return True
    else:
        print("Unknown argument for graph type: " + arg)
        return False

def check_graph_yscale(arg):
    if arg == "log" or \
            arg == "linear":
        return True
    else:
        print("Unknown argument for graph y scale: " + arg)
        return False

def check_graph_data_set(arg):
    if arg in GRAPH_TYPES:
        return True
    else:
        print("Unknown argument for graph data set: " + arg)
        return False
def check_source_filename(arg):
    if not os.path.exists() or not os.path.isfile():
        print("Not a valid file: " + arg)
        return False
    else:
        return True

def check_n_day_av(arg):
    try:
        n = int(arg)
    except ValueError:
        print("Please provide a valid integer argument for the rolling average")
        return False
    if n < 1:
        print("Please provide a positive integer argument for the rolling average")
        return False
    return True

def check_date_arg(arg):
    try:
        datetime.datetime.strptime(arg,"%d-%m-%Y").date()
    except ValueError:
        print("Bad date format")
        return False
    return True

def parse_args(argv):
    settings = get_default_settings()

    i = 1
    while i < len(argv):
        arg = argv[i].strip().split("=")
        if arg[0] == "graphtype" and check_graph_type(arg[1]):
            settings["graphtype"] = arg[1]
        elif arg[0] == "yscale" and check_graph_yscale(arg[1]):
            settings["yscale"] = arg[1]
        elif arg[0] == "dataset" and check_graph_data_set(arg[1]):
            settings["dataset"] = arg[1]
        elif arg[0] == "filename" and check_source_filename(arg[1]):
            settings["filename"] = arg[1]
        elif arg[0] == "n_day_av" and check_n_day_av(arg[1]):
            try:
                settings["n_day_av"] = int(arg[1])
            except ValueError:
                print("Well this is weird... " + arg[1])
                settings["n_day_av"] = 1
        elif arg[0] == "start_date" and check_date_arg(arg[1]):
            settings["start_date"] = \
                    datetime.datetime.strptime(arg[1],"%d-%m-%Y").date()
        elif arg[0] == "end_date" and check_date_arg(arg[1]):
            settings["end_date"] = \
                    datetime.datetime.strptime(arg[1],"%d-%m-%Y").date()

        i = i + 1

    return settings

### Data processing ############################################################

def parse_data(filename):
    dates = np.array([])
    tests = {}
    posit = {}
    deaths = {}
    recov = {}

    curr_date = ""
    with open (filename, "r") as f:
        line = f.readline()
        while not line == "":
            data = line.split("\t")
            if (data[0].strip() == "Entry:"):
                curr_date = ""
            if data[0].strip() == "date":
                curr_date = data[1].strip()
                if not curr_date == "":
                    dates = np.append(dates, curr_date)
            elif (data[0].strip() == TESTS):
                if not curr_date == "":
                    tests[curr_date] = data[1].strip()
            elif (data[0].strip() == POS):
                if not curr_date == "":
                    posit[curr_date] = data[1].strip()
            elif (data[0].strip() == DEATHS):
                if not curr_date == "":
                    deaths[curr_date] = data[1].strip()
            elif (data[0].strip() == RECOV):
                if not curr_date == "":
                    recov[curr_date] = data[1].strip()
            line = f.readline()
    ret_data = {}
    ret_data["dates"] = dates
    ret_data[TESTS] = tests
    ret_data[POS] = posit
    ret_data[DEATHS] = deaths
    ret_data[RECOV] = recov

    return ret_data

def get_n_day_av(data, settings):
    ret_data = np.array([])
    sum = 0
    n = 0;

    if len(data) < settings["n_day_av"]:
        last_date = None
        last_date_str = None
        for d in data:
            try:
                sum = sum + d
            except ValueError:
                print("bad value in data")
                continue
            n = n + 1
        ret_data = np.array([sum / n])
    else:
        vals = np.zeros(settings["n_day_av"])
        for d in data:
            i = len(vals) - 1
            while i > 0:
                vals[i] = vals[i - 1]
                i = i - 1
            vals[0] = d
            n = n + 1
            if n < settings["n_day_av"]:
                continue
            sum = 0
            for v in vals:
                sum = sum + v

            ret_data = np.append(ret_data, sum / settings["n_day_av"])
    return ret_data

def convert_date(sdate):
    try:
        # check date format
        d = datetime.datetime.strptime(sdate,"%d-%m-%Y").date()
    except ValueError:
        print("bad date format")
        print(sdate)
        return None
    return d


def is_date_valid_range(date, settings):
    if (not settings["start_date"] == None) and \
            (d < settings["start_date"]):
        return False
    if (not settings["end_date"] == None) and \
            (d > settings["end_date"]):
        return False
    return True

def get_pos_tests_data(data, settings):
    x_data =  np.array([])
    pos_data =  np.array([])
    tst_data =  np.array([])

    prev_tsts = 0
    prev_pos = 0

    for t in data["dates"]:
        d = convert_date(t)
        if d == None:
            continue

        if not is_date_valid_range(d, settings):
            continue

        if not t in data[POS] or not t in data[TESTS]:
            continue
        try:
            tsts = int(data[TESTS][t])
            pos = int(data[POS][t])
        except ValueError:
            continue

        if settings["graphtype"] == "daily":
            cur_pos = pos
            cur_tst = tsts
            pos = pos - prev_pos
            tsts = tsts - prev_tsts
            prev_pos = cur_pos
            prev_tsts = cur_tst
        if tsts == 0:
            continue
        pos_data = np.append(pos_data, pos)
        tst_data = np.append(tst_data, tsts)
        x_data = np.append(x_data, d)

    if settings["n_day_av"] > 1:
        pos_data = get_n_day_av(pos_data, settings)
        tst_data = get_n_day_av(tst_data, settings)
        x_data = x_data[settings["n_day_av"] -1:]
    return x_data, pos_data / tst_data

def get_std_data(data, settings):
    x_data =  np.array([])
    y_data =  np.array([])

    prev_y = 0

    for t in data["dates"]:
        d = convert_date(t)
        if d == None:
            continue

        if not is_date_valid_range(d, settings):
            continue

        if not t in data[settings["dataset"]]:
            continue
        try:
            y = int(data[settings["dataset"]][t])
        except ValueError:
            continue

        if settings["graphtype"] == "daily":
            y_data = np.append(y_data, y - prev_y)
            prev_y = y
        else:
            y_data = np.append(y_data, y)

        x_data = np.append(x_data, d)
    if settings["n_day_av"] > 1:
        y_data = get_n_day_av(y_data, settings)
        x_data = x_data[settings["n_day_av"] -1:]
    return x_data, y_data


def get_plot_data(data, settings):

    if settings["dataset"] == POSTESTS:
        x_data, y_data = get_pos_tests_data(data, settings)
    else:
        x_data, y_data = get_std_data(data, settings)

    return x_data, y_data

def print_data(data):
    for d in data["dates"]:
        print("Entry:")
        print("date\t" + d)
        if d in data[TESTS]:
            print("tests\t" + data[TESTS][d])
        if d in data[POS]:
            print("pos\t" + data[POS][d])
        if d in data[DEATHS]:
            print("deaths\t" + data[DEATHS][d])
        if d in data[RECOV]:
            print("recov\t" + data[RECOV][d])
        print()

def get_png_name(data):
    name = data["dataset"]
    name = name + "_" + data["graphtype"]
    name = name + "_" + data["yscale"]
    if not data["n_day_av"] == 1:
        name = name + "_" + str(data["n_day_av"]) + "_day_av"
    name = name + "_" + data["x_data"][0].strftime(data["dateformat"])
    name = name + "_" + data["x_data"][-1].strftime(data["dateformat"])

    return name

### Plotting Procedures ########################################################

def plot_data(data):

    #ax = plt.gca() # get axis
    fig, ax = plt.subplots()
    formatter = mdates.DateFormatter(data["dateformat"])
    ax.xaxis.set_major_formatter(formatter)

    #locator = mdates.DayLocator(interval=1)
    locator = mdates.WeekdayLocator(byweekday=mdates.MO)

    ax.xaxis.set_major_locator(locator)

    ax.plot(data["x_data"], data["y_data"]);
    ax.set_title(data["heading"])
    ax.set_ylabel(data["y_legend"])
    ax.set_xlabel(data["x_legend"])
    ax.grid()
    ax.set_yscale(data["yscale"])
    fig.autofmt_xdate()
    fig.savefig(get_png_name(data))
    #plt.show()

def get_legend_heading(settings):
    if settings["graphtype"] == "cummulative":
        first_word = "Cummulative "
    elif settings["graphtype"] == "daily":
        first_word = "Daily "
    else:
        first_word = ""

    if settings["yscale"] == "log":
        log_note = "\n(Log Graph)"
    else:
        log_note = ""

    if settings["n_day_av"] > 1:
        av_note = " (" + str(settings["n_day_av"]) +" Day Average)"
    else:
        av_note = ""

    if settings["dataset"] == TESTS:
        heading = first_word + \
                "Covid-19 Tests Performed to Date in South Africa" + log_note
        y_leg = "Tests Performed"
    elif settings["dataset"] == POS:
        heading = first_word + \
                "Covid-19 Confirmed Cases to Date in South Africa" + log_note
        y_leg = "Confirmed Cases"
    elif settings["dataset"] == POSTESTS:
        heading = first_word + \
                "Covid-19 proportion of Tests Positive to Date in South Africa" \
                + log_note
        y_leg = "Proportion Positive"
    elif settings["dataset"] == DEATHS:
        heading = first_word + \
                "Covid-19 Confirmed Deaths to Date in South Africa" + log_note
        y_leg = "Confirmed Deaths"
    elif settings["dataset"] == RECOV:
        heading = first_word + \
                "Covid-19 Confirmed Recoveries to Date in South Africa" + \
                log_note
        y_leg = "Confirmed Recoveries"
    else:
        print("please give valid plotting data")
        return None, None
    y_leg = y_leg + av_note
    return y_leg, heading

### Main Function ##############################################################

if __name__ == "__main__":
    settings = parse_args(sys.argv)
    data = parse_data(settings["filename"])

    y_leg, heading = get_legend_heading(settings)
    if y_leg == None or heading == None:
        print("didn't get heading or legend")
        exit()
    x_leg = "Date"

    x_data, y_data = get_plot_data(data, settings)

    y_data = [y for _,y in sorted(zip(x_data, y_data))]
    x_data = sorted(x_data)

    p_data = {}
    p_data["x_data"] = x_data
    p_data["y_data"] = y_data
    p_data["x_legend"] = x_leg
    p_data["y_legend"] = y_leg
    p_data["heading"] = heading
    p_data["yscale"] = settings["yscale"]
    p_data["dataset"] = settings["dataset"]
    p_data["graphtype"] = settings["graphtype"]
    p_data["n_day_av"] = settings["n_day_av"]
    p_data["start_date"] = settings["start_date"]
    p_data["end_date"] = settings["end_date"]

    p_data["dateformat"] = "%Y-%m-%d"


    plot_data(p_data)

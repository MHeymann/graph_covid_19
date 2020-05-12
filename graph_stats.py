#! /usr/bin/python3

import sys
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import Locator as locator
import numpy as np

### Commandline Arguments ######################################################

def get_default_settings():
    settings = {}

    settings["graphtype"] = "cummulative"
    settings["yscale"] = "log"
    settings["dataset"] = "pos"
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
    if arg == "pos" or \
            arg == "tests" or \
            arg == "recov" or \
            arg == "deaths":
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
    dates = []
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
                    dates = dates + [curr_date]
            elif (data[0].strip() == "tests"):
                if not curr_date == "":
                    tests[curr_date] = data[1].strip()
            elif (data[0].strip() == "pos"):
                if not curr_date == "":
                    posit[curr_date] = data[1].strip()
            elif (data[0].strip() == "deaths"):
                if not curr_date == "":
                    deaths[curr_date] = data[1].strip()
            elif (data[0].strip() == "recov"):
                if not curr_date == "":
                    recov[curr_date] = data[1].strip()
            line = f.readline()
    ret_data = {}
    ret_data["dates"] = dates
    ret_data["tests"] = tests
    ret_data["pos"] = posit
    ret_data["deaths"] = deaths
    ret_data["recov"] = recov

    return ret_data

def get_n_day_av(data, settings):
    ret_data = []
    sum = 0
    n = 0;

    if len(data) < settings["n_day_av"]:
        last_date = None
        last_date_str = None
        for d in data:
            try:
                sum = sum + int(d)
            except ValueError:
                print("bad value in data")
                continue
            n = n + 1
        ret_data = [sum / n]
    else:
        vals = np.zeros(settings["n_day_av"])
        for d in data:
            try:
                val = int(d)
            except ValueError:
                print("bad value in data")
                continue
            # valid data
            i = len(vals) - 1
            while i > 0:
                vals[i] = vals[i - 1]
                i = i - 1
            vals[0] = val
            n = n + 1
            if n < settings["n_day_av"]:
                continue
            sum = 0
            for v in vals:
                sum = sum + v

            ret_data = ret_data + [sum / settings["n_day_av"]]
    return ret_data

def get_plot_data(data, settings):
    x_data =  []
    y_data =  []

    prev_y = 0

    for t in data["dates"]:
        if not t in data[settings["dataset"]]:
            continue
        try:
            y = int(data[settings["dataset"]][t])
        except ValueError:
            continue
        try:
            # check date format
            d = datetime.datetime.strptime(t,"%d-%m-%Y").date()
        except ValueError:
            print("bad date format")
            print(t)
            continue

        if (not settings["start_date"] == None) and \
                (d < settings["start_date"]):
            continue
        if (not settings["end_date"] == None) and \
                (d > settings["end_date"]):
            continue

        if settings["graphtype"] == "daily":
            y_data = y_data + [y - prev_y]
            prev_y = y
        else:
            y_data = y_data + [y]
        x_data = x_data + [d]

    if settings["n_day_av"] > 1:
        y_data = get_n_day_av(y_data, settings)
        x_data = x_data[settings["n_day_av"] -1:]
    return x_data, y_data

def print_data(data):
    for d in data["dates"]:
        print("Entry:")
        print("date\t" + d)
        if d in data["tests"]:
            print("tests\t" + data["tests"][d])
        if d in data["pos"]:
            print("pos\t" + data["pos"][d])
        if d in data["deaths"]:
            print("deaths\t" + data["deaths"][d])
        if d in data["recov"]:
            print("recov\t" + data["recov"][d])
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

    if settings["dataset"] == "tests":
        heading = first_word + \
                "Covid-19 Tests Performed to Date in South Africa" + log_note
        y_leg = "Tests Performed"
    elif settings["dataset"] == "pos":
        heading = first_word + \
                "Covid-19 Confirmed Cases to Date in South Africa" + log_note
        y_leg = "Confirmed Cases"
    elif settings["dataset"] == "deaths":
        heading = first_word + \
                "Covid-19 Confirmed Deaths to Date in South Africa" + log_note
        y_leg = "Confirmed Deaths"
    elif settings["dataset"] == "recov":
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

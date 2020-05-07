#! /usr/bin/python3

import sys
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import Locator as locator
import numpy as np

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

def parse_args(argv):
    settings = {}
    settings["graph_type"] = "cummulative"
    settings["yscale"] = "log"
    settings["dataset"] = "pos"
    settings["filename"] = "covid19_tests.txt"
    settings["n_day_av"] = 1

    i = 1
    while i < len(argv):
        arg = argv[i].strip().split("=")
        if arg[0] == "graph_type" and check_graph_type(arg[1]):
            settings["graph_type"] = arg[1]
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
        i = i + 1

    return settings

def parse_data(filename):
    dates = []
    tests = {}
    posit = {}
    deaths = {}
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
            elif (data[0].strip() == ""):
                pass
            line = f.readline()
    ret_data = {}
    ret_data["dates"] = dates
    ret_data["tests"] = tests
    ret_data["pos"] = posit
    ret_data["deaths"] = deaths

    return ret_data

def plot_data(data):

    ax = plt.gca() # get axis
    ax.set_yscale(data["yscale"])
    formatter = mdates.DateFormatter(data["date_format"])
    ax.xaxis.set_major_formatter(formatter)

    locator = mdates.DayLocator(interval=1)

    ax.xaxis.set_major_locator(locator)

    ax.tick_params(axis='x', rotation=90)
    plt.plot(data["x_data"], data["y_data"]);
    plt.title(data["heading"])
    plt.ylabel(data["y_legend"])
    plt.xlabel(data["x_legend"])
    plt.show()

def print_data(data):
    for d in data["dates"]:
        print("Entry:")
        print("date\t" + d)
        print("tests\t" + data["tests"][d])
        print("pos\t" + data["pos"][d])
        print("deaths\t" + data["deaths"][d])
        print()

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
            # valid data, valid date
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


def get_legend_heading(settings):
    if settings["graph_type"] == "cummulative":
        first_word = "Cummulative "
    else:
        first_word = "Daily "

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
    else:
        print("please give valid plotting data")
        return None, None
    y_leg = y_leg + av_note
    return y_leg, heading


def get_plot_data(data, settings):
    x_data =  []
    y_data =  []

    prev_y = 0

    for t in data["dates"]:
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

        if settings["graph_type"] == "daily":
            y_data = y_data + [y - prev_y]
            prev_y = y
        else:
            y_data = y_data + [y]
        x_data = x_data + [d]

    if settings["n_day_av"] > 1:
        y_data = get_n_day_av(y_data, settings)
        x_data = x_data[settings["n_day_av"] -1:]
    return x_data, y_data


if __name__ == "__main__":
    settings = parse_args(sys.argv)
    data = parse_data(settings["filename"])

    y_leg, heading = get_legend_heading(settings)
    if y_leg == None or heading == None:
        print("didn't get heading or legend")
        exit()
    x_leg = "Date"

    x_data, y_data = get_plot_data(data, settings)

    p_data = {}
    p_data["x_data"] = x_data
    p_data["y_data"] = y_data
    p_data["x_legend"] = x_leg
    p_data["y_legend"] = y_leg
    p_data["heading"] = heading
    p_data["yscale"] = settings["yscale"]
    p_data["date_format"] = "%Y-%m-%d"


    plot_data(p_data)

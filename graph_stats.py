#! /usr/bin/python3

import sys
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import Locator as locator
import numpy as np

### Constants ##################################################################

DATE = "date"
POS = "pos"
TESTS = "tests"
POSTESTS = "postests"
RECOV = "recov"
DEATHS = "deaths"
ACTIVE = "active"

GRAPHTYPE = "graphtype"
YSCALE = "yscale"
DATASET = "dataset"
FILENAME = "filename"
N_DAY_AV = "n_day_av"
START_DATE = "start_date"
END_DATE = "end_date"

TOTAL = "total"
LOG = "log"
LINEAR = "linear"
DAILY = "daily"

DATEFORMAT = "dateformat"
X_DATA = "x_data"
Y_DATA = "y_data"
X_LEGEND = "x_legend"
Y_LEGEND = "y_legend"
HEADING = "heading"

DATA_SETS = np.array([POS, TESTS, RECOV, DEATHS, POSTESTS, ACTIVE])
GRAPHTYPE_OPTS = np.array([TOTAL, DAILY])
YSCALE_OPTS = np.array([LOG, LINEAR])

DEFAULT_FILENAME = "covid19_tests.txt"
DFORMAT_YEAR_FRST = "%Y-%m-%d"
DFORMAT_YEAR_LST = "%d-%m-%Y"

### Commandline Arguments ######################################################

def get_default_settings():
    settings = {}

    settings[GRAPHTYPE] = TOTAL
    settings[YSCALE] = LOG
    settings[DATASET] = POS
    settings[FILENAME] = DEFAULT_FILENAME
    settings[N_DAY_AV] = 1
    settings[START_DATE] = None
    settings[END_DATE] = None


    return settings

def std_check_string_arg(arg, valids, descript):
    if arg in valids:
        return True
    else:
        print("Unknown argument for " + descript + ": " + arg)
        return False

def check_graph_type(arg):
    return std_check_string_arg(arg, GRAPHTYPE_OPTS, "graph type")

def check_graph_yscale(arg):
    return std_check_string_arg(arg, YSCALE_OPTS, "graph y scale")

def check_graph_data_set(arg):
    return std_check_string_arg(arg, DATA_SETS, "graph data set")

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
        datetime.datetime.strptime(arg, DFORMAT_YEAR_FRST).date()
    except ValueError:
        print("Bad date format")
        return False
    return True

def parse_args(argv):
    settings = get_default_settings()

    i = 1
    while i < len(argv):
        arg = argv[i].strip().split("=")
        if arg[0] == GRAPHTYPE and check_graph_type(arg[1]):
            settings[GRAPHTYPE] = arg[1]
        elif arg[0] == YSCALE and check_graph_yscale(arg[1]):
            settings[YSCALE] = arg[1]
        elif arg[0] == DATASET and check_graph_data_set(arg[1]):
            settings[DATASET] = arg[1]
        elif arg[0] == FILENAME and check_source_filename(arg[1]):
            settings[FILENAME] = arg[1]
        elif arg[0] == N_DAY_AV and check_n_day_av(arg[1]):
            try:
                settings[N_DAY_AV] = int(arg[1])
            except ValueError:
                print("Well this is weird... " + arg[1])
                settings[N_DAY_AV] = 1
        elif arg[0] == START_DATE and check_date_arg(arg[1]):
            settings[START_DATE] = \
                    datetime.datetime.strptime(arg[1], DFORMAT_YEAR_FRST).date()
        elif arg[0] == END_DATE and check_date_arg(arg[1]):
            settings[END_DATE] = \
                    datetime.datetime.strptime(arg[1], DFORMAT_YEAR_FRST).date()

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
            if data[0].strip() == DATE:
                curr_date = data[1].strip()
                if not curr_date == "":
                    dates = np.append(dates, curr_date)
            elif (data[0].strip() == TESTS):
                if not curr_date == "":
                    tests[curr_date] = data[1].replace(" ", "")
            elif (data[0].strip() == POS):
                if not curr_date == "":
                    posit[curr_date] = data[1].replace(" ", "")
            elif (data[0].strip() == DEATHS):
                if not curr_date == "":
                    deaths[curr_date] = data[1].replace(" ", "")
            elif (data[0].strip() == RECOV):
                if not curr_date == "":
                    recov[curr_date] = data[1].replace(" ", "")
            line = f.readline()
    ret_data = {}
    ret_data[DATE] = dates
    ret_data[TESTS] = tests
    ret_data[POS] = posit
    ret_data[DEATHS] = deaths
    ret_data[RECOV] = recov

    return ret_data

def get_n_day_av(data, settings):
    ret_data = np.array([])
    sum = 0
    n = 0;

    if len(data) < settings[N_DAY_AV]:
        last_date = None
        last_date_str = None
        for d in data:
            try:
                sum = sum + d
            except ValueError:
                print("bad value in data")
                continue
            n = n + 1
        if n == 0:
            n = 1
        ret_data = np.array([sum / n])
    else:
        vals = np.zeros(settings[N_DAY_AV])
        for d in data:
            i = len(vals) - 1
            while i > 0:
                vals[i] = vals[i - 1]
                i = i - 1
            vals[0] = d
            n = n + 1
            if n < settings[N_DAY_AV]:
                continue
            sum = 0
            for v in vals:
                sum = sum + v

            ret_data = np.append(ret_data, sum / settings[N_DAY_AV])
    return ret_data

def convert_date(sdate):
    try:
        # check date format
        d = datetime.datetime.strptime(sdate, DFORMAT_YEAR_LST).date()
    except ValueError as e:
        print(e)
        print("bad date format")
        print(DFORMAT_YEAR_LST)
        print(sdate)
        return None
    return d


def is_date_valid_range(date, settings):
    if (not settings[START_DATE] == None) and \
            (date < settings[START_DATE]):
        return False
    if (not settings[END_DATE] == None) and \
            (date > settings[END_DATE]):
        return False
    return True

def get_pos_tests_data(data, settings):
    x_data =  np.array([])
    pos_data =  np.array([])
    tst_data =  np.array([])

    prev_tsts = 0
    prev_pos = 0

    for t in data[DATE]:
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
        except ValueError as e:
            print("ValueError")
            print(e)
            continue

        if settings[GRAPHTYPE] == DAILY:
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

    if settings[N_DAY_AV] > 1:
        if settings[N_DAY_AV] > len(pos_data):
            n = len(pos_data)
        else:
            n = settings[N_DAY_AV]
        pos_data = get_n_day_av(pos_data, settings)
        tst_data = get_n_day_av(tst_data, settings)
        x_data = x_data[n -1:]
    return x_data, pos_data / tst_data

def get_active_data(data, settings):
    x_data =  np.array([])
    y_data =  np.array([])

    prev_active = -1

    for t in data[DATE]:
        d = convert_date(t)
        if d == None:
            continue

        if not is_date_valid_range(d, settings):
            continue

        if not t in data[POS] or not t in data[RECOV]:
            continue
        try:
            recov = int(data[RECOV][t])
            pos = int(data[POS][t])
        except ValueError as e:
            print("ValueError")
            print(e)
            continue

        active = pos - recov
        if active < 0:
            print("negative active cases!!!")
            continue

        if settings[GRAPHTYPE] == DAILY:
            if prev_active < 0:
                prev_active = active
                continue
            y_data = np.append(y_data, active - prev_active)
            prev_active = active
        else:
            y_data = np.append(y_data, active)

        x_data = np.append(x_data, d)
    if settings[N_DAY_AV] > 1:
        if settings[N_DAY_AV] > len(y_data):
            n = len(y_data)
        else:
            n = settings[N_DAY_AV]
        y_data = get_n_day_av(y_data, settings)
        x_data = x_data[n -1:]
    return x_data, y_data


def get_std_data(data, settings):
    x_data =  np.array([])
    y_data =  np.array([])

    prev_y = 0

    for t in data[DATE]:
        d = convert_date(t)
        if d == None:
            continue

        if not is_date_valid_range(d, settings):
            continue

        if not t in data[settings[DATASET]]:
            continue
        try:
            y = int(data[settings[DATASET]][t])
        except ValueError as e:
            print("ValueError")
            print(e)
            continue

        if settings[GRAPHTYPE] == DAILY:
            y_data = np.append(y_data, y - prev_y)
            prev_y = y
        else:
            y_data = np.append(y_data, y)

        x_data = np.append(x_data, d)
    if settings[N_DAY_AV] > 1:
        if settings[N_DAY_AV] > len(y_data):
            n = len(y_data)
        else:
            n = settings[N_DAY_AV]
        y_data = get_n_day_av(y_data, settings)
        x_data = x_data[n -1:]
    return x_data, y_data


def get_plot_data(data, settings):

    if settings[DATASET] == POSTESTS:
        x_data, y_data = get_pos_tests_data(data, settings)
    elif settings[DATASET] == ACTIVE:
        x_data, y_data = get_active_data(data, settings)
    else:
        x_data, y_data = get_std_data(data, settings)

    return x_data, y_data

def print_data(data):
    for d in data[DATE]:
        print("Entry:")
        print(DATE + "\t" + d)
        if d in data[TESTS]:
            print(TESTS + "\t" + data[TESTS][d])
        if d in data[POS]:
            print(POS + "\t" + data[POS][d])
        if d in data[DEATHS]:
            print(DEATHS + "\t" + data[DEATHS][d])
        if d in data[RECOV]:
            print(RECOV + "\t" + data[RECOV][d])
        print()

def get_png_name(data):
    name = data[DATASET]
    name = name + "_" + data[GRAPHTYPE]
    name = name + "_" + data[YSCALE]
    if not data[N_DAY_AV] == 1:
        name = name + "_" + str(data[N_DAY_AV]) + "_day_av"
    name = name + "_" + data[X_DATA][0].strftime(data[DATEFORMAT])
    name = name + "_" + data[X_DATA][-1].strftime(data[DATEFORMAT])

    return name

### Plotting Procedures ########################################################

def plot_data(data):

    #ax = plt.gca() # get axis
    fig, ax = plt.subplots()
    formatter = mdates.DateFormatter(data[DATEFORMAT])
    ax.xaxis.set_major_formatter(formatter)

    #locator = mdates.DayLocator(interval=1)
    locator = mdates.WeekdayLocator(byweekday=mdates.MO, interval=2)

    ax.xaxis.set_major_locator(locator)

    ax.plot(data[X_DATA], data[Y_DATA]);
    ax.set_title(data[HEADING])
    ax.set_ylabel(data[Y_LEGEND])
    ax.set_xlabel(data[X_LEGEND])
    ax.grid()
    ax.set_yscale(data[YSCALE])
    fig.autofmt_xdate()
    gname = get_png_name(data)
    print("saving graph as " + gname + ".png")
    fig.savefig(gname)
    #plt.show()

def get_legend_heading(settings):
    heading = ""

    if settings[GRAPHTYPE] == TOTAL:
        heading = heading + "Cummulative "
    elif settings[GRAPHTYPE] == DAILY:
        heading = heading + "Daily "
    else:
        print("invalid graph type")
        return None, None

    if settings[DATASET] == TESTS:
        heading = heading + \
                "Covid-19 Tests Performed in South Africa"
        y_leg = "Tests Performed"
    elif settings[DATASET] == POS:
        heading = heading + \
                "Covid-19 Confirmed Cases in South Africa"
        y_leg = "Confirmed Cases"
    elif settings[DATASET] == POSTESTS:
        heading = heading + \
                "Covid-19 proportion of Tests Positive in South Africa"
        y_leg = "Proportion Positive"
    elif settings[DATASET] == ACTIVE:
        if settings[GRAPHTYPE] == DAILY:
            heading = "Daily change in "
        else:
            heading = "Total known "
        heading = heading + \
                "Covid-19 Active Cases in South Africa"
        y_leg = "Active Cases"
    elif settings[DATASET] == DEATHS:
        heading = heading + \
                "Covid-19 Confirmed Deaths in South Africa"
        y_leg = "Confirmed Deaths"
    elif settings[DATASET] == RECOV:
        heading = heading + \
                "Covid-19 Confirmed Recoveries in South Africa"
        y_leg = "Confirmed Recoveries"
    else:
        print("please give valid plotting data")
        return None, None

    if settings[YSCALE] == LOG:
        y_leg  = y_leg + " (Log Scale)"

    if settings[N_DAY_AV] > 1:
        heading = heading + "\n(" + str(settings[N_DAY_AV]) +" Day Average)"

    return y_leg, heading

### Main Function ##############################################################

if __name__ == "__main__":
    settings = parse_args(sys.argv)
    data = parse_data(settings[FILENAME])

    y_leg, heading = get_legend_heading(settings)
    if y_leg == None or heading == None:
        print("didn't get heading or legend")
        exit()
    x_leg = "Date"

    x_data, y_data = get_plot_data(data, settings)

    y_data = [y for _,y in sorted(zip(x_data, y_data))]
    x_data = sorted(x_data)

    settings[X_DATA] = x_data
    settings[Y_DATA] = y_data
    settings[X_LEGEND] = x_leg
    settings[Y_LEGEND] = y_leg
    settings[HEADING] = heading

    settings[DATEFORMAT] = DFORMAT_YEAR_FRST

    plot_data(settings)

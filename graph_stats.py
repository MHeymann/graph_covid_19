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
PROPREC = "proprec"

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


RSA = "rsa"
WC = "wc"
NC = "nc"
EC = "ec"
FS = "fs"
KZN = "kzn"
GP = "gp"
LP = "lp"
NW = "nw"
MP = "mp"

REGIONS = {"rsa": "South Africa", \
           "wc": "the Western Cape", \
           "nc": "the Northern Cape", \
           "ec": "the Eastern Cape", \
           "fs": "the Freestate", \
           "kzn": "Kwazulu-Natal", \
           "gp": "Gauteng", \
           "lp": "Limpopo", \
           "nw": "North-West", \
           "mp": "Mpumalanga"}
GRAPH_REG = "graph_reg"

DATA_SETS = np.array([POS, TESTS, RECOV, DEATHS, POSTESTS, ACTIVE, PROPREC])
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
    settings[GRAPH_REG] = RSA

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

def check_region_name(arg):
    if not arg in REGIONS:
        print("Not a valid region argument: " + arg)
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
        elif arg[0] == GRAPH_REG and check_region_name(arg[1]):
            settings[GRAPH_REG] = arg[1]
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
    tests = {RSA: {}, WC: {}, NC: {}, EC: {}, FS: {}, KZN: {}, GP: {}, \
            LP: {}, NW: {}, MP: {}}
    posit = {RSA: {}, WC: {}, NC: {}, EC: {}, FS: {}, KZN: {}, GP: {}, \
            LP: {}, NW: {}, MP: {}}
    deaths = {RSA: {}, WC: {}, NC: {}, EC: {}, FS: {}, KZN: {}, GP: {}, \
            LP: {}, NW: {}, MP: {}}
    recov = {RSA: {}, WC: {}, NC: {}, EC: {}, FS: {}, KZN: {}, GP: {}, \
            LP: {}, NW: {}, MP: {}}

    curr_date = ""
    with open (filename, "r") as f:
        line = f.readline()
        while not line == "":
            if line.strip() == "" or line.strip()[0] == "#":
                line = f.readline()
                continue
            data = line.split("\t")
            if data[0] in REGIONS:
                i = 1
                reg = data[0]
            else:
                i = 0
                reg = RSA

            if (data[i].strip() == "Entry:"):
                curr_date = ""
            if data[i].strip() == DATE:
                curr_date = data[1].strip()
                if not curr_date == "":
                    dates = np.append(dates, curr_date)
            elif (data[i].strip() == TESTS):
                if not curr_date == "":
                    tests[reg][curr_date] = data[i+1].replace(" ", "")
            elif (data[i].strip() == POS):
                if not curr_date == "":
                    posit[reg][curr_date] = data[i+1].replace(" ", "")
            elif (data[i].strip() == DEATHS):
                if not curr_date == "":
                    deaths[reg][curr_date] = data[i+1].replace(" ", "")
            elif (data[i].strip() == RECOV):
                if not curr_date == "":
                    recov[reg][curr_date] = data[i+1].replace(" ", "")
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

def get_prop_data(data, set1, set2, settings):
    x_data =  np.array([])
    data_1 =  np.array([])
    data_2 =  np.array([])
    region = settings[GRAPH_REG]

    prev_2 = -1
    prev_1 = -1

    for t in data[DATE]:
        d = convert_date(t)
        if d == None:
            continue

        if not is_date_valid_range(d, settings):
            continue

        if not t in data[set1][region] or not t in data[set2][region]:
            continue

        try:
            point_2 = int(data[set2][region][t])
            point_1 = int(data[set1][region][t])
        except ValueError as e:
            print("ValueError")
            print(e)
            continue

        if settings[GRAPHTYPE] == DAILY:
            if prev_1 < 0 or prev_2 < 0:
                prev_1 = point_1
                prev_2 = point_2
                continue

            cur_1 = point_1
            cur_2 = point_2
            point_1 = point_1 - prev_1
            point_2 = point_2 - prev_2
            prev_1 = cur_1
            prev_2 = cur_2
        if point_2 == 0:
            continue
        data_1 = np.append(data_1, point_1)
        data_2 = np.append(data_2, point_2)
        x_data = np.append(x_data, d)

    if settings[N_DAY_AV] > 1:
        if settings[N_DAY_AV] > len(data_1):
            n = len(data_1)
        else:
            n = settings[N_DAY_AV]
        data_1 = get_n_day_av(data_1, settings)
        data_2 = get_n_day_av(data_2, settings)
        x_data = x_data[n -1:]
    return x_data, data_1 / data_2

def get_active_data(data, settings):
    x_data =  np.array([])
    y_data =  np.array([])
    region = settings[GRAPH_REG]

    prev_active = -1

    for t in data[DATE]:
        d = convert_date(t)
        if d == None:
            continue

        if not is_date_valid_range(d, settings):
            continue

        if not t in data[POS][region] or \
                not t in data[RECOV][region] or \
                not t in data[DEATHS][region]:
            continue
        try:
            recov = int(data[RECOV][region][t])
            deaths = int(data[DEATHS][region][t])
            pos = int(data[POS][region][t])
        except ValueError as e:
            print("ValueError")
            print(e)
            continue

        active = pos - (recov + deaths)
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
    region = settings[GRAPH_REG]

    prev_y = -1

    for t in data[DATE]:
        d = convert_date(t)
        if d == None:
            continue

        if not is_date_valid_range(d, settings):
            continue

        if not t in data[settings[DATASET]][region]:
            continue
        try:
            y = int(data[settings[DATASET]][region][t])
        except ValueError as e:
            print("ValueError")
            print(e)
            continue

        if settings[GRAPHTYPE] == DAILY:
            if prev_y < 0:
                prev_y = y
                continue
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
        x_data, y_data = get_prop_data(data, POS, TESTS, settings)
    elif settings[DATASET] == ACTIVE:
        x_data, y_data = get_active_data(data, settings)
    elif settings[DATASET] == PROPREC:
        x_data, y_data = get_prop_data(data, RECOV, POS, settings)
    else:
        x_data, y_data = get_std_data(data, settings)

    return x_data, y_data

def print_data(data):
    for d in data[DATE]:
        print("Entry:")
        print(DATE + "\t" + d)
        if d in data[TESTS][RSA]:
            print(TESTS + "\t" + data[TESTS][RSA][d])
        if d in data[POS][RSA]:
            print(POS + "\t" + data[POS][RSA][d])
        if d in data[DEATHS][RSA]:
            print(DEATHS + "\t" + data[DEATHS][RSA][d])
        if d in data[RECOV][RSA]:
            print(RECOV + "\t" + data[RECOV][RSA][d])
        print()

def get_png_name(data):
    name = data[GRAPH_REG]
    name = name + "_" + data[DATASET]
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
                "Covid-19 Tests Performed in " + \
                REGIONS[settings[GRAPH_REG]]
        y_leg = "Tests Performed"
    elif settings[DATASET] == POS:
        heading = heading + \
                "Covid-19 Confirmed Cases in " + \
                REGIONS[settings[GRAPH_REG]]
        y_leg = "Confirmed Cases"
    elif settings[DATASET] == POSTESTS:
        heading = heading + \
                "Covid-19 Proportion of Tests Positive in " + \
                REGIONS[settings[GRAPH_REG]]
        y_leg = "Proportion Positive"
    elif settings[DATASET] == PROPREC:
        heading = \
                "Covid-19 Proportion of Positive Cases Recovered\nin " + \
                REGIONS[settings[GRAPH_REG]]
        y_leg = "Proportion Recovered"
    elif settings[DATASET] == ACTIVE:
        if settings[GRAPHTYPE] == DAILY:
            heading = "Daily change in "
        else:
            heading = "Total known "
        heading = heading + \
                "Covid-19 Active Cases in " + \
                REGIONS[settings[GRAPH_REG]]
        y_leg = "Active Cases"
    elif settings[DATASET] == DEATHS:
        heading = heading + \
                "Covid-19 Confirmed Deaths in " + \
                REGIONS[settings[GRAPH_REG]]
        y_leg = "Confirmed Deaths"
    elif settings[DATASET] == RECOV:
        heading = heading + \
                "Covid-19 Confirmed Recoveries in " + \
                REGIONS[settings[GRAPH_REG]]
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

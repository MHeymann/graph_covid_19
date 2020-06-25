#! /bin/bash

startdate=2020-06-22
enddate=$( date +%Y-%m-%d )

curr=$( date +%Y-%m-%d --date "$startdate -1 day" )
#curr=$( date +%Y-%m-%d --date "$( date +%Y-%m-%d ) -1 day" )
#curr=$( date +%Y-%m-%d --date "$curr -1 day" )
#curr=$( date +%Y-%m-%d --date "$curr -1 day" )
while true; do
    curr=$( date +%Y-%m-%d --date "$curr +1 day" )
    echo "$curr"
    echo ./graph_stats.py dataset=pos \
	    end_date=$curr
    ./graph_stats.py dataset=pos \
	    end_date=$curr
    echo ./graph_stats.py dataset=pos yscale=linear graphtype=daily \
	    end_date=$curr
    ./graph_stats.py dataset=pos yscale=linear graphtype=daily \
	    end_date=$curr
    echo ./graph_stats.py dataset=tests \
	    end_date=$curr
    ./graph_stats.py dataset=tests \
	    end_date=$curr
    echo ./graph_stats.py dataset=tests yscale=linear graphtype=daily \
	    end_date=$curr
    ./graph_stats.py dataset=tests yscale=linear graphtype=daily \
	    end_date=$curr
    echo ./graph_stats.py dataset=deaths \
	    end_date=$curr
    ./graph_stats.py dataset=deaths \
	    end_date=$curr
    echo ./graph_stats.py dataset=deaths yscale=linear \
	    end_date=$curr
    ./graph_stats.py dataset=deaths yscale=linear \
	    end_date=$curr
    echo ./graph_stats.py dataset=deaths yscale=linear graphtype=daily \
	    end_date=$curr
    ./graph_stats.py dataset=deaths yscale=linear graphtype=daily \
	    end_date=$curr
    echo ./graph_stats.py dataset=recov yscale=linear graphtype=daily n_day_av=3 \
	    end_date=$curr
    ./graph_stats.py dataset=recov yscale=linear graphtype=daily n_day_av=3 \
	    end_date=$curr
    echo ./graph_stats.py dataset=postests yscale=linear \
	    end_date=$curr
    ./graph_stats.py dataset=postests yscale=linear \
	    end_date=$curr
    echo ./graph_stats.py dataset=postests yscale=linear graphtype=daily \
	    end_date=$curr
    ./graph_stats.py dataset=postests yscale=linear graphtype=daily \
	    end_date=$curr
    echo ./graph_stats.py dataset=postests yscale=linear graphtype=daily n_day_av=3 \
	    end_date=$curr
    ./graph_stats.py dataset=postests yscale=linear graphtype=daily n_day_av=3 \
	    end_date=$curr
    echo ./graph_stats.py dataset=active yscale=linear \
	    end_date=$curr
    ./graph_stats.py dataset=active yscale=linear \
	    end_date=$curr
    ./graph_stats.py dataset=proprec yscale=linear \
	    end_date=$curr
    [ "$curr" \< "$enddate" ] || break
done

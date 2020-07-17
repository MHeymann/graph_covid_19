#! /bin/bash

startdate=2020-07-14
enddate=$( date +%Y-%m-%d )

curr=$( date +%Y-%m-%d --date "$startdate -1 day" )
#curr=$( date +%Y-%m-%d --date "$( date +%Y-%m-%d ) -1 day" )
#curr=$( date +%Y-%m-%d --date "$curr -1 day" )
#curr=$( date +%Y-%m-%d --date "$curr -1 day" )
while true; do
    curr=$( date +%Y-%m-%d --date "$curr +1 day" )
    echo "$curr"
    echo ./draw_graphs.sh \"end_date=$curr $1\"
    ./draw_graphs.sh "end_date=$curr $1"

    [ "$curr" \< "$enddate" ] || break
done

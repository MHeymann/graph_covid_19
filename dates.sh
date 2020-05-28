#! /bin/bash

startdate=2020-03-15
enddate=2020-05-20

curr="$startdate"
while true; do
    echo "$curr"
    [ "$curr" \< "$enddate" ] || break
    curr=$( date +%Y-%m-%d --date "$curr +1 day" )
done

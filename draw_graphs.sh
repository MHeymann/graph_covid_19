# /bin/bash

./graph_stats.py dataset=pos $1
./graph_stats.py dataset=pos yscale=linear graphtype=daily $1
./graph_stats.py dataset=pos yscale=linear graphtype=daily n_day_av=7 $1

./graph_stats.py dataset=tests $1
./graph_stats.py dataset=tests yscale=linear graphtype=daily $1
./graph_stats.py dataset=tests yscale=linear graphtype=daily n_day_av=7 $1

./graph_stats.py dataset=deaths $1
./graph_stats.py dataset=deaths yscale=linear $1
./graph_stats.py dataset=deaths yscale=linear graphtype=daily $1
./graph_stats.py dataset=deaths yscale=linear graphtype=daily n_day_av=7  $1

./graph_stats.py dataset=recov yscale=linear graphtype=daily n_day_av=7 $1

./graph_stats.py dataset=postests yscale=linear $1
./graph_stats.py dataset=postests yscale=linear graphtype=daily $1
./graph_stats.py dataset=postests yscale=linear graphtype=daily n_day_av=7 $1

./graph_stats.py dataset=active yscale=linear $1
./graph_stats.py dataset=proprec yscale=linear $1


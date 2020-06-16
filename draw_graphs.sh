# /bin/bash

./graph_stats.py dataset=pos
./graph_stats.py dataset=pos yscale=linear graphtype=daily
./graph_stats.py dataset=tests
./graph_stats.py dataset=tests yscale=linear graphtype=daily
./graph_stats.py dataset=deaths
./graph_stats.py dataset=deaths yscale=linear
./graph_stats.py dataset=deaths yscale=linear graphtype=daily
./graph_stats.py dataset=recov yscale=linear graphtype=daily n_day_av=3
./graph_stats.py dataset=postests yscale=linear
./graph_stats.py dataset=postests yscale=linear graphtype=daily
./graph_stats.py dataset=postests yscale=linear graphtype=daily n_day_av=3
./graph_stats.py dataset=active yscale=linear

#!/usr/bin/env sh
gnuplot -p -e "binwidth=2;
bin(x,width)=width*floor(x/width);
plot '$1' using (bin(\$1,binwidth)):(1.0) smooth freq with boxes;"

set terminal postscript color enhanced 
set output "loop_derivation_pval.eps"
set yrange[0:1]
set xlabel "GQ models"
set ylabel "p-value for predictor"
set xtics
set style fill solid 1.0 noborder
set key left top
set style line 1 lc rgb '#6d0000' lt 1 lw 2 pt 7 ps 1.5
set style line 2 lc rgb '#006d00' lt 1 lw 2 pt 5 ps 1.5
set style line 3 lc rgb '#00006d' lt 1 lw 2 pt 3 ps 1.5
set style data linespoints
plot \
     'pval-lc.dat' title "Loop lenght configuration" ls 1 smooth csplines, \
     'pval-k1.dat' title "K1" ls 2 smooth csplines, \
     'pval-k2.dat' title "K2" ls 3 smooth csplines, \
     'pval-lc.dat' title "" ls 1 with points, \
     'pval-k1.dat' title "" ls 2 with points, \
     'pval-k2.dat' title "" ls 3 with points

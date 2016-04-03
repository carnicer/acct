ME=$0
FF=$1

PP=`dirname $ME`
echo PP $PP
python $PP/p.py $FF | grep -B 1 -A 100 ===


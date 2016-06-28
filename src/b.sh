# extracts saldos from a balance report from p.py

F=$1
AA=`grep -n "==================" $F | tail -2 | cut -d: -f1`

for T in $AA
do
  S=${S}${T}","
done

DD=`echo $S | sed 's/.$//'`
#echo $DD

sed -n "$DD p" $F


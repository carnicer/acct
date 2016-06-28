#!/bin/bash

ME=$0
FF=$1

F_INIS=${FF}_saldoIni.txt
F_MOVS=${FF}.txt
F_OUT=${FF}_out.txt
F_BAL=${FF}_bal.txt

URL=`git remote -v | grep fetch | grep github | cut -f 2 | cut -d" " -f 1`
echo "using code from ${URL}"

PP=`dirname $ME`
echo working on folder $PP

[ -f $F_MOVS ] || {
  echo "FATAL: movements file $F_MOVS NOT found, aborting ..."
  exit 1
}
echo "processing movs file $F_MOVS ..."

[ -f $F_INIS ] && {
  echo "using initial saldo file $F_INIS"
  echo "python $PP/p.py -i $F_INIS $F_MOVS"
  python $PP/p.py -i $F_INIS $F_MOVS | grep -B 1 -A 100 === >$F_OUT
  RES=$?
} || {
  echo "NOT using initial saldo file ($F_INIS not found)"
  echo "python $PP/p.py $F_MOVS"
  python $PP/p.py $F_MOVS | grep -B 1 -A 100 === >$F_OUT
  RES=$?
}

[ $RES -eq 0 ] || {
  echo "ERROR processing file ${F_MOVS}, quitting ..."
  exit 1
}
echo "file $F_MOVS processed OK"
echo "tmp output in $F_OUT"

bash $PP/b.sh $F_OUT >$F_BAL
echo "balance in $F_BAL"


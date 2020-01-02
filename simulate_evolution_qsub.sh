#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
tmpFile=`mktemp -d -p "$DIR"`
sed "2i DIR=$DIR" $DIR/simulate_evolution.sh > tmpFile.sh
qsub -q batch -l walltime=23:59:00,mem=16gb -F "$@" tmpFile.sh &
sleep 2s
rm $tmpFile

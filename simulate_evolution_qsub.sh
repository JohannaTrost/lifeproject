#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
tmpFile=`mktemp -u -p "$DIR"`.sh
sed "2i DIR=$DIR" $DIR/simulate_evolution.sh > $tmpFile
qsub -q batch -l walltime=23:59:00,mem=16gb -F "$@" $tmpFile &
sleep 2s
rm $tmpFile

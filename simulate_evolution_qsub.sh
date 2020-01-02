#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
qsub -q batch -l walltime=23:59:00,mem=16gb -F "$@" $DIR/simulate_evolution.sh

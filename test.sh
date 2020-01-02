#!/bin/bash
test=/project/3018037.01/Experiment3.2_ERC/AnalysisFolder/scripts/toolboxes/lifeproject
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
python $DIR/simulate_evolution.py "$@"


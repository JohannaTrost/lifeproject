#!/bin/bash
num_simulations=30
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
for d in `ls -d $DIR/experiments/all_gene_pools_param_comparison/*`; do
	for s in `seq 1 $num_simulations`; do
		thisExperiment="$d/$s"
		if [ ! -d "$thisExperiment" ];then
			mkdir $thisExperiment
		fi
		cp $d/evo_config.json $thisExperiment/evo_config.json
		sh $DIR/simulate_evolution_qsub.sh "-e $thisExperiment -nt -s -o" &
	done
done

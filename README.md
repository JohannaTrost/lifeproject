# LIFPROJET

Project on evolution based learning of movement.

The base creature is a four-legged individuum that has to learn to coordinate its limbs. Furthermore the size of each limb is modified throughout the evolution. Motion is realized by applying a motion pattern to each limb (a series of steps to take) of varying length. After each generation sizes and motion patterns will be crossed, such that the individual infers learns to optimally use limbs given a certain size.

To run the script use:

`python simulate_evolution.py [args]`

Type `python simulate_evolution.py -h` obtain the output below for possible arguments:

```
usage: simulate_evolution.py [-h] [--individuals INDIVIDUALS]
                             [--generations GENERATIONS] [--duration DURATION]
                             [--fps FPS] [--save_gene_pool SAVE_GENE_POOL]
                             [--overwrite_latest OVERWRITE_LATEST]
                             [--cores CORES] [--visualize VISUALIZE]
                             [--stats STATS] [--gene_pool_file GENE_POOL_FILE]
                             [--best_only BEST_ONLY]

optional arguments:
  -h, --help            show this help message and exit
  --individuals INDIVIDUALS, -i INDIVIDUALS
                        number of individuals - In case visualization mode was
                        chosen, a random set of i individuals will be chosen
                        (default=40)
  --generations GENERATIONS, -g GENERATIONS
                        number of generations (default=100)
  --duration DURATION, -d DURATION
                        duration of each simulation in seconds (default=10)
  --fps FPS, -f FPS     frames per second (default=240)
  --save_gene_pool SAVE_GENE_POOL, -s SAVE_GENE_POOL
                        Save all gene pools per generation to new folder - If
                        not set only last generation will be saved
  --overwrite_latest OVERWRITE_LATEST, -o OVERWRITE_LATEST
                        whether to overwrite the default files in the parent
                        directory
  --cores CORES, -c CORES
                        number of CPU cores - Set to -1 for all cores
                        (default=-1)
  --visualize VISUALIZE, -v VISUALIZE
                        visualize result specified (default=False)
  --stats STATS, -sf STATS
                        evo stats file to use for visualization (default is
                        latest file)
  --gene_pool_file GENE_POOL_FILE, -gf GENE_POOL_FILE
                        genome file to use for visualization (default is
                        latest file)
  --best_only BEST_ONLY, -b BEST_ONLY
                        whether to show only the best or multiple individuals
                        (default=True)
  ```

Note that there are two different modes in which the script can be use: simulation and visualization mode. Within the simulation mode the evolution is simulated according to the specifications. The visualization mode can be used to readout the result of the evolution.

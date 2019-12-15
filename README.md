# LIFPROJET

Project on evolution based learning of movement.

The base creature is a four-legged individuum that has to learn to coordinate its limbs. Furthermore the size of each limb can be modified throughout the evolution. Motion is realized by applying a motion pattern to each limb (a series of steps to take) of varying length. After each generation, sizes and motion patterns will be crossed, such that the individual learns to optimally use limbs given a certain size.

## Usage

To run the script use:

`python simulate_evolution.py [args]`

Type `python simulate_evolution.py -h` obtain the output below for possible arguments:

```
usage: simulate_evolution.py [-h] [--individuals INDIVIDUALS]
                             [--generations GENERATIONS] [--duration DURATION]
                             [--get_config] [--evolution_dir EVOLUTION_DIR]
                             [--generation GENERATION] [--tracking]
                             [--save_gene_pool] [--overwrite] [--cores CORES]
                             [--visualize] [--best_only] [--show_stats]

optional arguments:
  -h, --help            show this help message and exit
  --individuals INDIVIDUALS, -i INDIVIDUALS
                        number of individuals per generation - In case
                        visualization mode was chosen, a random set of i
                        individuals will be chosen for displaying (default=10)
  --generations GENERATIONS, -g GENERATIONS
                        number of generations to be evolved (default=10)
  --duration DURATION, -d DURATION
                        duration of each simulation in seconds - Final fitness
                        is obtained after that time (default=10)
  --get_config, -gc     only create default config file and exit
  --evolution_dir EVOLUTION_DIR, -e EVOLUTION_DIR
                        parent directory for the evolution to be stored or
                        loaded from (default=example)
  --generation GENERATION, -gen GENERATION
                        generation on which to continue evolution or
                        generation to display if visualization mode was chosen
                        - Set -1 for latest (default=-1)
  --tracking, -nt       disable tracker for individuals
  --save_gene_pool, -s  Save all gene pools per generation to new folder
  --overwrite, -o       overwrite existing data
  --cores CORES, -c CORES
                        number of CPU cores for simulating one generation -
                        Set to -1 for all cores (default=-1)
  --visualize, -v       visualize results
  --best_only, -nb      do not show result of best, but rather -i random
                        individuals
  --show_stats, -ss     whether to show statistics on the evolution - If set,
                        statistics and not rendered individuals are shown
  ```

Note that there are two different modes in which the script can be use: simulation and visualization mode. Within the simulation mode the evolution is simulated according to the specifications. The visualization mode can be used to readout the result of the evolution.

## Example

Example for an evolution of 80 individuals over 100 generations, simulating each individual for 40s:

`python simulate_evolution.py -i 80 -g 100 -d 40`

if `-s` is added, gene pools for each generation are stored.

Furthermore it is possible to continue evolving from a certain generation by appending `-gen <number of generation>`.

## Results

For each evolution a `evo_config.json` file is used to store main parameters on the evolution. Furthermore a `stats` and `fitness` file store basic statistics such as average fitness and fitness per generation and individuals. A `tracker` file is requested storing the paths of each individual for each simulation. Supress requested tracker file by adding `-nt` to the simulation command.

## Visualization

A rendered instance of the resulting individuals can be obtained by adding the `-v` flag. Per default the last generation is selected, but can be modified by adding `-gen <number of generation>`.

`python simulate_evolution.py -v`

To see more global statistics, add the `-ss` flag. Note that this will supress the rendered instance.


# LIFPROJET

Project on evolution based learning of movement.

The base creature is a four-legged individuum that has to learn to coordinate its limbs. Furthermore the size of each limb can be modified throughout the evolution. Motion is realized by applying a motion pattern to each limb (a series of steps to take) of varying length. After each generation, sizes and motion patterns will be crossed, such that the individual learns to optimally use limbs given a certain size.

## Usage

To run the script use:

`python simulate_evolution.py [args]`

Type `python simulate_evolution.py -h` obtain the output below for possible arguments:

```
usage: simulate_evolution.py [-h] [-i INDIVIDUALS] [-g GENERATIONS]
                             [-d DURATION] [-gc] [-e EVOLUTION_DIR]
                             [-gen GENERATION] [-nt] [-s] [-o] [-c CORES] [-v]
                             [-f] [-sd SLOW_DOWN_FACTOR] [-nb] [-ss]

optional arguments:
  -h, --help            show this help message and exit
  -i INDIVIDUALS, --individuals INDIVIDUALS
                        number of individuals per generation - In case
                        visualization mode was chosen, a random set of i
                        individuals will be chosen for displaying (default=10)
  -g GENERATIONS, --generations GENERATIONS
                        number of generations to be evolved (default=10)
  -d DURATION, --duration DURATION
                        duration of each simulation in seconds - Final fitness
                        is obtained after that time (default=10)
  -gc, --get_config     only create default config file and exit
  -e EVOLUTION_DIR, --evolution_dir EVOLUTION_DIR
                        parent directory for the evolution to be stored or
                        loaded from (default=example)
  -gen GENERATION, --generation GENERATION
                        generation on which to continue evolution or
                        generation to display if visualization mode was chosen
                        - Set -1 for latest (default=-1)
  -nt, --no_tracking    disable tracker for individuals
  -s, --save_gene_pool  Save all gene pools per generation to new folder
  -o, --overwrite       overwrite existing data
  -c CORES, --cores CORES
                        number of CPU cores for simulating one generation -
                        Set to -1 for all cores (default=-1)
  -v, --visualize       visualize results
  -f, --follow_target   whether to follow the target with the GUI camera
  -sd SLOW_DOWN_FACTOR, --slow_down_factor SLOW_DOWN_FACTOR
                        divide GUI update speed by this value
  -nb, --not_only_best  do not show result of best, but rather -i random
                        individuals
  -ss, --show_stats     whether to show statistics on the evolution - If set,
                        statistics and not rendered individuals are shown
  ```

Note that there are two different modes in which the script can be use: simulation and visualization mode. Within the simulation mode the evolution is simulated according to the specifications. The visualization mode can be used to readout the result of the evolution.

## Example

Example for an evolution of 80 individuals over 100 generations, simulating each individual for 40s:

`python simulate_evolution.py -i 80 -g 100 -d 40`

if `-s` is added, gene pools for each generation are stored in the format `gen_<generation>.pkl`.

Furthermore it is possible to continue evolving from a certain generation by appending `-gen <number of generation>`.

## Results

For each evolution a `evo_config.json` file is used to store main parameters on the evolution. Furthermore a `stats.csv` and `fitness.csv` file store basic statistics such as average fitness and fitness per generation and individuals. A `tracker.pkl` file is requested storing the paths of each individual for each simulation. Supress requested tracker file by adding `-nt` to the simulation command.

## Visualization

A rendered instance of the resulting individuals can be obtained by adding the `-v` flag. Per default the last generation is selected, but can be modified by adding `-gen <number of generation>`.

`python simulate_evolution.py -v`

To see more global statistics, add the `-ss` flag. Note that this will supress the rendered instance.

If you want to follow the target with the GUI camera, use the `-f` flag and if you want to slow down the graphical rendering, add `-sd <factor>` to the command.

## evo_config.json

an example `evo_config.json` file looks like this:

```
{
"individuals": 
    {
    "min_box_size": 0.3,              -> minimum half size of initial randomly created boxes
    "max_box_size": 1.0,              -> maximum half size of initial randomly created boxes
    "random_box_size": true,          -> use random boxes - if false, the average of the above is used as fixed size
    "symmetric": false,               -> whether the individual is symmetric with respect to the sies of it's limbs 
    "min_force": 100,                 -> minimum force per limb
    "max_force": 500,                 -> maximum force per limb
    "start_move_pattern_size": 240,   -> size of the initial moving pattern (at 240 fps, this corresponds to 1s of steps)
    "vary_pattern_length": true,      -> whether to vary the length of the moving pattern by evolution
    "standard_volume": 2.197          -> scales the mass to be at 1 if the cube is shaped 1.3^3 (default half size * 2)
    }, 
"simulation": 
    {
    "fps": 240,                       -> update simulations so many times per second
    "colormap": "viridis",            -> color scheme for individuals that are rendered (randomly chosen from colormap)
    "generations": 200,               -> number of generations to be evolved
    "individuals": 80,                -> number of individuals per generation
    "duration": 40                    -> duration of the simulation for each individual in seconds
    }, 
"evolution": 
    {
    "mutation_prob_ind": 0.05,        -> probability for an individual to mutate
    "mutation_prob_gene": 0.05,       -> probability for a gene to mutate
    "mutation_prob_feature": 0.05,    -> probability for a feature of that gene to mutate
    "alpha_limits": 0.5               -> alpha value for computing limits for choosing the value after crossing
    }
}
```

## individuals
### sizes
All individuals consist of 6 boxes and 6 spheres. Boxes are: chest, hip, left / right arm and left / right leg. Spheres are: head, taile, left / right shoulder and left / right hip joint.

Each box is initialized such, that the mass (on average) per box is 1. This is due to the fact that the half-size of each box is a random value between 0.3 and 1.0 (for the default settings), which on average is 0.65. Since this value defines the half-size each box is on average shaped 1.3 * 1.3 * 1.3 and thus has a standard volume of 2.197 which corresponds to mass of one. If values are change, consider adapting the standard mass.

### forces
To each sphere (except the head) a force is added, moving the limb in x and / or z direction. The force is depending on the mass, but capped. It is computed according to this formula:

`1 / (1 / max_force + np.exp(-mass * 3)) + min_force`

which creates a sigmoid function f such that force = f(mass) between min_force and max_force. Hence there is an optimal range were the best volume - force tradeoff is achieved, preventing boxes from getting too small and too big.

### moving pattern
Each limb has an assigned movment pattern. Its array values are called sequentially one for each simulation step. If the end of the pattern is rached, it will repeat.

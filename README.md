# LIFPROJET

Project on evolution based learning of movement.

The base creature is a four-legged individuum that has to learn to coordinate its limbs. Furthermore the size of each limb is modified throughout the evolution.

To run the script use:

`python simulate_evolution.py [args]`

Type `python simulate_evolution.py -h` obtain the output below for possible arguments:

```
usage: simulate_evolution.py [-h] [--individuals INDIVIDUALS]
                             [--generations GENERATIONS] [--duration DURATION]
                             [--fps FPS] [--cores CORES]

optional arguments:
  -h, --help            show this help message and exit
  --individuals INDIVIDUALS, -i INDIVIDUALS
                        number of individuals
  --generations GENERATIONS, -g GENERATIONS
                        number of generations
  --duration DURATION, -d DURATION
                        duration of each simulation in seconds
  --fps FPS, -f FPS     frames per second
  --cores CORES, -c CORES
                        number of CPU cores (default=1) Set to -1 for all
                        cores
  ```

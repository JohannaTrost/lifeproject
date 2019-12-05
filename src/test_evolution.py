import numpy as np
import src.simplePopulation_test as spt
import matplotlib.pylab as plt
import src.data2plot as d2p


def save_as_csv(generations, parent_ids, distances, num_obj, filename):
    # generate column names
    col_names = 'Generation, ID,'
    for i in range(num_obj):
            col_names += 'x' + str(i+1) + ', '
            col_names += 'y' + str(i+1) + ', '
            col_names += 'z' + str(i + 1) + ', '
            col_names += 'power' + str(i + 1) + ', '
            col_names += 'velocity' + str(i + 1) + ', '
    col_names += 'fitness(distance from start), parent1, parent2'

    # fill table content into 2D array
    data = []
    for i, generation in enumerate(generations):
            for j, individual in enumerate(generation):
                    row = []
                    # generation
                    row.append(float(i))
                    # ID of individual
                    row.append(float(individual[0]))
                    # x,y,z,power,velocity for each box
                    for box in individual[1]:
                            row = np.concatenate([np.asarray(row), np.asarray(box)])
                    row = list(row)
                    # fitness(distance)
                    row.append(distances[i][j])
                    # because no parents for first population
                    if i > 0:
                            row.append(parent_ids[i][j][0])
                            row.append(parent_ids[i][j][1])
                    else:
                            row.append(np.nan)
                            row.append(np.nan)
                    data.append(row)
    np.savetxt(filename + ".csv", data, delimiter=",", header=col_names, comments='')


def test_variety_mutation_prob(nb_generations, pop_size, num_limbs, mutation_probs, csv_filepath):
    plt.figure()
    for mutation_prob in mutation_probs:
        np.random.seed(42)
        generations, parent_ids, distances = spt.simulate_evolution(nb_generations,
                                                                    pop_size,
                                                                    mutation_prob,
                                                                    num_limbs)
        save_as_csv(generations, parent_ids, distances, num_limbs, csv_filepath + str(mutation_prob))


data_sets = [0.0, 0.01, 0.02, 0.05]
#test_variety_mutation_prob(100, 70, 3, data_sets, 'src/results/evo_results_mut')
avg_fitness, max_fitness = d2p.fetch_data(data_sets, 'src/results/evo_results_mut')
d2p.generate_normal_plot(data_sets, avg_fitness, max_fitness, nb_individuals=70)
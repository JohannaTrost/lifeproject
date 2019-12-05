import numpy as np
import pybullet as p
import time
import src.simplePopulation_test as spt


def get_individuals_from_csv(csv_path, mutation_prob, nb_indiv):

        data = np.loadtxt(csv_path + str(mutation_prob) + ".csv", skiprows=1, delimiter=',')
        generations = data[:, 0]
        distances = data[:, 17]
        # nb of generations in between generation chosen for the demo
        distinct_generations = np.unique(generations)
        # e.g. nb generations = 100, nb individuals for demo = 4, generations for demo 0, 24, 49, 75
        # step_size = distinct_generations.shape[0] / nb_indiv

        selected_individuals = []
        generation_selected = [4, 10, 16, 37, 61]
        nearest_2_avg = None
        for step in range(nb_indiv):
            individual_genom = []
            curr_distances = data[generations == generation_selected[step], 17];
            avg = np.average(curr_distances)
            nearest_2_avg_idx = (np.abs(curr_distances - avg)).argmin()
            # if distance from before is higher than from this generation take the next higher distance
            while nearest_2_avg and nearest_2_avg >= curr_distances[nearest_2_avg_idx]:
                nearest_2_avg_idx += 1
            nearest_2_avg = curr_distances[nearest_2_avg_idx]

            # not adapted to dynamic number of boxes of individual
            individual_genom.append(np.squeeze(data[distances == nearest_2_avg, 2:7]))
            individual_genom.append(np.squeeze(data[distances == nearest_2_avg, 7:12]))
            individual_genom.append(np.squeeze(data[distances == nearest_2_avg, 12:17]))
            selected_individuals.append(individual_genom)

        return selected_individuals

# inits for simulation
sim_time = 10  # s
dt = 1. / 240.
p.connect(p.GUI)  # p.DIRECT to not display graphical output
p.createCollisionShape(p.GEOM_PLANE)
p.createMultiBody(0, 0)
p.setGravity(0, 0, -9.81)
assert (p.isConnected())

genomes = get_individuals_from_csv('src/results/evo_results_mut', 0.02, 5)
# p.startStateLogging(p.STATE_LOGGING_VIDEO_MP4, 'src/evo_demo_video.mp4')
rgb_image_frames = []
for genome in genomes:
    individual_id, genome, base_position = spt.create_individual(genome=genome)
    # simulation
    # curr_obj_position = None
    # fov = 60
    # aspect = 128 / 128
    # near = 0.02
    # far = 1

    for j in range(int(sim_time / dt)):
        p.stepSimulation()
        if j == 0:
            curr_obj_position = p.getBasePositionAndOrientation(individual_id)[0]
            p.resetDebugVisualizerCamera(cameraDistance=16.0,
                                         cameraYaw=0.0,
                                         cameraPitch=-11.0,
                                         cameraTargetPosition=p.getBasePositionAndOrientation(individual_id)[0])

        # diff_pos = abs(spt.distance(curr_obj_position[0], p.getBasePositionAndOrientation(individual_id)[0][0],
        #                             curr_obj_position[1], p.getBasePositionAndOrientation(individual_id)[0][1]))
        # if diff_pos > 5.0:
        #     p.resetDebugVisualizerCamera(cameraDistance=20.0,
        #                                  cameraYaw=0.0,
        #                                  cameraPitch=-45.0,
        #                                  cameraTargetPosition=p.getBasePositionAndOrientation(individual_id)[0])
        #     curr_obj_position = p.getBasePositionAndOrientation(individual_id)[0]
        time.sleep(dt)

        #view_matrix = p.computeViewMatrix([0, 0, 0.5], [0, 0, 0], [1, 0, 0])
        #projection_matrix = p.computeProjectionMatrixFOV(fov, aspect, near, far)

        # # Get depth values using the OpenGL renderer
        # images = p.getCameraImage(128,
        #                           128,
        #                           view_matrix,
        #                           projection_matrix,
        #                           shadow=True,
        #                           renderer=p.ER_BULLET_HARDWARE_OPENGL)
        # rgb_image_frames.append(images)
    p.removeBody(individual_id)
# p.stopStateLogging(p.STATE_LOGGING_VIDEO_MP4)




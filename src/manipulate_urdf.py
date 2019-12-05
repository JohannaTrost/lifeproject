from urdfpy import URDF
import numpy as np

creature = URDF.load('data/Creature.URDF')

def setSizes(creature=np.nan, sizes=[]):
    if(creature is np.nan):
        creature = URDF.load('data/Creature.urdf')
    i = 0
    for link in creature.links:
        if int(link.name) % 2 == 1:
            link.visual.geometry.box.size = str(sizes[i]) + ' ' + str(sizes[i+1]) + ' ' + str(sizes[i+2])
            (link + 1).visual.geometry.sphere.radius = str(sizes[i+2]/2)
            i += 3

    creature.save('data/Creature.urdf')
    #sizeX, sizeY, sizeZ, sphere_radius, velocity_z, power_z, velocity_y, power_y
from lxml import etree

#def setSizes(creature=np.nan, sizes=[]):

    tree = etree.parse('data/Creature.urdf')
    root = tree.getroot()
    x = root.xpath("//link[@name='B2']/visual/geometry/box")
    x[0].attrib['size'] = "2. 2. 2."
    #sizeX, sizeY, sizeZ, sphere_radius, velocity_z, power_z, velocity_y, power_y
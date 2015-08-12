__author__ = 'fran'

from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
#ff = open("output", "r")
#ft
pointsfile = open("output", "r").readlines()
points = []
triangles = []
edges = []
cons = []

for l in pointsfile:
    if l[0] == "#": #triangulos
        pos=l[2:len(l)-1].split(" ")
        #if int(pos[0]) < ft and int(pos[1]) < ft and int(pos[2]) < ft:
            #newtriang = [int(pos[0]), int(pos[1]), int(pos[2])]
        edge1 = [int(pos[0]), int(pos[1])]
        edge2 = [int(pos[1]), int(pos[2])]
        edge3 = [int(pos[2]), int(pos[0])]
        edges.append(edge1)
        edges.append(edge2)
        edges.append(edge3)
    elif l[0]=="*": #aristas restringidas
        pos=l[2:len(l)-1].split(" ")
        newedge=[int(pos[0]),int(pos[1])]
        #if 11 in newtriang:
        #    continue
        edges.append(newedge)
    else: #vertices
        pos=l[:len(l)-1].split(" ")
        newpoint=[float(pos[1]), float(pos[2])]
        points.append(newpoint)

points = np.asarray(points)
edges = np.asarray(edges)

x = points[:, 0].flatten()
y = points[:, 1].flatten()

plt.plot(x[edges.T], y[edges.T], linestyle='-', color='y', markerfacecolor='red', marker='o')

plt.show()
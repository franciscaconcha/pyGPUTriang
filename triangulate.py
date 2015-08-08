__author__ = 'fran'

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import numpy as np
import string as st
import copy
from Triangle import Triangle
from Edge import Edge
import utils
import math
import pyopencl as cl


# Lee el archivo con las coordenadas y lo transforma a una lista de vertices
def prepCoords(file):
    coordlist = np.array(open(file).readlines())
    coordst = map(st.split, coordlist)
    coords = [map(float, l) for l in coordst]
    vertex = []

    for i in range(len(coords)):
        vertex.append([coords[i][0], coords[i][1]])

    return vertex


def getMax(coordsList):
    maxpoint = coordsList[0]

    for i in range(len(coordsList)):
        if coordsList[i][0] > maxpoint[0]:
            if coordsList[i][1] > maxpoint[1]:
                maxpoint = coordsList[i]

    return maxpoint

def getMin(coordsList):
    minpoint = coordsList[0]

    for i in range(len(coordsList)):
        if coordsList[i][0] < minpoint[0]:
            if coordsList[i][1] < minpoint[1]:
                minpoint = coordsList[i]

    return minpoint

def getNeighbors(t, triangles):
    t1 = triangles[0]
    t2 = triangles[1]
    t3 = triangles[2]
    n1 = [0, 0, 0]
    n2 = [0, 0, 0]
    n3 = [0, 0, 0]

    if len(totaltriangles) == 1:
        n1[0] = t2
        n1[1] = t3
        n1[2] = t.n3

        if t2.v1[0] < t2.v2[0]:
            n2[0] = t.n1
            n2[1] = t3
            n2[2] = t1
        else:
            n2[0] = t1
            n2[1] = t.n1
            n2[2] = t3

        n3[0] = t2
        n3[1] = t.n2
        n3[2] = t1

        return n1, n3, n3
    else:
        edge1_1 = [t1.v2, t1.v3]
        edge2_1 = [t1.v3, t1.v1]
        edge3_1 = [t1.v1, t1.v2]

        edge1_2 = [t2.v2, t2.v3]
        edge2_2 = [t2.v3, t2.v1]
        edge3_2 = [t2.v1, t2.v2]

        edge1_3 = [t3.v2, t3.v3]
        edge2_3 = [t3.v3, t3.v1]
        edge3_3 = [t3.v1, t3.v2]

        for r in totaltriangles:
            common = utils.findCommonEdge(t1, r)
            '''print "common:"
            print common'''
            if len(common) >= 2:
                if common[0] == edge1_1[0] and common[1] == edge1_1[1] and r.status == 0:
                    n1[0] = r
                elif common[0] == edge2_1[0] and common[1] == edge2_1[1] and r.status == 0:
                    n1[1] = r
                elif common[0] == edge3_1[0] and common[1] == edge3_1[1] and r.status == 0:
                    n1[2] = r

        for r in totaltriangles:
            common = utils.findCommonEdge(t2, r)
            if len(common) >= 2:
                if common[0] == edge1_2[0] and common[1] == edge1_2[1] and r.status == 0:
                    n2[0] = r
                elif common[0] == edge2_2[0] and common[1] == edge2_2[1] and r.status == 0:
                    n2[1] = r
                elif common[0] == edge3_2[0] and common[1] == edge3_2[1] and r.status == 0:
                    n2[2] = r

        for r in totaltriangles:
            common = utils.findCommonEdge(t3, r)
            if len(common) >= 2:
                if common[0] == edge1_3[0] and common[1] == edge1_3[1] and r.status == 0:
                    n3[0] = r
                elif common[0] == edge2_3[0] and common[1] == edge2_3[1] and r.status == 0:
                    n3[1] = r
                elif common[0] == edge3_3[0] and common[1] == edge3_3[1] and r.status == 0:
                    n3[2] = r

        for i in range(3):
            if n1[i] == 0:
                n1[i] = None

        for i in range(3):
            if n2[i] == 0:
                n2[i] = None

        for i in range(3):
            if n3[i] == 0:
                n3[i] = None

        return n1, n2, n3


def edgeFlip(t1,t2):
    common = utils.findCommonEdge(t1, t2)
    '''print "common: " + str(common)'''

    vertex1 = utils.findOutsider(t1, common)
    vertex2 = utils.findOutsider(t2, common)
    '''print "vertices:"
    print vertex1
    print vertex2'''

    if vertex1 == vertex2 or vertex1 is None or vertex2 is None or len(common) < 2:
        print "mal"
        return False

    ccwCoords = utils.orderVertices([vertex1, vertex2, common[0]])
    temp1 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
    ccwCoords = utils.orderVertices([vertex1, vertex2, common[1]])
    temp2 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])

    t1vertex = [temp1.v1, temp1.v2, temp1.v3]
    t2vertex = [temp2.v1, temp2.v2, temp2.v3]
    t1nbs = [None, None, None]
    t2nbs = [None, None, None]

    opTemp1 = utils.findOutsider(temp2, [vertex1, vertex2])
    opTemp2 = utils.findOutsider(temp1, [vertex1, vertex2])
    tmpIndex = t1vertex.index(opTemp2)
    t1nbs[tmpIndex] = temp2
    tmpIndex = t2vertex.index(opTemp1)
    t2nbs[tmpIndex] = temp1

    '''print opTemp1, opTemp2'''

    totaltriangles.remove(t1)
    totaltriangles.remove(t2)
    totaltriangles.append(temp1)
    totaltriangles.append(temp2)

    for r in totaltriangles:
        if r != t1 and r != t2:
            common = utils.findCommonEdge(r, temp1)
            if len(common) == 2:
                solo = utils.findOutsider(temp1, common)
                nbindex = t1vertex.index(solo)
                t1nbs[nbindex] = r

            common = utils.findCommonEdge(r, temp2)
            if len(common) == 2:
                solo = utils.findOutsider(temp2, common)
                nbindex = t2vertex.index(solo)
                t2nbs[nbindex] = r

    temp1.setNeighbor(t1nbs[0], t1nbs[1], t1nbs[2])
    temp2.setNeighbor(t2nbs[0], t2nbs[1], t2nbs[2])

    for r in totaltriangles:
        nbsr = [r.n1, r.n2, r.n3]
        if r != t1 and r != t2:
            if t1 in nbsr:
                nbindex = nbsr.index(t1)
                common = utils.findCommonEdge(r, t1)
                if common[0] in t1vertex and common[1] in t1vertex:
                    nbsr[nbindex] = temp1
            if t2 in nbsr:
                nbindex = nbsr.index(t2)
                common = utils.findCommonEdge(r, t2)
                if common[0] in t2vertex and common[1] in t2vertex:
                    nbsr[nbindex] = temp2
        r.setNeighbor(nbsr[0], nbsr[1], nbsr[2])


def fixEdge(t, p):
    d1 = utils.pointLineDistance(p, t.v2, t.v3)  # Arista opuesta a v1, compartida con vecino1
    d2 = utils.pointLineDistance(p, t.v3, t.v1)  # Arista opuesta a v2, compartida con vecino2
    d3 = utils.pointLineDistance(p, t.v1, t.v2)  # Arista opuesta a v3, compartida con vecino3

    lowerDistance = [d1, d2, d3]

    #print lowerDistance

    minDist = min(lowerDistance)

    for i in range(len(lowerDistance)):
        if lowerDistance[i] == minDist:
            neighborIndex = i

    nbs = [t.n1, t.n2, t.n3]
    #print nbs

    nbt = nbs[neighborIndex]  # Triangulo vecino mas cercano al punto

    #print nbt

    if nbt != None:
        common = utils.findCommonEdge(t, nbt)
        vertex1 = utils.findOutsider(t, common)
        vertex2 = utils.findOutsider(nbt, common)
        ccwCoords = utils.orderVertices([vertex1, common[0], p])
        t1 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
        ccwCoords = utils.orderVertices([vertex1, common[1], p])
        t2 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
        ccwCoords = utils.orderVertices([vertex2, common[0], p])
        t3 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
        ccwCoords = utils.orderVertices([vertex2, common[1], p])
        t4 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])

        return nbt, t1, t2, t3, t4


def circleTest(t, p):
    print "GPUing bitchezzz"
    mf = cl.mem_flags

    print t

    p1 = t.v1
    p2 = t.v2
    p3 = t.v3

    #initialize client side (CPU) arrays
    self.a = np.array(p1, dtype=np.int32)
    self.b = np.array(p2, dtype=np.int32)
    self.c =np.array(p3, dtype=np.int32)

    #create OpenCL buffers
    self.a_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.a)
    self.b_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.b)
    self.c_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.c)
    self.dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, self.b.nbytes)

    self.program.area2(self.queue, self.a.shape, None, self.a_buf, self.b_buf, self.c_buf, self.dest_buf)
    d = np.empty_like(self.a[0])
    cl.enqueue_read_buffer(self.queue, self.dest_buf, d).wait()
    print "a", self.a
    print "b", self.b
    print "c", d

    return d

def startTriangles(triangles, coords): # triangles tiene inicialmente el triang grande, coords solo los ptos interiores

    trs = []
    trs.append(triangles[0])

    for i in range(len(coords)):
        p = coords[i]

        for t in trs:
            print "ok"
            print p
            if utils.isInside(p, t):
                print "inside triangle"
                ccwCoords = utils.orderVertices([p, t.v1, t.v2])
                tn1 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
                ccwCoords = utils.orderVertices([p, t.v2, t.v3])
                tn2 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
                ccwCoords = utils.orderVertices([p, t.v3, t.v1])
                tn3 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])

                trs.append(tn1)
                trs.append(tn2)
                trs.append(tn3)

                #Esta es la parte de edge flip para Delaunay, ahora no la necesito
                """for nt in t.neighbors:
                    if nt is not None:
                        commonEdge = utils.findCommonEdge(nt, tn1)
                        if commonEdge != []:
                            outsider = utils.findOutsider(nt, commonEdge)
                            if circleTest(tn1, outsider) < 0:
                                ccwCoords = utils.orderVertices([p, commonEdge[0], outsider])
                                tnn1 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
                                ccwCoords = utils.orderVertices([p, commonEdge[1], outsider])
                                tnn2 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
                                tnn1.setNeighbor([tnn2, tn2, nt.neighbors[2]])
                                tnn2.setNeighbor([tn1, tnn1, nt.neighbors[0]])

                                trs.append(tnn1)
                                trs.append(tnn2)
                                trs.remove(nt)
                                trs.remove(tn1)
                for nt in t.neighbors:
                    if nt is not None:
                        commonEdge = utils.findCommonEdge(nt, tn2)
                        if commonEdge != []:
                            outsider = utils.findOutsider(nt, commonEdge)
                            if circleTest(tn2, outsider) < 0:
                                ccwCoords = utils.orderVertices([p, commonEdge[0], outsider])
                                tnn1 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
                                ccwCoords = utils.orderVertices([p, commonEdge[1], outsider])
                                tnn2 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
                                tnn1.setNeighbor([tnn2, tn2, nt.neighbors[2]])
                                tnn2.setNeighbor([tn1, tnn1, nt.neighbors[0]])

                                trs.append(tnn1)
                                trs.append(tnn2)
                                trs.remove(nt)
                                trs.remove(tn2)

                for nt in t.neighbors:
                    if nt is not None:
                        commonEdge = utils.findCommonEdge(nt, tn3)
                        if commonEdge != []:
                            outsider = utils.findOutsider(nt, commonEdge)
                            if circleTest(tn3, outsider) < 0:
                                ccwCoords = utils.orderVertices([p, commonEdge[0], outsider])
                                tnn1 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
                                ccwCoords = utils.orderVertices([p, commonEdge[1], outsider])
                                tnn2 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
                                tnn1.setNeighbor([tnn2, tn2, nt.neighbors[2]])
                                tnn2.setNeighbor([tn1, tnn1, nt.neighbors[0]])

                                trs.append(tnn1)
                                trs.append(tnn2)
                                trs.remove(nt)
                                trs.remove(tn3)"""
                trs.remove(t)
                break

    print "fin"
    return trs


def main():
    output = open("output", "w")

    pointsfile = sys.argv[1]
    coordsList = prepCoords(pointsfile)
    maxpointLex = getMax(coordsList)
    minpointLex = getMin(coordsList)

    coordsToAdd = copy.deepcopy(coordsList)

    k1 = (maxpointLex[0]-minpointLex[0])
    k2 = (maxpointLex[1]-minpointLex[1])
    k = 100*max(k1, k2)

    p1 = [0, -round(k/2)]
    p2 = [0, round(k/2)]
    p3 = [round(k/2), round(k/2)]

    print p1, p2, p3

    coordsList.append(p1)
    coordsList.append(p2)
    coordsList.append(p3)

    i = 0

    for c in coordsList:
        output.write(str(i) + " " + str(c[0]) + " " + str(c[1]) + "\n")
        i += 1

    ccwCoords = utils.orderVertices([p1, p2, p3])
    print ccwCoords[0], ccwCoords[1], ccwCoords[2]
    firstTriangle = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])

    allTriangles = []
    allTriangles.append(firstTriangle)

    triang = startTriangles(allTriangles, coordsToAdd)
    triang = utils.removeBigTriangle(triang, p1, p2, p3)

    for t in triang:
        output.write("# " + str(coordsList.index(t.v1)) + " " + str(coordsList.index(t.v2)) + " " + str(coordsList.index(t.v3)) + "\n")

    output.close()

if __name__ == "__main__":
    main()

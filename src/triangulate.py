__author__ = 'fran'

import sys
import numpy as np
import string as st
import copy
from Triangle import Triangle
import utils
import pyopencl as cl
import time


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
    """ Returns max lexicographic point
    :param coordsList: Numpy array of coordinates
    """
    maxpoint = coordsList[0]

    for i in range(len(coordsList)):
        if coordsList[i][0] > maxpoint[0]:
            if coordsList[i][1] > maxpoint[1]:
                maxpoint = coordsList[i]

    return maxpoint

def getMin(coordsList):
    """ Returns min lexicographic point
    :param coordsList: Numpy array of coordinates
    """
    minpoint = coordsList[0]

    for i in range(len(coordsList)):
        if coordsList[i][0] < minpoint[0]:
            if coordsList[i][1] < minpoint[1]:
                minpoint = coordsList[i]

    return minpoint


def triangulate_GPU(triangles, coords):
    newtriangles = [triangles[0]]
    gputime = 0

    platforms = cl.get_platforms()
    if len(platforms) == 0:
        print "Failed to find any OpenCL platforms."
        return None

    devices = platforms[0].get_devices(cl.device_type.GPU)
    if len(devices) == 0:
        print "Could not find GPU device, trying CPU..."
        devices = platforms[0].get_devices(cl.device_type.CPU)
        if len(devices) == 0:
            print "Could not find OpenCL GPU or CPU device."
            return None

    for p in coords:
        # Paso la info de triangles a un formato que pueda usar en un kernel de OpenCL
        tv1x, tv2x, tv3x = [], [], []
        tv1y, tv2y, tv3y = [], [], []

        for t in newtriangles:
            #print t
            tv1x.append(np.int32(t.v1[0]))
            tv1y.append(np.int32(t.v1[1]))
            tv2x.append(np.int32(t.v2[0]))
            tv2y.append(np.int32(t.v2[1]))
            tv3x.append(np.int32(t.v3[0]))
            tv3y.append(np.int32(t.v3[1]))

        tv1x = np.array(tv1x)
        tv1y = np.array(tv1y)
        tv2x = np.array(tv2x)
        tv2y = np.array(tv2y)
        tv3x = np.array(tv3x)
        tv3y = np.array(tv3y)

        px = p[0]*np.ones(len(tv1x))
        py = p[1]*np.ones(len(tv1x))

        ctx = cl.Context([devices[0]])
        queue = cl.CommandQueue(ctx)
        mf = cl.mem_flags

        tv1x_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=tv1x)
        tv1y_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=tv1y)
        tv2x_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=tv2x)
        tv2y_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=tv2y)
        tv3x_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=tv3x)
        tv3y_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=tv3y)
        px_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=px)
        py_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=py)

        dest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, tv1x.nbytes)

        f = open('isinside.cl', 'r')
        programName = "".join(f.readlines())

        program = cl.Program(ctx, programName).build()

        starttime = time.clock()
        program.isinside(queue, tv1x.shape, None, tv1x_buf, tv1y_buf, tv2x_buf, tv2y_buf,
                         tv3x_buf, tv3y_buf, px_buf, py_buf, dest_buf)
        endtime = time.clock()
        totaltime = endtime - starttime
        gputime = gputime + totaltime

        res_triangles = np.empty_like(tv1x)
        cl.enqueue_copy(queue, res_triangles, dest_buf)

        # triangle_index = indice del triangulo en triangles donde se encuentra el punto
        # currTriangle = triangulo que contiene al punto p
        triangle_index = np.nonzero(res_triangles)[0][0]
        currTriangle = newtriangles[triangle_index]

        # Ahora tengo que eliminar currTriangle y crear los 3 nuevos triangulos, esos los agrego a newtriangles
        ccwCoords = utils.orderVertices([p, currTriangle.v1, currTriangle.v2])
        tn1 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
        ccwCoords = utils.orderVertices([p, currTriangle.v2, currTriangle.v3])
        tn2 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
        ccwCoords = utils.orderVertices([p, currTriangle.v3, currTriangle.v1])
        tn3 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])

        newtriangles.append(tn1)
        newtriangles.append(tn2)
        newtriangles.append(tn3)

        newtriangles.remove(currTriangle)

    return newtriangles, gputime


def triangulate_CPU(triangles, coords):
    trs = []
    trs.append(triangles[0])

    for i in range(len(coords)):
        p = coords[i]

        for t in trs:
            if utils.isInside(p, t):
                ccwCoords = utils.orderVertices([p, t.v1, t.v2])
                tn1 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
                ccwCoords = utils.orderVertices([p, t.v2, t.v3])
                tn2 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])
                ccwCoords = utils.orderVertices([p, t.v3, t.v1])
                tn3 = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])

                trs.append(tn1)
                trs.append(tn2)
                trs.append(tn3)

                trs.remove(t)
                break
    return trs


def main():
    output = open("output", "w")

    pointsfile = sys.argv[1]
    coordsList = prepCoords(pointsfile)
    maxpointLex = getMax(coordsList)
    minpointLex = getMin(coordsList)

    coordsToAdd = copy.deepcopy(coordsList)

    # Defino bounding triangle inicial
    k1 = (maxpointLex[0]-minpointLex[0])
    k2 = (maxpointLex[1]-minpointLex[1])
    k = 100*max(k1, k2)

    p1 = [0, -round(k/2)]
    p2 = [0, round(k/2)]
    p3 = [round(k/2), round(k/2)]

    coordsList.append(p1)
    coordsList.append(p2)
    coordsList.append(p3)

    i = 0

    for c in coordsList:
        output.write(str(i) + " " + str(c[0]) + " " + str(c[1]) + "\n")
        i += 1

    ccwCoords = utils.orderVertices([p1, p2, p3])
    firstTriangle = Triangle(ccwCoords[0], ccwCoords[1], ccwCoords[2])

    allTriangles = []
    allTriangles.append(firstTriangle)

    # Triangulacion CPU
    start = time.clock()
    triangCPU = triangulate_CPU(allTriangles, coordsToAdd)
    end = time.clock()
    print("CPU: %f s" % (end - start))

    # Triangulacion GPU
    triang, gputime = triangulate_GPU(allTriangles, coordsToAdd)
    print("GPU: %f s" % (gputime))

    triangCPU = utils.removeBigTriangle(triangCPU, p1, p2, p3)

    for t in triang:
        output.write("# " + str(coordsList.index(t.v1)) + " " + str(coordsList.index(t.v2)) + " " + str(coordsList.index(t.v3)) + "\n")

    output.close()

if __name__ == "__main__":
    main()

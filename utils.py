import numpy as np
import math
import copy


'''Distancia entre puntos a y b'''
def distance(a, b):
        return np.sqrt(np.pow(b[0]-a[0], 2) + np.pow(b[1]-a[1], 2))


'''Punto medio entre a y b'''
def midpoint(a, b):
        return [(b[0]+a[0])/2.0, (b[1]+a[1])/2.0]


'''Test de la orientacion para el punto p
con respecto a la arista ab'''
def orientationTest(a, b, p):
    return (b[1] - a[1]) * (p[0] - a[0]) - (p[1] - a[1]) * (b[0]-a[0])


""" Determinando si un punto esta dentro
    del triangulo..."""
def signP(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])


def isInside(p, t):
    v1 = t.v1
    v2 = t.v2
    v3 = t.v3
    b1 = signP(p, v1, v2) < 0.0
    b2 = signP(p, v2, v3) < 0.0
    b3 = signP(p, v3, v1) < 0.0

    return b1 == b2 and b2 == b3


""" Elimina el bounding triangle del output, para graficar"""
def removeBigTriangle(triangles, p1, p2, p3):
    newtriangles = []
    for t in triangles:
        if t.v1 not in [p1, p2, p3] and t.v2 not in [p1, p2, p3] and t.v3 not in [p1, p2, p3]:
            newtriangles.append(t)
    return newtriangles


'''Distancia entre punto p y segmento lp1-lp2'''
def pointLineDistance(p, lp1, lp2):
    a = abs(((lp2[0] - lp1[0]) * (lp1[1] - p[1])) - ((lp1[0] - p[0]) * (lp2[1] - lp1[1])))
    b = np.sqrt(math.pow((lp2[0] - lp1[0]), 2) + math.pow((lp2[1] - lp1[1]), 2))

    return a/b


'''Test del circulo'''
def circleTest(t, d):
    a = t.v1
    b = t.v2
    c = t.v3
    mat = [[1, a[0], a[1], (a[0] * a[0] + a[1] * a[1])],
           [1, b[0], b[1], (b[0] * b[0] + b[1] * b[1])],
           [1, c[0], c[1], (c[0] * c[0] + c[1] * c[1])],
           [1, d[0], d[1], (d[0] * d[0] + d[1] * d[1])]]

    return np.linalg.det(mat)


'''Encuentra la arista comun entre dos triangulos vecinos'''
def findCommonEdge(t1, t2):
    t1vertices = [t1.v1, t1.v2, t1.v3]
    t2vertices = [t2.v1, t2.v2, t2.v3]

    common = []

    for v in t1vertices:
        if v in t2vertices:
            common.append(v)
            break

    for b in t1vertices:
        if b in t2vertices and b!=common[0]:
            common.append(b)

    return common


""" Dados un triangulo y un edge, retorna el vertice
    del triangulo que no pertence a dicho edge."""
def findOutsider(t, edge):
    vertices = [t.v1, t.v2, t.v3]

    for v in vertices:
        if v not in edge:
            return v



'''Encuentra el angulo en el punto p'''
def getAngle(p1, p, p2):
    a = np.sqrt(math.pow((p1[1] - p2[1]), 2) + math.pow((p1[0] - p2[0]), 2))
    b = np.sqrt(math.pow((p1[1] - p2[1]), 2) + math.pow((p1[0] - p[0]), 2))
    c = np.sqrt(math.pow((p[1] - p2[1]), 2) + math.pow((p[0] - p2[0]), 2))

    if a != 0 and b != 0 and c != 0:
        d = np.power(b, 2) + np.power(c, 2) - np.power(a, 2)
        e = 2 * b * c

        return np.arccos(d/e)


'''Retorna angulo minimo del triangulo t'''
def minAngle(t):
    ang1 = getAngle(t.v3, t.v1, t.v2) #Angulo en v1
    ang2 = getAngle(t.v1, t.v2, t.v3) #Angulo en v2
    ang3 = getAngle(t.v2, t.v3, t.v1) #Angulo en v3

    arr = [ang1, ang2, ang3]

    return min(arr)


'''Retorna indice de vertice mas a la izquierda de un array'''
def getLeftmost(vertices):
    minx = min([vertices[0][0], vertices[1][0], vertices[2][0]])

    for i in range(len(vertices)):
        if minx == vertices[i][0]:
            return i


'''Retorna el vertice de mas abajo'''
def getLower(v1, v2):
    miny = min([v1[1], v2[1]])

    if(miny == v1[1]):
        return v1
    else: 
        return v2


'''Entrega los vertices en orden antihorario'''
def orderVertices(vertices):
    lmi = getLeftmost(vertices)
    rightvertices = copy.deepcopy(vertices)
    rightvertices.remove(vertices[lmi]) #Dejo los dos vertices restantes (los de la derecha)

    if orientationTest(vertices[lmi], rightvertices[0], rightvertices[1]) < 0:
        return [vertices[lmi], rightvertices[0], rightvertices[1]]
    else:
        return [vertices[lmi], rightvertices[1], rightvertices[0]]



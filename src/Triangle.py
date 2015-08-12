class Triangle:
    '''Un triangulo tiene la estructura: v1,v2,v3,n1,n2,n3,ind1,ind2,ind3
    se define en sentido antihorario:
    v1: primer vertice (el de mas a la izquierda)
    v2: puntero vertice 2
    v3: puntero vertice 3
    n1, n2, n3: triangulos vecinos, opuestos al vertice respectivo
    ind1, ind2, ind3: True arista restringida, False no restringida (arista opuesta al vertice)'''

    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.neighbors = [None, None, None]
        self.ind1 = False
        self.ind2 = False
        self.ind3 = False
        self.status = 0  # 0=libre, 1=ocupado
        self.flipped = 0  # 0 sin flip, 1 flipeado

    def setNeighbor(self, n):
        self.neighbors = n




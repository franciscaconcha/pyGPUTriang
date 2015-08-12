#pragma OPENCL EXTENSION cl_khr_fp64 : enable
#define EPS 0.05

int area2(int x1, int y1, int x2, int y2, int x3, int y3){
   return abs((x1*(y2-y3) + x2*(y3-y1)+ x3*(y1-y2)));
}

/* Determina si el punto (x, y) se encuentra en la bounding box +- epsilon
 * del triangulo ((x1, y1), (x2, y2), (x3, y3)), vertices en orden CCW.
 */
int pointInBoundingBox(x1, y1, x2, y2, x3, y3, x, y)
{
    float xMin = min(x1, min(x2, x3)) - EPS;
    float xMax = max(x1, max(x2, x3)) + EPS;
    float yMin = min(y1, min(y2, y3)) - EPS;
    float yMax = max(y1, max(y2, y3)) + EPS;

    if ( x < xMin || xMax < x || y < yMin || yMax < y )
        return 0; // Point is not inside the bounding box
    else
        return 1; // Point is inside the bounding box
}

/* Calcula la distancia entre el punto (x, y) y el segmento ((x1, y1), (x2, y2)).
 * Esta distancia la retorna al cuadrado, para no tener que calcular raiz.
 */
int distanceSquarePointToSegment(x1, y1, x2, y2, x, y)
{
    int p1_p2_squareLength = (x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1);
    float dotProduct = ((x - x1)*(x2 - x1) + (y - y1)*(y2 - y1)) / p1_p2_squareLength;

    if ( dotProduct < 0 ){
        return (x - x1)*(x - x1) + (y - y1)*(y - y1);
    }else if ( dotProduct <= 1 ){
        int p_p1_squareLength = (x1 - x)*(x1 - x) + (y1 - y)*(y1 - y);
        return p_p1_squareLength - dotProduct * dotProduct * p1_p2_squareLength;
    }else{
        return (x - x2)*(x - x2) + (y - y2)*(y - y2);
    }
}


__kernel void isinside(__global int* vertex1x, __global int* vertex1y, __global int* vertex2x, __global int* vertex2y, __global int* vertex3x, __global int* vertex3y, __global int* px, __global int* py, __global int* res)
{
    const int i = (int)get_global_id(0);

    int v1x = vertex1x[i];
    int v1y = vertex1y[i];
    int v2x = vertex2x[i];
    int v2y = vertex2y[i];
    int v3x = vertex3x[i];
    int v3y = vertex3y[i];
    int ppx = px[i];
    int ppy = py[i];

    if(pointInBoundingBox(v1x, v1y, v2x, v2y, v3x, v3x, ppx, ppy) == 0){
        // Punto no esta en la bounding box, o sea no puede estar dentro del triangulo
        res[i] = 0;
    }else{ //Punto esta dentro de bounding box del triangulo, hay que ver si esta realmente dentro del triangulo
        int s1 = (ppx - v2x) * (v1y - v2y) - (v1x - v2x) * (ppy - v2y);
        int s2 = (ppx - v3x) * (v2y - v3y) - (v2x - v3x) * (ppy - v3y);
        int s3 = (ppx - v1x) * (v3y - v1y) - (v3x - v1x) * (ppy - v1y);

        bool b1 = (s1 < 0);
        bool b2 = (s2 < 0);
        bool b3 = (s3 < 0);

        bool b4 = (b1 == b2);
        bool b5 = (b2 == b3);
        bool b6 = b4 && b5;

        /*int A = area2(v1x, v1y, v2x, v2y, v3x, v3y);
        int A1 = area2(ppx, ppy, v2x, v2y, v3x, v3y);
        int A2 = area2(v1x, v1y, ppx, ppy, v3x, v3y);
        int A3 = area2(v1x, v1y, v2x, v2y, ppx, ppy);
        bool b6 = (A == A1 + A2 + A3);*/

        int r = (int)b6;

        if(r == 1){ // El punto esta dentro del triangulo
            res[i] = 1;
        }else{
            // Si dice que el punto esta afuera, hay que poner ojo, puede estar justo en el borde del triangulo
            if(distanceSquarePointToSegment(v1x, v1x, v2x, v2y, ppx, ppy) <= EPS*EPS){
                res[i] = 1;
            }
            if(distanceSquarePointToSegment(v2x, v2x, v3x, v3y, ppx, ppy) <= EPS*EPS){
                res[i] = 1;
            }
            if(distanceSquarePointToSegment(v3x, v3x, v1x, v1y, ppx, ppy) <= EPS*EPS){
                res[i] = 1;
            }
        }
    }
}
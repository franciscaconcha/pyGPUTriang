**********************************************************************
	    	NON-DELAUNAY Triangulation Algorithm
		     with (some) GPU support :)
**********************************************************************
              By Francisca Concha Ramírez -- August 2015
           Assignment for course CC5502 Computational Geometry
	   Computer Science Department - Universidad de Chile
**********************************************************************

## About:
- This program uses an incremental algorithm, as would be done for a Delaunay
  triangulation, but skipping the edge flips.
- Some GPU support provided - checking which triangle contains the point to
  be added is implemented in parallel.
- Also includes a random coordinates generator and a small plotting script

### WARNINGS! When running on GPU...
- The GPU part has A LOT of precision problems that I'm trying to fix. 
  If you want to use it, do so at your own risk (for now!)
- Some drivers may present some problems of not detecting your GPU device.
  If this happens, try running the program as root.

## Requirements:
- Python 2.7 or higher
- OpenCL 1.2
- pyOpenCL bindings
- All the necessary drivers and support for your specific GPU

## Running:
-To generate random points for the triangulation:

        python pointsGen.py n_of_points low_limit high_limit

`low_limit` and `high_limit` are the coordinate limits. The random points will be created inside a square of side length `high_limit-low_limit`. The script will output a file with the coordinates of the points.

- To create triangulation from the random points:

        python triangulate.py input_coordinates_file

- To plot the triangulation:

	    python plot.py

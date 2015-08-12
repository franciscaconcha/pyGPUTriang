**************************************************************
	    	NON-DELAUNAY Triangulation Algorithm
		     with (some) GPU support :)
**************************************************************
         By Francisca Concha Ramírez -- faconcha@dcc.uchile.cl
          Assignment for course CC5502 Computational Geometry
		              August 2015
	 Computer Science Department - Universidad de Chile
***************************************************************

----------------------------------ABOUT-----------------------------------
- This program uses an incremental algorithm, as would be done for a Delaunay
  triangulation, but skipping the edge flips.
- Some GPU support provided - checking which triangle contains the point to
  be added is implemented in parallel.
- Also includes a random coordinates generator and a small plotting script


------------------*** WARNINGS! When running on GPU... ***-----------------
- The GPU part has A LOT of precision problems that I'm tryin to fix. 
  If you want to use it, do so at your own risk (for now!)
- Some drivers may present some problems of not detecting your GPU device.
  If this happens, try running the program as root.


--------------------------------REQUIREMENTS------------------------------
- Python 2.7 or higher
- OpenCL 1.2
- pyOpenCL bindings
- All the necessary drivers and support for your specific GPU


----------------------------------RUNNING---------------------------------
- To run the points generator:
	python pointsGen.py <n of points> <low limit> <high limit>
	--> Will generate n coordinates with values between high and low

- To run the triangulations:
	python triangulate.py [OPTION] input_coordinates_file
	
	OPTIONS: 
	
		-C: run on CPU 
		-G: run on GPU
		none: will run BOTH!

- To plot:
	python plot.py

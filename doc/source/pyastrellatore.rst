pyastrellatore.py - how to use
===========================================

The Python script pyastrellatore.py helps to create some sequences of 
tiles, ordered and organized in folders, that can be used for Leaflet, a 
JavaScript library to visualize a geographical map using some tiles.
This script uses some modules, between which

- "os"; 
- "io"; 
- "matplotlib.pyplot";
- "PIL"; 
- "numpy"; 
- "mpl_toolkits.basemap"; 
- "multiprocessing"; 
- "netCDF4".

There are three constants to set, according to the user preferences.

- BASEWIDTH is the width of the image base after its resize. The default value is 256; in this way the tiles will be created with a width of 256 pixel and the height of 127 pixel.
- OUTPUT_DIR is the path of the directory with which will be saved the tiles.
- NPROC is the number of cores that the user want to use to execute the program.
- ZOOM, with which the user has to specify the number of zoom level he wants to create.

Interestingly, the resolution of the map changes with the zoom level.

The tiles will be created with a hierarchy of directories:

- Firstly the folders of the zoom level "z", which go from 0 to the level "ZOOM".
- Secondly the folders of the x coordinate (columns); their number is 2^ZOOM for every zoom level, starting from 0.
- Thirdly the tiles, saved as .png files in every folder; every tile is numbered following the order of tiles in every column from 0 to y, which value is  2^ZOOM (counting the 0).



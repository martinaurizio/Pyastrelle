datiMirto.py - how to use
=========================================

The Python script datiMirto.py helps to create a layer of tiles that contain
graphical data. 
This script uses some modules, among all:

- "matplotlib";
- "numpy";
- "io";
- "mpl_toolkits.basemap"
- "PIL"
- "netCDF4"
- "os"
- "multiprocessing"
- "matplotlib.pyplot"
- "pyastrellatore", the script pyastrellatore.py from which we need the functions "coordinate", "zoom_indices" and "genera_pyastrella".

The user can set three constants, which are:

- OUTPUT_DIR, the path of the folders with the tiles.
- NPROC is the number of cores that that the user wants to use to execute the program.
- ZOOM, with which the user has to specify the number of zoom level he wants to create.


According to a file given by the user, this script can choose when to create a tile 
with graphical data, using the script pyastrellatore.py,  or a transparent tile.

The tiles will be created with a hierarchy of directories:

- Firstly the folders of the zoom level “z”, which go from 0 to the level “ZOOM”.
- Secondly the folders of the x coordinate (columns); their number is 2^ZOOM for every zoom level, starting from 0.
- Thirdly the tiles, saved as .png files in every folder; every tile is numbered following the order of tiles in every column from 0 to y, which value is 2^ZOOM (counting the 0).


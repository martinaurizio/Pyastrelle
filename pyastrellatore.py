import os
from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from mpl_toolkits.basemap import Basemap, cm
from multiprocessing import pool
from netCDF4 import Dataset

BASEWIDTH = 256
OUTPUT_DIR = "/home/martina/Scrivania/UltimatePyastrellatore"
NPROC = 2
ZOOM = 1

'''
pyastrellatore is a Python script which produces 
some sequences of tiles organized in folders.
According to the zoom level, the tiles will be 
created and arranged into the respective folders.
'''

def coordinate(z, x, y):
	'''
	According to the zoom level 'z' and the position
	of the tile (x and y), this function returns the
	coordinates (latitude and longitude) of the lower
	left corner and the upper right corner of the tile. 
	'''
	npLato=2**z #number of the tiles along the side
	
	lat = 180/npLato #angular size in latitude of the tile
	lon = 360/npLato #angular size in longitude of the tile
	
	lon_min=-180+lon*x
	lon_max=lon_min+lon
	
	lat_max=90-lat*y			
	lat_min=lat_max-lat
		
	return (lat_min, lon_min, lat_max, lon_max)

def crop(mappa):
	'''
	This function removes the white space round the tile
	'''	
	map_io = BytesIO() #it is reserved a zone of the RAM to save the figure
	mappa.savefig(map_io) #it saves the figure in the zone just created
	map_io.seek(0)
	im = Image.open(map_io) #it opens the figure as an image
	
	#it opens the image as an array of sequential numbers
	im_data_raw = np.array(im.getdata(), dtype=np.uint8)
	
	#the image has to be thought as a bidimensional array of 32 bit numbers
	im_data_raw.dtype = np.uint32
	im_array = im_data_raw.reshape(im.size[0], im.size[1])

	bianco = 255*256**3+255*256**2+255*256+255

	x_no_bianco, y_no_bianco = np.where(im_array!=bianco)
	
	x0 = x_no_bianco[0]
	y0 = y_no_bianco[0]
	x1 = x_no_bianco[-1]
	y1 = y_no_bianco[-1]

	im = im.crop((y0, x0, y1, x1))
	
	return(im)


def resize(mappa):
	'''
	It modifies the dimensions of the tile
	'''

	wpercent = (BASEWIDTH / float(mappa.size[0]))
	hsize = int((float(mappa.size[1]) * float(wpercent)))
	mappa = mappa.resize((BASEWIDTH, hsize), Image.ANTIALIAS)
	
	return (mappa)
	
	
def genera_pyastrella(z, x, y, risoluzione='l', pll=20, datiM=False):
	'''
	It creates the tile for the zoom level z and following the coordinates
	x and y, used for the function "coordinate". It colors the tile and it
	draws the coastlines; so it calls the function "crop" which removes the
	white space round the tile.
	If this function is called by the datiMirto.py script, the boolean 
	variable datiM becomes True and the function genera_pyastrella draws
	graphic data on the map.
	'''
	
	fg=Dataset('fg_complete.nc','r')
	atmc=fg.groups["atmospheric_components"]
	t=atmc.variables['skT'][:]
	t-=272.15
	lat=fg.variables["Latitude"][:]
	lon=fg.variables["Longitude"][:]
	fg.close()
	
	npLato = 2**z
	lat0, lon0, lat1, lon1 = coordinate(z, x, y)
	
	fig = plt.figure(figsize=(8,8)) #it creates the figure used by Basemap to draw the map
	
	m = Basemap(projection='cyl', llcrnrlat=lat0, urcrnrlat=lat1,
           		llcrnrlon=lon0, urcrnrlon=lon1 , resolution=risoluzione)
	
	m.fillcontinents(color='#CD853F',lake_color='#66B2FF', zorder=0)
	m.drawmapboundary(fill_color='#66B2FF',color='None')
	m.drawcoastlines()
	
	if datiM == True:
		jet=plt.cm.get_cmap('jet')
		x, y = m(lon, lat)
		sc=plt.scatter(x,y, c=t, vmin=np.min(t), vmax=np.max(t), cmap=jet, s=pll ,edgecolors='none')
	
	figura = crop(fig)
	figura = resize(figura)
	plt.close()
	return figura

def zoom_indices(z):
	'''
	This function returns a list of all the valid indices x and y 
	of the tiles created from the zoom level z
	'''
	indices = []
	
	for i in range(0, 2**z):
		
		for j in range(0, 2**z):
			indices.append((i, j))
			
	return indices
	

if __name__ == '__main__':

	
	for z in range (0, ZOOM+1):
		zdir = os.path.join(OUTPUT_DIR,"{}".format(z))
		os.mkdir(zdir)
		
		for x in range (2**z):
			xdir = os.path.join(zdir, "{}".format(x))
			os.mkdir(xdir)
			
		def f(p):
			x = p[0]
			y = p[1]
			'''
			According to the zoom level z, the resolution of the map 
			changes from intermediate to high
			'''
			if z > 3 and z < 7:
				risoluzione = 'i'
			elif z > 6:
				risoluzione = 'h'
			pyastrella = genera_pyastrella(z, x, y, risoluzione)
			pyastrella.save(os.path.join(zdir, "{}/{}.png".format(x, y)))	
		
		p = pool.Pool(processes = NPROC)
		p.map(f, zoom_indices(z))
		p.close()
			
			
			
			
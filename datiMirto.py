import matplotlib as mpl
mpl.use('Agg')
from pyastrellatore import coordinate, zoom_indices, genera_pyastrella
import numpy as np
from io import BytesIO
from mpl_toolkits.basemap import Basemap, cm
from PIL import Image
from netCDF4 import Dataset
import os
from multiprocessing import pool
import matplotlib.pyplot as plt

BASEWIDTH = 256
OUTPUT_DIR = "/home/martina/Scrivania/UltimatePyastrellatore/"
NPROC = 1

'''
datiMirto is a Python script which manages the tiles, choosing when
it creates a new tile with some graphic data or when it saves a 
transparent tile.
Those tiles will be applied on the layer of the tiles created by
the only script pyastrellatore.py
'''

def controllo(lat0, lon0, lat1, lon1):
	fg=Dataset('fg_complete.nc','r')
	atmc=fg.groups["atmospheric_components"]
	t=atmc.variables['skT'][:]
	t-=272.15
	lat3=fg.variables["Latitude"][:]
	lon3=fg.variables["Longitude"][:]
	fg.close()
	
	verifica = True
	
	lat_0= np.min(lat3)
	lat_1= np.max(lat3)
	lon_0= np.min(lon3)
	lon_1= np.max(lon3)	
	if lat1 < lat_0:
		verifica = False	
	if lat0 > lat_1:
		verifica = False	
	if lon0 > lon_1:
		verifica = False
	if lon1 < lon_0:
		verifica = False

	return verifica
			

def trasparente():
	'''
	'''
	array_trasparente = np.zeros((127, 256, 4), dtype = np.uint8)
	im_trasparente = Image.fromarray(array_trasparente)
	
	map_io = BytesIO() #it is reserved a zone of the RAM to save the figure
	im_trasparente.save(map_io, format="png") #it saves the figure in the zone just created
	map_io.seek(0)
	return map_io

imTrasparente = trasparente()

def salva_trasparente(output_path):
	'''
	'''
	with open(output_path, 'wb') as f:
		f.write(imTrasparente.read())
	imTrasparente.seek(0)
		
def genera_dati_mirto(z, x, y, risoluzione, pll):
	'''
	This function calls the pyastrellatore.py function to create a 
	'''
	figura = genera_pyastrella(z, x, y, risoluzione, pll, True)
	
	return(figura)
	
if __name__ == '__main__':
	zoom = 6
	
	for z in range (zoom, zoom+1):
		zDir = os.path.join(OUTPUT_DIR, "{}".format(z))
		os.mkdir(zDir)
		
		for x in range (2**z):
			xDir = os.path.join(zDir, "{}".format(x))
			os.mkdir(xDir)
		
		def f(p):
			risoluzione='l'
			pll = 20
			x = p[0]
			y = p[1]
			lat0, lon0, lat1, lon1 = coordinate(z, x, y)
			verifica = controllo(lat0, lon0, lat1, lon1)
			if verifica == False:
				salva_trasparente(os.path.join(zDir, "{}/{}.png".format(x, y)))
			else:
				'''
				According to the zoom level z, the resolution of the map 
				changes from intermediate to high
				'''
				if z > 3 and z < 7:
					risoluzione = 'i'
				elif z > 6:
					risoluzione = 'h'
				'''
				According to the zoom level z, it changes the ray of the 
				circle for the	graphic data to apply on the map
				'''
				if z == 5:
					pll = 50
				elif z == 6:
					pll = 150
				elif z == 7:
					pll = 250
				elif z == 8:
					pll = 350
				
				piastrella = genera_dati_mirto(z, x, y, risoluzione, pll)
				piastrella.save(os.path.join(zDir, "{}/{}.png".format(x, y)), facecolor="none")

		p = pool.Pool(processes=NPROC)
		p.map(f, zoom_indices(z))
		p.close()
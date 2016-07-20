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
OUTPUT_DIR = "/home/lorenzo/Documenti/Finale/Pyastrelle/" 
NPROC = 1 
''' datiMirto è uno script python che permette di generare delle piastrelle trasparenti (senza 
il profilo dei continenti mondiali) con i dati presi dalle misurazioni di 
Mirto. ''' 
def controllo(lat0, lon0, lat1, lon1):
	fg=Dataset('../../../fg_complete.nc','r')
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
	
	map_io = BytesIO() #viene riservata una zona di ram per salvare la figura
	im_trasparente.save(map_io, format="png") #salva la figura nella zona appena generata
	map_io.seek(0)
	return map_io imTrasparente = trasparente() 

def salva_trasparente(output_path):
	with open(output_path, 'wb') as f:
		f.write(imTrasparente.read())
	imTrasparente.seek(0)
		
def genera_dati_mirto(z, x, y):
	
	fig=plt.figure(figsize=(8,8))
	
	return(figura)
	
if __name__ == '__main__':
	zoom = 1
	
	for z in range (0, zoom+1):
		zDir = os.path.join(OUTPUT_DIR, "{}".format(z))
		os.mkdir(zDir)
		
		for x in range (2**z):
			xDir = os.path.join(zDir, "{}".format(x))
			os.mkdir(xDir)
		
		def f(p):
			risoluzione='l'
			x = p[0]
			y = p[1]
			lat0, lon0, lat1, lon1 = coordinate(z, x, y)
			verifica = controllo(lat0, lon0, lat1, lon1)
			if verifica == False:
				salva_trasparente(os.path.join(zDir, "{}/{}.png".format(x, y)))
			else:
				 if z > 3 and z < 7:
                                	risoluzione='i'
        			elif z >6:
                                	risoluzione='h'
				piastrella = genera_dati_mirto(z, x, y)
				piastrella.save(os.path.join(zDir, "{}/{}.png".format(x, y)), facecolor="none")
		p = pool.Pool(processes=NPROC)
		p.map(f, zoom_indices(z))
		p.close()

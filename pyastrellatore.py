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

'''
pyastrellatore e' uno script python che ha lo scopo di produrre
una sequenza di piastrelle organizzate in cartelle.
In base al livello di zoom verranno elaborate le varie 
piastrelle ed organizzate nelle rispettive cartelle.
'''

def coordinate(z, x, y):
	'''
	In base al livello di zoom z e alla posizione della piastrella
	individuata dalle coordinate x e y, ritorna le coordinate 
	(latitudine e longitudine) del punto in basso a sinistra e di
	quello in alto a destra della piastrella da creare
	'''
	npLato=2**z #numero di piastrelle per lato al livello z di zoom
	
	lat = 180/npLato #dimensione angolare in latitudine della piastrella
	lon = 360/npLato #dimensione angolare in longitudine della piastrella
	
	lon_min=-180+lon*x
	lon_max=lon_min+lon
	
	lat_max=90-lat*y			
	lat_min=lat_max-lat
		
	return (lat_min, lon_min, lat_max, lon_max)

def crop(mappa):
	'''
	rimuove il colore bianco esterno alla piastrella generata
	'''	
	map_io = BytesIO() #viene riservata una zona di ram per salvare la figura
	mappa.savefig(map_io) #salva la figura nella zona appena generata
	map_io.seek(0)
	im = Image.open(map_io) #riapre la figura come immagine
	
	#viene riaperta l'immagine come un array di numeri in sequenza
	im_data_raw = np.array(im.getdata(), dtype=np.uint8)
	#im_data = im_data_raw.reshape(im.size[0], im.size[1], 4)
	
	#l'immagine va pensata come un array bidimensionale di numeri a 32 bit
	im_data_raw.dtype = np.uint32
	im_array = im_data_raw.reshape(im.size[0], im.size[1])

	bianco = 255*256**3+255*256**2+255*256+255

	
	x_no_bianco, y_no_bianco = np.where(im_array!=bianco)
	
	x0 = x_no_bianco[0]
	y0 = y_no_bianco[0]
	x1 = x_no_bianco[-1]
	y1 = y_no_bianco[-1]

	im = im.crop((y0, x0, y1, x1))
	#print(y0, x0, y1, x1)
	#m.save("/home/martina/Scrivania/UltimatePyastrellatore/prova.png")		
	
	return(im)


def resize(mappa):
	'''
	Modifica la risoluzione della piastrella
	'''

	wpercent = (BASEWIDTH / float(mappa.size[0]))
	hsize = int((float(mappa.size[1]) * float(wpercent)))
	mappa = mappa.resize((BASEWIDTH, hsize), Image.ANTIALIAS)
	
	return (mappa)
	
	
def genera_pyastrella(z, x, y, risoluzione='l', pll=20, datiM=False):
	'''
	Genera la piastrella per lo zoom z e seguendo le coordinate x e y, utilizzate
	per la funzione "coordinate". Colora la piastrella e disegna le coste.
	Richiama quindi la funzione "crop" per eliminare gli spazi bianchi ai bordi
	della piastrella
	'''
	
	#aggiunti
	fg=Dataset('fg_complete.nc','r')
	atmc=fg.groups["atmospheric_components"]
	t=atmc.variables['skT'][:]
	t-=272.15
	lat=fg.variables["Latitude"][:]
	lon=fg.variables["Longitude"][:]
	fg.close()
	
	
	
	npLato = 2**z
	lat0, lon0, lat1, lon1 = coordinate(z, x, y)
	
	fig = plt.figure(figsize=(8,8)) #genera la figura su cui Basemap genererà la mappa
	
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
	ritorna una lista di tutti i validi indici x e y delle 
	piastrelle di zoom z da generare
	'''
	indices = []
	
	for i in range(0, 2**z):
		
		for j in range(0, 2**z):
			indices.append((i, j))
			
	return indices
	

if __name__ == '__main__':
	#c = coordinate(1, 0, 1)
	zoom =1
	
	for z in range (0, zoom+1):
		zdir = os.path.join(OUTPUT_DIR,"{}".format(z))
		os.mkdir(zdir)
		
		for x in range (2**z):
			xdir = os.path.join(zdir, "{}".format(x))
			os.mkdir(xdir)
		def f(p):
			x = p[0]
			y = p[1]
			if z > 3 and z < 7:
				risoluzione = 'i'
			elif z > 6:
				risoluzione = 'h'
			pyastrella = genera_pyastrella(z, x, y, risoluzione)
			pyastrella.save(os.path.join(zdir, "{}/{}.png".format(x, y)))	
		
		p = pool.Pool(processes = NPROC)
		
		p.map(f, zoom_indices(z))
		
		p.close()
			
			
			
			
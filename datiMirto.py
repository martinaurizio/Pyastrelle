from pyastrellatore import coordinate, zoom_indices, genera_pyastrella, crop, resize
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
datiMirto è uno script python che permette di generare delle piastrelle
trasparenti (senza il profilo dei continenti mondiali) con i dati
presi dalle misurazioni di Mirto.
'''

def trasparente():
	'''
	'''
	array_trasparente = np.zeros((127, 256, 4), dtype = np.uint8)
	im_trasparente = Image.fromarray(array_trasparente)
	
	map_io = BytesIO() #viene riservata una zona di ram per salvare la figura
	im_trasparente.save(map_io, format="png") #salva la figura nella zona appena generata
	map_io.seek(0)
	return map_io

imTrasparente = trasparente()

def salva_trasparente(output_path):
	with open(output_path, 'wb') as f:
		f.write(imTrasparente.read())
		
def genera_dati_mirto(z, x, y):
	
	fg=Dataset('fg_complete.nc','r')
	atmc=fg.groups["atmospheric_components"]
	t=atmc.variables['skT'][:]
	t-=272.15
	lat3=fg.variables["Latitude"][:]
	lon3=fg.variables["Longitude"][:]
	fg.close()

	fig=plt.figure(figsize=(8,8))
	
	figura = genera_pyastrella(z, x, y)
	'''
	lat0, lon0, lat1, lon1 = coordinate(z, x, y)
	
	m = Basemap(projection='cyl', llcrnrlat=lat0, urcrnrlat=lat1, \
            llcrnrlon=lon0, urcrnrlon=lon1, \
            resolution='c')
	

	m.drawmapboundary(fill_color='none', color="none")
	m.drawcoastlines(color="none")
	'''
	jet=plt.cm.get_cmap('jet')
	x, y = figura(lon3, lat3)
	sc=plt.scatter(x,y, c=t, vmin=np.min(t), vmax=np.max(t), cmap=jet, s=20 ,edgecolors='none')
	'''
	map_io = BytesIO() #viene riservata una zona di ram per salvare la figura
	fig.savefig(map_io, facecolor= 'none', format="png") #salva la figura nella zona appena generata
	map_io.seek(0)
	figC = crop(fig)
	figR= resize(figC)
	'''
	
	figura = crop(figura)
	figura = resize(figura)
	plt.show()
	plt.close()
	
	return(figR)

#imMirto = genera_dati_mirto(z, x, y)

def salva_mirto(output_path):
	with open(output_path, 'wb') as f:
		f.write(imMirto.read())
		
def resize(imP):
	'''
	'''
	wpercent=(BASEWIDTH/float(imP.size[0]))
	hsize = int((float(imP.size[1])*float(wpercent)))
	imP = imP.resize((BASEWIDTH, hsize), Image.ANTIALIAS)
	return(imP)


def crop(mappa):
	'''
	rimuove il colore bianco esterno alla piastrella
	'''
	map_io = BytesIO() #viene riservata una zona di ram per salvare la figura
	mappa.savefig(map_io, facecolor="none") #salva la figura nella zona appena generata
	map_io.seek(0)
	im = Image.open(map_io) #riapre la figura come immagine
	
	
	im_data_raw = np.array(im.getdata(), dtype=np.uint8)
	
	im_data_raw.dtype = np.uint32
	im_array = im_data_raw.reshape(im.size[0], im.size[1])

	bianco = 255*256**3+255*256**2+255*256+255
	
	#x_bianco, y_bianco = np.where(im_array==bianco)

	for aaa in range (0, im_array.shape[0]):
		for bbb in range(0, im_array.shape[1]):
			if im_array[aaa][bbb] == bianco:
				im_array[aaa][bbb] = 0
				
	im_array=im_array.flatten()
	im_array.dtype = np.uint8
	im_array = im_array.reshape(im.size[0], im.size[1], 4)
	im=Image.fromarray(im_array.astype('uint8'))
	
	im = im.crop((100, 245, 719, 554))
	
	return(im)

	
if __name__ == '__main__':
	zoom = 1
	
	genera_dati_mirto(3, 0, 2)
	
	'''
	
	valori = zoom_indices(zoom)
	mappa = trasparente()
	genera_dati_mirto()
	salva_mirto("./map.png")
	'''
	
	
	'''for n in range (0, 2**zoom):
		x = valori[n][0]
		y = valori[n][1]
		lat_min, lon_min, lat_max, lon_max = coordinate(zoom, x, y)'''
	
	
	for z in range (0, zoom+1):
		zDir = os.path.join(OUTPUT_DIR, "{}".format(z))
		os.mkdir(zDir)
		
		for x in range (2**z):
			xDir = os.path.join(zDir, "{}".format(x))
			os.mkdir(xDir)
		
		def f(p):
			x = p[0]
			y = p[1]
			piastrella = genera_dati_mirto(z, x, y)

			piastrella.save(os.path.join(zDir, "{}/{}.png".format(x, y)), facecolor="none")

		p = pool.Pool(processes=NPROC)
		p.map(f, zoom_indices(z))
		p.close()
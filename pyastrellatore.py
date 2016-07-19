'''
Pyastrellatore e' uno script che ha lo scopo di produrre 
una sequenza di piastrelle organizzate in cartelle.
In base al livello di zoom verranno elaborate le varie 
piastrelle 
'''
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')
from mpl_toolkits.basemap import Basemap, cm
from io import BytesIO 
from PIL import Image
import numpy as np
from multiprocessing import pool
import datiMirto

BASEWIDTH = 256
OUTPUT_DIR="/home/lorenzo/Documenti/mappaMondo/"
NPROC=1

def coordinate(z,x,y):
    '''
    In base al livello di zoom z e alla posizione della 
    piastrella individuata dalle coordinate x e y, ritorna le coordinate
    del punto in basso a sinistra e di quello in alto a destra dela 
    piastrella da creare
    '''
    npLato = 2**z #numero di piastrelle per lato a livello z di zoom
    
    lat_dim = 180/npLato #dimensione angolare della latitudine della piastrella
    lon_dim = 360/npLato #dimensione angolare della longitudine della piastrella

    lon_min = -180+lon_dim*x
    lon_max = lon_min+lon_dim

    lat_max = 90-lat_dim*y
    lat_min = lat_max-lat_dim
            
    return(lat_min, lon_min, lat_max, lon_max)

def crop(mappa):
    '''
    Rimuove il colore bianco esterno alla piastrella
    '''
    mappa_io = BytesIO()#viene riservata una zona di RAM per salvare la figura 
    mappa.savefig(mappa_io)#salvo la figura nella zona appena generata
    mappa_io.seek(0)
    im = Image.open(mappa_io)#riapro la figura come immagine
    
    #riapro l' immagine come un array di numeri in sequenza
    im_data_raw = np.array(im.getdata(), dtype=np.uint8)
    
    #im_data = im_data_raw.reshape(im.size[0], im.size[1], 4)
    
    #penso all'immagine come un array bidimensionale di numeri a 32 bit
    im_data_raw.dtype = np.uint32
    im_array = im_data_raw.reshape(im.size[0], im.size[1])
    bianco = (255*256**3 + 255*256**2 + 255*256 +255)

    x_no_bianco, y_no_bianco = np.where(im_array!=bianco)
    x0 = x_no_bianco[0]
    y0 = y_no_bianco[0]
    x1 = x_no_bianco[-1]
    y1 = y_no_bianco[-1]
    
    print(x0,y0,x1,x1)
    im = im.crop((y0, x0, y1, x1))
  
    return(im)

def resize(mappa):
    '''
    '''
    wpercent = (BASEWIDTH / float(mappa.size[0]))
    hsize = int((float(mappa.size[1]) * float(wpercent)))
    mappa = mappa.resize((BASEWIDTH, hsize), Image.ANTIALIAS)
        
    return(mappa)

def generaPiastrella(z, x, y, risoluzione='l'):
    '''
    Dato un livello di zoom z, le coordinate x e y , il livello di risoluzione,
    genero la mappa
    '''
    #Genero la figura su cui basemap genera la mappa
    fig = plt.figure(figsize=(8,8))
    npLato = 2**z
    lat0, lon0, lat1, lon1 = coordinate(z, x ,y)
    if z >3 & z<8:
        risoluzione='i'
        
    m = Basemap(projection='cyl', llcrnrlat=lat0, urcrnrlat=lat1, 
                llcrnrlon=lon0, urcrnrlon=lon1, resolution=risoluzione)
            
    m.fillcontinents(color='#CD853F', lake_color='#66B2FF')
    m.drawmapboundary(fill_color='#66B2FF', color='none')
    m.drawcoastlines()
    
    
	#if controllo():
	#	figura=generaDatiMirto(z,x,y)
	#else 
	#	salvaTrasparente('{}/{}/{}.png'.format(z,x,y))
	
    figura=crop(fig)
    figura=resize(figura)
    plt.close()
	
    return(figura)

def controllo():
	tipo='true'
	

	return()

def zoomIndices(z):
    '''
    Ritorna una lista di tutti i validi indice x e y per delle piastrelle di zoom z
    '''
    indices=[]
    for i in range(0,2**z):
        for j in range(0,2**z):
            indices.append((i,j))
            
    return(indices)

	
	
#main
if __name__== '__main__':
        
        zoom=0
        for z in range(0,zoom+1):
            zDir = os.path.join(OUTPUT_DIR,"{}".format(z))
            os.mkdir(zDir)
            
            for x in range(2**z):
                xDir = os.path.join(zDir,"{}".format(x))
                os.mkdir(xDir)
            def f(p):
                x = p[0]
                y = p[1]
                piastrella = generaPiastrella(z, x, y)
                piastrella.save(os.path.join(zDir,"{}/{}.png".format(x,y)))
            
            p=pool.Pool(processes=NPROC)
            p.map(f, zoomIndices(z))
            p.close()     














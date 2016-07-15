'''
datiMirto e' uno script che permette di generare delle piastrelle trasparenti
insieme alle piastrelle con i dati
'''
from Pyastrellatore import coordinate, zoomIndices
from mpl_toolkits.basemap import Basemap, cm
import matplotlib.pyplot as plt
import numpy as np
import os
from io import BytesIO 
from PIL import Image
from netCDF4 import Dataset
from multiprocessing import pool

BASEWIDTH = 256
OUTPUT_DIR="/home/lorenzo/Documenti/mappaMondo/"
NPROC=1

def generaTrasparente():
    
    arrayTrasparente= np.zeros((127,256,4), dtype=np.uint8)
    imTrasparente = Image.fromarray(arrayTrasparente)
    
    map_io = BytesIO()#viene riservata una zona di RAM per salvare la figura 
    imTrasparente.save(map_io, format="png")#salvo la figura nella zona appena generata
    map_io.seek(0)   
    return(map_io)

imTr = generaTrasparente()

def salvaTrasparente(output_path):
    with open(output_path, "wb") as f:
        f.write(imTr.read())

def generaDatiMirto(z, x, y):
    
    fg=Dataset("fg_complete.nc",'r')
    t=fg.groups["atmospheric_components"].variables['skT'][:]
    t-=272.15
    lat=fg.variables["Latitude"][:]
    lon=fg.variables["Longitude"][:]
    fg.close()
    
    fig=plt.figure(figsize=(8,8))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    
    lat0, lon0, lat1, lon1 = coordinate(z, x ,y)

    imMirto = Basemap(projection='cyl', llcrnrlat=lat0, urcrnrlat=lat1, 
                      llcrnrlon=lon0, urcrnrlon=lon1, resolution='c')
    
    imMirto.drawcoastlines(color="none")
    
    jet=plt.cm.get_cmap('jet')
    x, y = imMirto(lon, lat)
    sc=plt.scatter(x,y, c=t, vmin=np.min(t), vmax=np.max(t), cmap=jet, s=20 ,edgecolors='none')
    
    
    map_io = BytesIO()#viene riservata una zona di RAM per salvare la figura 
    fig.savefig(map_io, facecolor="none", format="png")#salvo la figura nella zona appena generata
    map_io.seek(0)
    
    return(map_io)


def salvaMirto(imMr, output_path):
    with open(output_path, "wb") as f:
        f.write(imMr.read())


def resize(imP):
    
    wpercent = (BASEWIDTH / float(imP.size[0]))
    hsize = int((float(imP.size[1]) * float(wpercent)))
    imP = imP.resize((BASEWIDTH, hsize), Image.ANTIALIAS)
    
    return(imP)

def crop():
    return()

def controlloPiastrella(z):
    return()




#main
if __name__== '__main__':
    
    zoom=2
    #valori=zoomIndices(zoom)
    #mappa = generaDatiMirto()
    #salvaMirto("/home/lorenzo/Documenti/mappaMondo/mMirto.png")
    
    for z in range(0,zoom+1):
            zDir = os.path.join(OUTPUT_DIR,"{}".format(z))
            os.mkdir(zDir)
            
            for x in range(2**z):
                xDir = os.path.join(zDir,"{}".format(x))
                os.mkdir(xDir)
            def f(p):
                x = p[0]
                y = p[1]
                piastrella = generaDatiMirto(z, x, y)
                
                salvaMirto(piastrella, os.path.join(zDir,"{}/{}.png".format(x,y)))
            
            p=pool.Pool(processes=NPROC)
            p.map(f, zoomIndices(z))
            p.close()     
    
    #for i in range(0, 2**zoom):
     #   x=valori[i][0]
    #    y=valori[i][1]
       # lat_min, lon_min, lat_max, lon_max = coordinate(zoom, x, y)
    
    
    
    

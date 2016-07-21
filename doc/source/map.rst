Generate the map
=================================

The two scripts pyastrellatore.py and datiMirto.py have created two sequences of folders 
with the tiles.
It's better to separate the two layers of tiles creating one folder for every sequence of
directories, for example one folder named "tiles" and one folder named "data".
The two folders have to be put on a server, for example Apache2.
Using Apache2, the two folders have to be put in the directory /var/www, for example:

- /var/www/maps

Then the file 000-default.conf (situated in the directory /etc/apache2/sites-available)
has to be changed writing a line with the Document Root, under the ServerAdmin, 
for example:

- DocumentRoot /var/www/maps

So the server can be restarted, using (for Apache2):

- sudo service apache2 restart

We need to use Leaflet to visualize the map; we have to create an .html file, writing 
the normal tags of a simple html page:

``<html>``

``<head>``

``</head>``

``<body>``

``Leaflet space``

``</body>``

``</html>``

Instead of "Leaflet space", we have to add the lines about our layers.

``mymap = L.map('mapid').setView([45, 20], 8);``

``L.tileLayer("http://1.2.3.4/tiles/{z}/{x}/{y}.png").addTo(mymap);``

``L.tileLayer("http://1.2.3.4/data/{z}/{x}/{y}.png").addTo(mymap);``
 
"mymap" contains the map; the two numbers 45 and 20 are the two coordinates (latitude and
longitude) of the initial point of the map that we have to visualize when we open the 
html page; 8 is the number of the zoom level.

The last two lines are the layers. 
Instead of 1.2.3.4 the user has to change with the IP address of the server that contains
the two folders with the tiles.

"tiles" and "data" are the name of the folders with the tiles.
z, x and y are, respectively, the zoom level, the x coordinate (column) and the y 
coordinate (line, the name of the tile).

Using this sequence, Leaflet can assemble the tiles and create a map that contains
all the graphical data.


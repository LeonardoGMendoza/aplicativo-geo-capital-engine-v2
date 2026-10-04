import re

with open('frontend/mapa_interativo.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Change 1: Update abrirWaze and abrirGMaps functions
c = c.replace(
    '''function abrirWaze(lat,lon){\n  window.open('https://waze.com/ul?ll='+lat+','+lon+'&navigate=yes','_blank');\n}''',
    '''function abrirWaze(lat,lon){\n  var wz = "https://www.waze.com/live-map/directions?navigate=yes&to=ll."+lat+"%2C"+lon+"&from=ll."+uLat+"%2C"+uLng;\n  window.open(wz, '_blank');\n}'''
)
c = c.replace(
    '''function abrirGMaps(lat,lon){\n  window.open('https://www.google.com/maps/dir/?api=1&destination='+lat+','+lon,'_blank');\n}''',
    '''function abrirGMaps(lat,lon){\n  var gm = "https://www.google.com/maps/dir/?api=1&origin="+uLat+","+uLng+"&destination="+lat+","+lon;\n  window.open(gm, '_blank');\n}'''
)

with open('frontend/mapa_interativo.py', 'w', encoding='utf-8', newline='') as f:
    f.write(c)

print('mapa patched 2.')

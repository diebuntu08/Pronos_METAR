#!/usr/bin/python3
#-*-coding: utf-8-*-

from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re

hoy = datetime.utcnow()

URL_BASE = 'https://www.ogimet.com/display_metars2.php?lugar=mroc&tipo=SA&ord=REV&nil=SI&fmt=txt&ano={}&mes={}&day={}&hora={}&anof={}&mesf={}&dayf={}&horaf={}&minf=05&enviar=Ver'
url = URL_BASE.format(hoy.year, str(hoy.month).zfill(2), str(hoy.day).zfill(2), str(hoy.hour).zfill(2), hoy.year, str(hoy.month).zfill(2), str(hoy.day).zfill(2), str(hoy.hour).zfill(2))
req = requests.get(url)

statusCode = req.status_code
if statusCode == 200:
	html = BeautifulSoup(req.text, "html.parser")
	entrada = html.find('pre')
else:
	print("La página no existe o no es accesible.")

f = open("texto.txt", 'w')
f.write(str(entrada))
f.close()
print(entrada)
metar = entrada.find('MROC').getText()

print('.....................................\n')
lista = metar.split(' ')
for elm in lista:
	print(elm)
	
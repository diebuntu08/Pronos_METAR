#!/usr/bin/python
#-*-coding: utf-8-*-

from datetime import datetime
from calendar import monthrange
from time import sleep
import re
import urllib.request

def convertir_a_string(valor):
	if valor < 10:
		string = '0' + str(valor)
	else:
		string = str(valor)
	return string

def encuentra_posicion(archivo, patron):
	for linea in archivo:
		acierto = patron.search(linea)
		if acierto:
			linea = archivo.readline()
			break
			
def remplaza_iguales(cadena):
	for x in range(0,3):
		cadena = cadena.replace("  "," ")
		cadena = cadena.replace("==","=")
		cadena = cadena.replace(" =","=")
	return cadena
			
def acomoda_metares(archivo, linea, linea_ant):
	try:
		fecha = int(linea[0:11])
		estado = 0        
	except ValueError:
		estado = 1
	
	igual = linea.count("=")
	if estado == 0 and igual == 0:
		linea_ant = linea[0:len(linea)-1]
	elif estado == 1 and igual == 0:
		linea_ant = linea_ant + linea[23:len(linea)-1]
	elif estado == 0 and igual == 1:
		linea = remplaza_iguales(linea)
		linea = linea.replace("WS R", "WSR")
		archivo.write(linea)
#		print(linea)
	elif estado == 1 and igual == 1:
		linea_ant = linea_ant + linea[23:len(linea)-1]
		linea_ant = remplaza_iguales(linea_ant)
		linea_ant = linea_ant.replace("WS R", "WSR")
		archivo.write(linea_ant + "\n")
#		print(linea_ant)
	return linea_ant

hoy = datetime.today()
anios = [x for x in range(2005, 2020)]
meses = [y for y in range(1, 13)]
for year in anios:
	f3 = open('files/' + str(year) + '.txt', 'w')
	for month in meses:
		fecha = datetime(year, month, 1, 0, 0, 0)
		anio = fecha.year
		print(anio)
		mes = convertir_a_string(fecha.month)
		print(month)
		dia_ini = convertir_a_string(fecha.day)
		month_range = monthrange(fecha.year, fecha.month)
		dia_fin = convertir_a_string(month_range[1])
		print(dia_fin)

		direccion = 'http://ogimet.com/display_metars2.php?lugar=MROC&tipo=SA&ord=DIR&nil=SI&fmt=txt&ano=%i&mes=%s&day=%s&hora=00&anof=%i&mesf=%s&dayf=%s&horaf=23&minf=59&enviar=Ver'
		while True:
			try:
				url = direccion%(anio, mes, dia_ini, anio, mes, dia_fin)
				r = urllib.request.urlopen(url)
				texto = r.read().decode('iso-8859-1')
				break
			except:
				sleep(30)
				continue
			

		f1 = open('textow.txt', 'w')
		f1.write(texto)
		f1.close()

		f2 = open('textow.txt', 'r')

		formato = r'METAR/SPECI\sde\sMROC'
		patron = re.compile(formato)
		encuentra_posicion(f2, patron)
		linea_ant = 'texto'
		for linea in f2:
			if linea[0] == '\n':
				break
			else:
				linea_ant = acomoda_metares(f3, linea, linea_ant)
		for x in range(300, 0, -1):
			print(x)
			sleep(1)
		f2.close()
	f3.close()


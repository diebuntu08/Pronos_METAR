#!/usr/bin/python
#-*-coding: utf-8-*-

from datetime import datetime
import re

hoy = datetime.utcnow()

lista = [x for x in range(2005, hoy.year)]

formato = r'VRB\d{2}KT|VRB\d{2}G\d{2}KT|\d{5}KT|\d{5}G\d{2}KT'
#formato = r'\d{5}KT9999|\d{5}G\d{2}KT9999'
#formato = r'A\d{4}|A////'
#formato = r'\d{2}/\d{2}|/////|\d{2}///|///\d{2}'
#formato = r'A29(85|86|87|88|89)'
#formato_fecha = r'\d{4}01\d{2}2200'
#formato = r'\s\d{4}\s|\s\d{4}([A-Z]|[A-Z][A-Z])\s|\sCAVOK\s'
#formato = r'\d{6}Z'
#formato = r'NOSIG|BECMG|TEMPO|RMK|REMARK|A\d{4}='
patron = re.compile(formato)
#patron_fecha = re.compile(formato_fecha)

log = open('log.txt', 'w')

for anio in lista:
	#f = open('files/' + str(anio) + '.txt', 'r')
	f = open('nuevos/' + str(anio) + '.txt', 'r')
	for linea in f:
		nil = linea.count('NIL')
		if nil != 0:
			continue
		#print(linea)
		#linea = linea.replace('=', '')
		#linea = linea.replace('\n', '')
		linea = re.sub(r'\s+', ' ', linea)
		#lista = linea.split(' ')
		#for elemento in lista:
		acierto = patron.search(linea)
		#acierto_fecha = patron_fecha.match(linea)
			#acierto = patron.search(elemento)
		if acierto: #and acierto_fecha:
		#		presion = float(elemento.replace('A', '')) / 100
		#		if presion > 30.25 or presion < 29.80:
		#	print(linea)
		#	log.write(linea + '\n')
			continue
		else:
			print(linea)
			log.write(linea + '\n')
			continue
	log.write('##############################################################################\n\n')
	log.write('##############################################################################\n')
	f.close()
log.close()

#!/usr/bin/python
#-*-coding: utf-8-*-

from datetime import datetime
import re

hoy = datetime.utcnow()

anios = [x for x in range(2019, hoy.year)]

FORMATOS = {
			'viento': r'VRB\d{2}KT|VRB\d{2}G\d{2}KT|\d{5}KT|\d{5}G\d{2}KT',
			'viento_vis':	r'\d{5}KT9999|\d{5}G\d{2}KT9999',
			'presion': r'A\d{4}|A////',
			'temperaturas': r'\d{2}/\d{2}|/////|\d{2}///|///\d{2}',
			'presion_80s': r'A29(85|86|87|88|89)',
			'fecha': r'\d{4}01\d{2}2200',
			'visibilidad': r'\s\d{4}\s|\s\d{4}([A-Z]|[A-Z][A-Z])\s|\sCAVOK\s',
			'hora': r'\d{6}Z',
			'tendencia': r'NOSIG|BECMG|TEMPO|RMK|REMARK|A\d{4}='
}
#patron_fecha = re.compile(fecha)
patron = re.compile(FORMATOS['presion'])

log = open('log.txt', 'w')

def verificar_valor():
	for anio in anios:
		f = open('files/{}.txt'.format(anio), 'r')

		for linea in f:
			nil = linea.count('NIL')
			if nil != 0:
				continue

			linea = re.sub(r'\s+', ' ', linea)
			metar = linea.split(' ')

			for elemento in metar:
				#acierto = patron.search(linea)
				#acierto_fecha = patron_fecha.match(linea)
				acierto = patron.match(elemento)
				if acierto:
					presion = float(elemento.replace('A', '')) / 100
					if presion > 30.25 or presion < 29.80:
						print(linea)
						log.write(linea + '\n')
					else:
						continue
		log.write('##############################################################################\n\n')
		log.write('##############################################################################\n')
		f.close()

def verificar_estado():
	for anio in anios:
		f = open('files/{}.txt'.format(anio), 'r')

		for linea in f:
			nil = linea.count('NIL')
			if nil != 0:
				continue

			linea = re.sub(r'\s+', ' ', linea)

			#acierto = patron.search(linea)
			#acierto_fecha = patron_fecha.match(linea)
			acierto = patron.search(linea)
			if acierto:
				continue
			else:
				print(linea)
				log.write(linea + '\n')
		log.write('##############################################################################\n\n')
		log.write('##############################################################################\n')
		f.close()


#verificar_valor()
#verificar_estado()

log.close()

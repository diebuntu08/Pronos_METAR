#!/usr/bin/python
#-*-coding: utf-8-*-

from datetime import datetime, timedelta
import re
import time

hoy = datetime.utcnow()

anios = [x for x in range(2005, hoy.year)]

station = 'MRLB'

def files_dir(anio):
    return f'files/{station}/{anio}.txt'

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
patron = re.compile(FORMATOS['viento'])

log = open('log.txt', 'w')

def verificar_valor():
	for anio in anios:
		f = open(files_dir(anio), 'r')

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
					valor = float(elemento.replace('A', '')) / 100
					if valor > 30.25 or valor < 29.80:
						print(linea)
						log.write(linea + '\n')
					else:
						continue
		log.write('##############################################################################\n\n')
		log.write('##############################################################################\n')
		f.close()

def verificar_estado():
	for anio in anios:
		f = open(files_dir(anio), 'r')

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

def verificar_fechas():
    for anio in anios:
        f = open(files_dir(anio), 'r')
        fecha_inicial = datetime.strptime(f'{anio}01010000', '%Y%m%d%H%M')
        
        for linea in f:
            linea = re.sub(r'\s+', ' ', linea)
            
            metar = linea.split(' ')
            fecha_metar = metar[0]
            
            if not fecha_metar.endswith('00'):
                continue
            
            fecha_comparar = datetime.strftime(fecha_inicial, '%Y%m%d%H%M')
            # if fecha_metar != fecha_comparar:
            #     # print(fecha_metar, fecha_comparar)
            #     # time.sleep(2)
            #     log.write(fecha_comparar + '\n')
            #     fecha_inicial += timedelta(hours=2)
            # else:            
            # 	fecha_inicial += timedelta(hours=1)
            while fecha_metar != fecha_comparar:
                print(fecha_metar, fecha_comparar)
                time.sleep(0.2)
                fecha_inicial += timedelta(hours=1)
                fecha_comparar = datetime.strftime(fecha_inicial, '%Y%m%d%H%M')
                log.write(f"{fecha_comparar}\n")
            fecha_inicial += timedelta(hours=1)
        log.write('##############################################################################\n\n')
        log.write('##############################################################################\n')
        f.close()


#verificar_valor()
#verificar_estado()
verificar_fechas()

log.close()

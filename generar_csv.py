from datetime import datetime
import re

from utils.classes.metar_class import MetarClass

station = 'MROC'

f = open(f'files/{station}/metar_data.csv', 'w')

f.write('ANIO,MES,DIA,HORA,MINUTO,DIR,MAG,RAF,VIS,DZ,RA,SHRA,TSRA,BCFG,BR,FG,TEMP,DPTEMP,QNH,CAPA1,ALTURA1,CONVECTIVA1,CAPA2,ALTURA2,CONVECTIVA2,CAPA3,ALTURA3,CONVECTIVA3,CAPA4,ALTURA4,CONVECTIVA4,CAVOK,\n')

anios = [x for x in range(2005, 2020)]

def handle_metar(code):
    metar_date = code[0:12]
    metar = code[13:]
    date = datetime.strptime(metar_date, '%Y%m%d%H%M')
    return date, metar

# def create_metar_object()

for anio in anios:
    yfile = open(f'files/{station}/{anio}.txt', 'r')
    for line in yfile:
        print(line)
        metar_date, metar_text = handle_metar(line.replace('=', ''))
        metar = MetarClass(metar_date, metar_text)
        print(metar.time.year, metar.time.month, metar.time.day)
        print(metar.get_wind_dir())
        print(metar.sky)
        if metar.vis is not None:
        	print(metar.vis.value())
        print(metar.get_sky_conditions())
        print(metar.cavok)
#         print(metar_date)
#         data = extract_metar_data(metar_date, metar_text)
#         f.write(",".join(data) + "\n")
	#yfile.close()
f.close()

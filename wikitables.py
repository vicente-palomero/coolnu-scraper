#!/usr/bin/python
import sys, getopt
from bs4 import BeautifulSoup
import numpy as np
from urllib.request import urlopen

# Como usar esto:
# En caso de que haya tablas con filas dentro de una celda (véase 3 finalistas de un premio) hay que multiplicar
# las posiciones, los años y si hubiera bandera u otro campo por el número de finalistas. Ver abajo, lo que está
# comentado
#
# EJECUCIÓN DESDE CONSOLA
# Para que se vea por pantalla:
# python wikitables.py -u URL
#
# Para guardarlo en un archivo de texto (terminal Linux)
# python wikitables.py -u URL > /RUTA/DEL/ARCHIVO.csv
#
# EJECUCION DESDE ANACONDA O SIMILARES
# 1. Definir las variables "url", "prize", "year", "winner", "title", "info":
#   1. url: ruta completa de la wikipedia
#   2. prize: posición en la tabla de la columna de premios

#   3. year: posición en la tabla de la columna de año
#   4. winner: posición en la tabla de la columna de ganadores
#   5. title: posición en la tabla de la columna de nombres de las obras
#   6. info: para filas con info como "no presentado"
#
# Si se guarda como .csv se puede importar desde Google Spreadsheet sin problemas

url = "https://es.wikipedia.org/wiki/Premio_Biblioteca_Breve"
prize = "Breve"
year = 0 
winner = 2
title = 1 
info =  1
def run_by_url(url, prize, year, winner, title, info):
    read_tables(url, prize, year, winner, title, info)

def main(argv, prize, year, winner, title, info):
    url = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hu:", ["url="])
    except getopt.GetoptError:
        print('tables.py -u <url> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if (opt == '-h'):
            print('tables.py -u <url> -o <outputfile>')
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
        else:
            assert False, "unhandled option"

    read_tables(url, prize, year, winner, title, info)

def read_tables(url, prize, year, winner, title, info):
    bsObj = urlToBSoup(url)
    tables = bsObj.find_all('table', {'class': 'wikitable'})
    pos = 0
    for t in tables:
        pos = pos + 1
        table = read_table(t, str(pos), prize, year, winner, title, info)
        for r in table['body']:
            print(','.join(r))

def read_table(table, position, prize, year, winner, title, info):

    head_body = {'head': [], 'body': []}
    for tr in table.select('tr'):
        if all(t.name == 'th' for t in tr.find_all(recursive=False)):
            head_body['head'] += [th.get_text().rstrip('\n') for th in tr.find_all(recursive=False)]
        else:
            row = [td for td in tr.find_all(recursive=False)]
            info_value = row[info].get_text()
            shallContinue = 'No convocado' in info_value or 'Desierto' in info_value # Aquí cuando no se entregó el premio, por lo que sea. Cambiar para adaptar a textos "inválidos" de la tabla
            if shallContinue:
                continue
            pos = [position]
            # pos = [position, position, position] # Para ejemplos en los que hay celdas con hasta 3 filas
            oneYear = row[year].get_text().strip('\n')
            year1 = [oneYear]
            # year = [oneYear, oneYear, oneYear] # Para ejemplos en los que hay celdas con hasta 3 filas
            winners1 = [a.get_text().strip('\n') for a in row[winner].find_all('a')]
            flags = ["-", "-", "-"] #[span for span in row[2].find('span')] # No sé sacar bien el nombre del país
            titles1 = [i.text for i in row[title].findAll('i')]
            bodyRow1 = [list(a) for a in zip(year1, [prize], "1", winners1, titles1)]
            head_body['body'] += bodyRow1
            # Adaptado para la tabla del Nadal, marcado como FALSE para que no moleste
            if False and len(row) > 4:
                winners2 = [a.get_text().strip('\n') for a in row[winner + 2].find_all('a')]
                titles2 = [i.text for i in row[title+ 2].findAll('i')]
                bodyRow2 = [list(a) for a in zip(year, [prize], "2", winners2, titles2)]
                head_body['body'] += bodyRow2
    return head_body

def urlToBSoup(url):
    return BeautifulSoup(urlopen(url).read(), features = "html.parser")


if __name__ == "__main__":
    prize = "Breve" # Nombre en clave del premio
    year = 0 # Columna donde esta el anyo, empezando por 0
    winner = 2 # Columna donde esta el ganador, empezando por 0
    title = 1 # Columna donde esta el titulo, empezando por 0
    info = 1 # Esto es por si hay una fila desierta
    #run_by_url("https://es.wikipedia.org/wiki/Premio_Biblioteca_Breve", prize, year, winner, title, info)
    main(sys.argv[1:], prize, year, winner, title, info)

#!/usr/bin/python
import sys, getopt
from bs4 import BeautifulSoup
import numpy as np
from urllib.request import urlopen

# Como usar esto:
#  1. En el método read_table hay 5 variables. Estas variables deben ser adaptadas a:
#     a. Nombre del premio
#     b. Posición del año en la tabla
#     c. Posición del ganador / persona en la tabla
#     d. Posición del título en la tabla
#
# En "pos" está la posición (ganador/subganador) en caso de que haya varias tablas. Este valor viene del orden
# de la tabla, si es la primera o segunda.
#
# En caso de que haya tablas con filas dentro de una celda (véase 3 finalistas de un premio) hay que multiplicar
# las posiciones, los años y si hubiera bandera u otro campo por el número de finalistas. Ver abajo, lo que está
# comentado
#
# La salida es por consola

def main(argv):
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

    read_list(url)

def read_list(url):
    bsObj = urlToBSoup(url)
    ul_list = bsObj.find('table')
    for li in ul_list.find_all('li'):
        text = li.get_text().replace("(escritor", "")
        if "No se tienen datos" in text or "No celebrado" in text or "Desierto" in text:
            continue
        (year, text) = text.split(' ', 1)
        (author, title) = text.split("por", 1)
        print(','.join([year, 'Ateneo Sevilla', "1", author.strip(), title.strip()]))

def urlToBSoup(url):
    return BeautifulSoup(urlopen(url).read(), features = "html.parser")


if __name__ == "__main__":
    main(sys.argv[1:])

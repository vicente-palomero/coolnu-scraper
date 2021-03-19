#!/usr/bin/python
import sys, getopt
from bs4 import BeautifulSoup
import numpy as np
from urllib.request import urlopen

# Como usar esto:
#  1. En el método read_list hay 2 variables. Estas variables deben ser adaptadas a:
#     a. Nombre del premio
#     2. Posición del ganador / persona en la lista
#
# EJECUCIÓN
# Para que se vea por pantalla:
# python wiki_ullist.py -u URL
#
# Para guardarlo en un archivo de texto (terminal Linux)
# python wiki_ullist.py -u URL > /RUTA/DEL/ARCHIVO
#
# Si se guarda como .csv se puede importar desde Google Spreadsheet sin problemas

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
    prize = 'Ateneo Sevilla'
    winner = '1'
    bsObj = urlToBSoup(url)
    ul_list = bsObj.find('table')
    for li in ul_list.find_all('li'):
        text = li.get_text().replace("(escritor", "")
        if "No se tienen datos" in text or "No celebrado" in text or "Desierto" in text:
            continue
        (year, text) = text.split(' ', 1) # Esta línea separa el año del resto.
        (author, title) = text.split("por", 1) # Esta línea separa al autor del título (en el caso usado no hace falta más)
        print(','.join([year, prize, winner, author.strip(), title.strip()]))

def urlToBSoup(url):
    return BeautifulSoup(urlopen(url).read(), features = "html.parser")


if __name__ == "__main__":
    main(sys.argv[1:])

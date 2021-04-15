#!/usr/bin/python
import sys, getopt
from bs4 import BeautifulSoup
import numpy as np
from urllib.request import urlopen



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

    read_tables(url)

def read_tables(url):
    bsObj = urlToBSoup(url)
    tables = bsObj.find_all('table', {'class': 'wikitable'})
    pos = 0
    for t in tables:
        pos = pos + 1
        table = read_table(t, str(pos))
        for r in table['body']:
            print(','.join(r))

def read_table(table, position):
    prize = "Azorin"
    yearTablePosition = 0
    winnerTablePosition = 3
    titleTablePosition = 2
    whereInfoShouldBePosition = 1 # Esto es por si hay una fila desierta

    head_body = {'head': [], 'body': []}
    for tr in table.select('tr'):
        if all(t.name == 'th' for t in tr.find_all(recursive=False)):
            head_body['head'] += [th.get_text().rstrip('\n') for th in tr.find_all(recursive=False)]
        else:
            row = [td for td in tr.find_all(recursive=False)]
            info = row[whereInfoShouldBePosition].get_text()
            shallContinue = 'No convocado' in info or 'Desierto' in info # Aquí cuando no se entregó el premio, por lo que sea. Cambiar para adaptar a textos "inválidos" de la tabla
            if shallContinue:
                continue
            pos = [position]
            # pos = [position, position, position] # Para ejemplos en los que hay celdas con hasta 3 filas
            oneYear = row[yearTablePosition].get_text().strip('\n')
            year = [oneYear]
            # year = [oneYear, oneYear, oneYear] # Para ejemplos en los que hay celdas con hasta 3 filas
            winners1 = [a.get_text().strip('\n') for a in row[winnerTablePosition].find_all('a')]
            flags = ["-", "-", "-"] #[span for span in row[2].find('span')] # No sé sacar bien el nombre del país
            titles1 = [i.text for i in row[titleTablePosition].findAll('i')]
            bodyRow1 = [list(a) for a in zip(year, [prize], "1", winners1, titles1)]
            head_body['body'] += bodyRow1
            # Adaptado para la tabla del Nadal, marcado como FALSE para que no moleste
            if False and len(row) > 4:
                winners2 = [a.get_text().strip('\n') for a in row[winnerTablePosition + 2].find_all('a')]
                titles2 = [i.text for i in row[titleTablePosition + 2].findAll('i')]
                bodyRow2 = [list(a) for a in zip(year, [prize], "2", winners2, titles2)]
                head_body['body'] += bodyRow2
    return head_body

def urlToBSoup(url):
    return BeautifulSoup(urlopen(url).read(), features = "html.parser")


if __name__ == "__main__":
    main(sys.argv[1:])

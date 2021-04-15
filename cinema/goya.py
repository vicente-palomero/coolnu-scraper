#!/usr/bin/python
import sys, getopt
from bs4 import BeautifulSoup
import numpy as np
from urllib.request import urlopen

goya_path = 'https://es.wikipedia.org/wiki/Premios_Goya'
prize = 'goya'

def main(argv):
    url = goya_path
    read_tables(url)

def read_tables(url):
    bsObj = urlToBSoup(url)
    table = bsObj.find_all('table', {'class': 'wikitable'})[0]
    table_read = read_table(table)
    for r in table_read['body']:
        print(', '.join(r))

def read_table(table):
    head_body = {'head': [], 'body': []}
    movie_pos = 2
    director_pos = 3
    first_edition_year = 1986
    year = first_edition_year
    for tr in table.select('tr'):
        if all(t.name == 'th' for t in tr.find_all(recursive=False)):
            head_body['head'] += [th.get_text().rstrip('\n') for th in tr.find_all(recursive=False)]
        else:
            row = [td for td in tr.find_all(recursive=False)]
            movie, movie_director = row[movie_pos].get_text().rstrip().split('(de ')
            director = row[director_pos].get_text().split('\n')[0].split('  ')[0]
            bodyRow1 = [str(year), prize, movie.strip(), movie_director.rstrip(')'), director.split(' (')[0]]
            head_body['body'] += [bodyRow1]
            year = year + 1
    return head_body

def urlToBSoup(url):
    return BeautifulSoup(urlopen(url).read(), features = "html.parser")


if __name__ == "__main__":
    main(sys.argv[1:])


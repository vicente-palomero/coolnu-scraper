#!/usr/bin/python
import sys, getopt
from bs4 import BeautifulSoup
import numpy as np
from urllib.request import urlopen

feroz = [
    ('https://es.wikipedia.org/wiki/Anexo:Premio_Feroz_a_la_mejor_pel%C3%ADcula_dram%C3%A1tica','feroz drama', 2, 3, -1),
    ('https://es.wikipedia.org/wiki/Anexo:Premio_Feroz_a_la_mejor_comedia','feroz comedia', 2, 3, -1),
    ('https://es.wikipedia.org/wiki/Anexo:Premio_Feroz_a_la_mejor_direcci%C3%B3n','feroz director', -1, -1, 2),
]

def main(argv):
    for (url, prize, movie_pos, movie_director_pos, director_pos) in feroz:
        read_tables(url, prize, movie_pos, movie_director_pos, director_pos)

def read_tables(url, prize, movie_pos, movie_director_pos, director_pos):
    bsObj = urlToBSoup(url)
    table = bsObj.find_all('table', {'class': 'wikitable'})[0]
    table_read = read_table(table, prize, movie_pos, movie_director_pos, director_pos)
    for r in table_read['body']:
        print(', '.join(r))

def read_table(table, prize, movie_pos, movie_director_pos, director_pos):
    head_body = {'head': [], 'body': []}
    year_pos = 1
    for tr in table.select('tr'):
        if all(t.name == 'th' for t in tr.find_all(recursive=False)):
            head_body['head'] += [th.get_text().rstrip('\n') for th in tr.find_all(recursive=False)]
        else:
            row = [td for td in tr.find_all(recursive=False)]
            movie = '' if (movie_pos == -1) else row[movie_pos].get_text().strip()
            movie_director = '' if (movie_director_pos == -1) else row[movie_director_pos].get_text().strip()
            director = '' if (director_pos == -1) else row[director_pos].get_text().strip()
            year = row[year_pos].get_text().strip()
            bodyRow1 = [year, prize, movie, movie_director, director]
            head_body['body'] += [bodyRow1]
    return head_body

def urlToBSoup(url):
    return BeautifulSoup(urlopen(url).read(), features = "html.parser")


if __name__ == "__main__":
    main(sys.argv[1:])

#!/usr/bin/python
import sys, getopt
from bs4 import BeautifulSoup
import numpy as np
from urllib.request import urlopen

feroz = [
    ('https://es.wikipedia.org/wiki/Anexo:Premio_Turia_a_la_mejor_pel%C3%ADcula_espa%C3%B1ola', 'turia pelicula', 1, 2, -1),
]

def main(argv):
    for (url, prize, movie_pos, movie_director_pos, director_pos) in feroz:
        read_tables(url, prize, movie_pos, movie_director_pos, director_pos)

def read_tables(url, prize, movie_pos, movie_director_pos, director_pos):
    bsObj = urlToBSoup(url)
    tables = bsObj.find_all('table', {'class': 'wikitable'})
    for table in tables:
        output = read_table(table, prize, movie_pos, movie_director_pos, director_pos)
        for r in output ['body']:
            print(', '.join(r))

def read_table(table, prize, movie_pos, movie_director_pos, director_pos):
    head_body = {'head': [], 'body': []}
    year_pos = 0
    for tr in table.select('tr'):
        if all(t.name == 'th' for t in tr.find_all(recursive=False)):
            head_body['head'] += [th.get_text().rstrip('\n') for th in tr.find_all(recursive=False)]
        else:
            row = [td for td in tr.find_all(recursive=False)]
            row_length = len(row)
            correction = 1 if row_length == 2 else 0
            movie = '' if (movie_pos == -1) else row[movie_pos - correction].get_text().strip()
            if (movie in ['No hubo certamen', 'Desierto']):
                continue
            movie_director = '' if (movie_director_pos == -1) else row[movie_director_pos - correction].get_text().strip()
            director = '' if (director_pos == -1) else row[director_pos - correction].get_text().strip()
            if (director in ['No hubo certamen', 'Desierto']):
                continue
            year = year if correction else row[year_pos].get_text().strip().lstrip('´')
            bodyRow1 = [year, prize, movie, movie_director, director]
            head_body['body'] += [bodyRow1]
    return head_body

def urlToBSoup(url):
    return BeautifulSoup(urlopen(url).read(), features = "html.parser")


if __name__ == "__main__":
    main(sys.argv[1:])

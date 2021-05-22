#!/usr/bin/python
import sys, getopt
from bs4 import BeautifulSoup
import numpy as np
from urllib.request import urlopen

links = [
    ('https://en.wikipedia.org/wiki/Academy_Award_for_Best_Director', 'director', 2, 1),
]

def main(argv):
    for (url, prize, movie_pos, director_pos) in links:
        read_tables(url, prize, movie_pos, director_pos)

def read_tables(url, prize, movie_pos, director_pos):
    bsObj = urlToBSoup(url)
    tables = bsObj.find_all('table', {'class': 'wikitable'})
    for table in tables:
        caption = table.find('caption')
        if (caption and caption.get_text().strip() == 'Table key'):
            continue
        output = read_table(table, prize, movie_pos, director_pos)
        for r in output ['body']:
            print(', '.join(r))

def read_table(table, prize, movie_pos, director_pos):
    head_body = {'head': [], 'body': []}
    year_pos = 0
    max_cells = 4
    pivot = 0
    for tr in table.select('tr'):
        if all(t.name == 'th' for t in tr.find_all(recursive=False)):
            head_body['head'] += [th.get_text().rstrip('\n') for th in tr.find_all(recursive=False)]
            if (head_body['head'][0] != 'Year'):
                break
        else:
            row = [td for td in tr.find_all(recursive=False)]
            if (len(row) == 5):
                row.pop()
            cells = len(row)
            if (cells == 2):
                pivot = 1
            elif (cells == 1):
                pivot = 2
            else:
                pivot = 0
            dir_cell = row[director_pos - pivot]
            if (cells != 1):
                director = '' if (director_pos == -1) else dir_cell.get_text().strip()
            movie = '' if (movie_pos == -1) else row[movie_pos - pivot].get_text().strip()
            if (cells == max_cells):
                year = row[year_pos].get_text().strip().lstrip('´')
            is_winner = '1' if str(dir_cell).find('background') != -1 else '0'
            bodyRow1 = [year, movie, director, is_winner]
            head_body['body'] += [bodyRow1]
    return head_body

def urlToBSoup(url):
    return BeautifulSoup(urlopen(url).read(), features = "html.parser")


if __name__ == "__main__":
    main(sys.argv[1:])

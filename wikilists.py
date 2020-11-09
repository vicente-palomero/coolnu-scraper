#!/usr/bin/python
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
import csv
import sys, getopt
from bs4 import BeautifulSoup
from bs4 import re

def main(argv):
    url = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hu:o:", ["url=","ofile="])
    except getopt.GetoptError:
        print('scrap.py -u <url> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if (opt == '-h'):
            print('wikilists.py -u <url> -o <outputfile>')
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        else:
            assert False, "unhandled option"

    urls = []
    result = []
    openHRef(url, urls, result)

    with open(outputfile, mode="w") as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['title', 'href'])
        for r in result:
            writer.writerow([r[0], r[1]])

def openHRef(url, urls, result):
    if (url in urls):
        return

    urls.append(url)

    bsObj = urlToBeautifulSoup(url)
    container = bsObj.find('div', {'id': 'mw-pages'})
    nextPage = container.find('a', {'href': re.compile("/w/.*#mw-pages")})
    anchors = container.findAll('a', {'href': re.compile("/wiki/.*")})

    for a in anchors:
        if a['href'] not in result:
            result.append((a['title'], a['href']))

    if nextPage is not None:
        openHRef('https://es.wikipedia.org{}'.format(nextPage['href']), urls, result)


def urlToBeautifulSoup(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        raise e
    except URLError as e:
        raise e
    return BeautifulSoup(html.read(), features = "html.parser")

if __name__ == "__main__":
    main(sys.argv[1:])

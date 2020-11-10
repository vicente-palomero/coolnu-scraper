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
        print('wikiannex.py -u <url> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if (opt == '-h'):
            print('wikiannex.py -u <url> -o <outputfile>')
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        else:
            assert False, "unhandled option"

    bsObj = urlToBeautifulSoup(url)
    ids = bsObj.findAll('span', {'class': 'mw-headline'})
    elements = {}
    for id in ids:
        element = {}
        name = id.get_text()
        element['name'] = name
        if (name == 'Referencias'):
            break
        parent = id.parent
        article = parent.find_next_sibling()
        if (article is not None and article.name == 'div'):
            articleHref = article.find('i').find('a')['href']
            element['href'] = articleHref
            nextNode = parent.find_next_sibling()
        while True:
            if (nextNode.name == 'ul'):
                break
            elif (nextNode.name == 'h2'):
                break
            nextNode = nextNode.find_next_sibling()
            continue

        if (nextNode.name == 'h2'):
            nextNode = parent.find_next_sibling()
            element['media'] = {}
            counter = 0
            while True:
                if (nextNode.name == 'p'):
                    element['media']["p{}".format(counter)] = nextNode.get_text()
                    counter = counter+1
                elif (nextNode.name == 'h2'):
                    break
                nextNode = nextNode.find_next_sibling()
                continue

        else:
            li = nextNode.findAll('li')
            actives = {}
            for l in li:
                text = (l.get_text())
                if ':' in text:
                    category, other = text.split(':', 1)
                    actives[category.strip()] = other
            element['media'] = actives
        elements[element['name']] = element
    print(elements)


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

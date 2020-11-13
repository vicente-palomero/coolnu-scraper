#!/usr/bin/python
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
import csv
import sys, getopt
from bs4 import BeautifulSoup
from bs4 import re


wikipedia = 'https://es.wikipedia.org'

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
    result = {}
    openHRef(url, urls, result)

    print(result)
    # with open(outputfile, mode="w") as csv_file:
    #     writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     writer.writerow(['title', 'href'])
    #     for r in result:
    #         writer.writerow([r[0], r[1]])

def openHRef(url, urls, result):
    if (url in urls):
        return

    urls.append(url)

    bsObj = urlToBeautifulSoup(url)
    container = bsObj.find('div', {'id': 'mw-pages'})
    nextPage = container.find('a', {'href': re.compile("/w/.*#mw-pages")})
    anchors = container.findAll('a', {'href': re.compile("/wiki/.*")})

    for a in anchors:
        if a['title'] not in result:
            wikilink = '{}{}'.format(wikipedia, a['href'])
            bsWikilink = urlToBeautifulSoup(wikilink)
            wikidataUrl = bsWikilink.find('a', {'href': re.compile('https://www.wikidata.org/wiki/Q')})
            if (wikidataUrl is None):
                continue
            wikidataHref = wikidataUrl['href']
            bsWikidata = urlToBeautifulSoup(wikidataHref)

            data = getData(bsWikidata)

            qid = 'Q{}'.format(wikidataHref.split('Q')[1])
            result[a['title']] = {
                'qid': qid,
                'title': a['title'],
                'href': a['href'],
                'data': data
            }
            print(result[a['title']])

    if nextPage is not None:
        openHRef('https://es.wikipedia.org{}'.format(nextPage['href']), urls, result)

def getData(bs):
    statementHeader = bs.find(id = 'claims').parent
    divContainer = statementHeader.find_next_sibling()
    divData = divContainer.findAll('div', {'id': re.compile('P[0-9]*')})
    properties = {}
    for data in divData:
        aProperty = data.find('a', {'title': re.compile('Property:P[0-9]*')})
        propertyId = aProperty['title'].split(':')[1]
        propertyName = aProperty.get_text()
        if propertyName == 'logo image':
            aValue = data.findAll('img')
        else:
            aValue = data.findAll('a', {'title': re.compile('Q[0-9]*')})
        values = {}
        for a in aValue:
            if (a.name == 'img'):
                qValue = 'img'
                textValue = 'https:{}'.format(a['src'])
            else:
                qValue = a['title']
                textValue= a.get_text()
            values[qValue] = textValue

        properties[propertyId] = {}
        properties[propertyId]['label'] = propertyName
        properties[propertyId]['values'] = values

    return properties


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

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
        opts, args = getopt.getopt(argv, "hu:", ["url="])
    except getopt.GetoptError:
        print('scrap.py -u <url> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if (opt == '-h'):
            print('wikilists.py -u <url> -o <outputfile>')
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
        else:
            assert False, "unhandled option"

    urls = []
    result = {}
    openHRef(url, urls, result)

    print(result)

def openHRef(url, urls, result):
    if (url in urls):
        return

    urls.append(url)

    bsObj = urlToBeautifulSoup(url)
    container = bsObj.find('div', {'id': 'mw-pages'})
    nextPage = container.find('a', {'href': re.compile("/w/.*#mw-pages")})
    anchors = container.findAll('a', {'href': re.compile("/wiki/.*")})

    for a in anchors:
        if a.has_attr('title') and a['title'] not in result:
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
                'href': wikilink,
                'data': data
            }

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
        if 'image' in propertyName:
            aValue = [data.find('img')]
        else:
            aValue = data.findAll('div', {'class': 'wikibase-snakview-value wikibase-snakview-variation-valuesnak'})
        values = {}
        for a in aValue:
            if (a.name == 'img'):
                qValue = 'img'
                textValue = 'https:{}'.format(a['src'])
            else: # this is a div
                if len(a.find_all()) > 0:
                    innerDataTitle = a.find_all('a', {'title': re.compile('Q[0-9]*')})
                    for idata in innerDataTitle:
                        if 'ikipedia' in idata.get_text():
                            continue
                        qValue = idata['title']
                        textValue = idata.get_text()
                    innerDataLink = a.find_all('a', {'class': re.compile('external free')})
                    for idata in innerDataLink:
                        if 'ikipedia' in idata.get_text():
                            continue
                        qValue = 'link'
                        textValue = idata.get_text()
                else:
                    qValue = 'value'
                    textValue = a.get_text()
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

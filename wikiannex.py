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
        element['qid'] = ''
        element['title'] = name
        element['href'] = ''
        element['data'] = {}
        if (name == 'Referencias'):
            break
        parent = id.parent
        article = parent.find_next_sibling()
        if (article is not None and article.name == 'div'):
            articleHref = article.find('i').find('a')['href']
            wikilink = '{}{}'.format(wikipedia, articleHref)
            element['href'] = articleHref
            nextNode = parent.find_next_sibling()
        while True:
            if (nextNode.name == 'ul'):
                break
            elif (nextNode.name == 'h2'):
                break
            nextNode = nextNode.find_next_sibling()
            continue

        # if (nextNode.name == 'h2'):
        #     nextNode = parent.find_next_sibling()
        #     element['media'] = {}
        #     counter = 0
        #     while True:
        #         if (nextNode.name == 'p'):
        #             element['media']["p{}".format(counter)] = nextNode.get_text()
        #             counter = counter+1
        #         elif (nextNode.name == 'h2'):
        #             break
        #         nextNode = nextNode.find_next_sibling()
        #         continue

        # else:
        #     li = nextNode.findAll('li')
        #     actives = {}
        #     for l in li:
        #         text = (l.get_text())
        #         if ':' in text:
        #             category, other = text.split(':', 1)
        #             actives[category.strip()] = other
        #     element['media'] = actives

        href = element.get('href', False)
        if href:
            bsWikilink = urlToBeautifulSoup(wikilink)
            wikidataUrl = bsWikilink.find('a', {'href': re.compile('https://www.wikidata.org/wiki/Q')})
            if (wikidataUrl is None):
                continue
            wikidataHref = wikidataUrl['href']
            bsWikidata = urlToBeautifulSoup(wikidataHref)

            data = getData(bsWikidata)

            qid = 'Q{}'.format(wikidataHref.split('Q')[1])
            element['qid'] = qid
            element['data'] = data
        elements[element['title']] = element
    print(elements)

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

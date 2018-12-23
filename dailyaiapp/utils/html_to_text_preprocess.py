import feedparser
import json
import urllib2
import urllib
import nltk
import re
from bs4 import BeautifulSoup

USELESS_SENTENCES = [
    'Share this with', 'Email', 'Facebook', 'Messenger', 'Twitter', 'Pinterest', 'WhatsApp', 'LinkedIn',
    'Copy this link', 'These are external links and will open in a new window'
    ]


def get_content_from_link(link, pub_name):
    f = urllib.urlopen(link)
    response = f.read()
    soup = BeautifulSoup(response, 'html.parser')
    content_sents = []
    content_forbidden = []
    
    if pub_name == 'bbc':
        content_sents = get_text_from_bbc(soup)
    else:
        content_sents = get_text_by_tag(soup, 'p', content_sents)

    final_content_sents = [i for i in content_sents if isinstance(i, unicode)]

    return final_content_sents


def get_text_by_tag(a_soup, a_tag, a_content):
    for line in a_soup.find_all(a_tag):
        if len(line.contents) != 0:
            a_content.append(line.contents[0])
    return a_content


def get_text_from_bbc(soup):
    content_sents = []
    content_forbidden = []
    found_class_one = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['story-body'])
    if found_class_one != []:
        for line in found_class_one:
            for line_cont in line.find_all('a'):
                if len(line_cont.contents) != 0:
                    content_forbidden.append(line_cont.contents[0])

            for line_cont in line.find_all('h1'):
                if len(line_cont.contents) != 0 and line_cont.contents[0] not in content_forbidden:
                    for i in line_cont.contents:
                        content_sents.append(i)
            for line_cont in line.find_all('p'):
                if len(line_cont.contents) != 0 and line_cont.contents[0] not in content_forbidden:
                    for i in line_cont.contents:
                        if i.find('link-external') == -1:
                            content_sents.append(i)
                        elif len(i.contents) != 0:
                            content_sents.append(i.contents[0])
            
    found_class_two = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['vxp-media__body'])
    if found_class_two != []:
        for line in found_class_two:
            for line_cont in line.find_all('a'):
                if len(line_cont.contents) != 0:
                    content_forbidden.append(line_cont.contents[0])

            for line_cont in line.find_all('h1'):
                if len(line_cont.contents) != 0 and line_cont.contents[0] not in content_forbidden:
                    for i in line_cont.contents:
                        content_sents.append(i)
            for line_cont in line.find_all('p'):
                if len(line_cont.contents) != 0 and line_cont.contents[0] not in content_forbidden:
                    for i in line_cont.contents:
                        if i.find('link-external') == -1:
                            content_sents.append(i)
                        else:
                            content_sents.append(i.contents[0])

    found_class_three = soup.find_all(lambda tag: tag.name == 'div' and tag.get('id') == ['story-body'])
    if found_class_three != []:
        for line in found_class_three:
            for line_cont in line.find_all('a'):
                if len(line_cont.contents) != 0:
                    content_forbidden.append(line_cont.contents[0])

            for line_cont in line.find_all('h1'):
                if len(line_cont.contents) != 0 and line_cont.contents[0] not in content_forbidden:
                    for i in line_cont.contents:
                        content_sents.append(i)
            for line_cont in line.find_all('p'):
                if len(line_cont.contents) != 0 and line_cont.contents[0] not in content_forbidden:
                    for i in line_cont.contents:
                        if i.find('link-external') == -1:
                            content_sents.append(i)
                        else:
                            content_sents.append(i.contents[0])

    if len(content_sents) == 0:
        for line in soup.find_all('p'):
            if len(line.contents) != 0:
                content_sents.append(line.contents[0])
    for i in USELESS_SENTENCES:
        while content_sents.count(i) != 0:
            content_sents.remove(i)
    return content_sents

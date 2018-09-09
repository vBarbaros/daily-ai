from dailyaiapp import app

from flask import render_template
from flask import request

import feedparser
import json
import urllib2
import urllib
import nltk
from bs4 import BeautifulSoup


RSS_FEEDS = {
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'iol': 'http://www.iol.co.za/cmlink/1.640',
    'reuters': 'http://feeds.reuters.com/news/wealth',
    'marketwatch-top stories': 'http://www.marketwatch.com/rss/topstories'
    }

DEFAULTS = {
    'publication':'bbc', 'city': 'Montreal,CA',
    'currency_from': 'CAD', 'currency_to': 'USD'
    }

PUBLICATION_TO_SHOW = DEFAULTS['publication']

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=97cdbe13097f09f5a3334076e1d5eca4'
CURRENCY_URL = 'https://openexchangerates.org//api/latest.json?app_id=7c049d68cc6b4274970cca63852e1e99'


@app.route("/")
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    PUBLICATION_TO_SHOW = publication
    articles = get_news(publication)
    # get customized weather based on user input or default
    # city = request.args.get('city')
    # if not city:
    #     city = DEFAULTS['city']
    # weather = get_weather(city)

    # get customized currency based on user input or default
    # currency_from = request.args.get("currency_from")
    # if not currency_from:
    #     currency_from = DEFAULTS['currency_from']
    # currency_to = request.args.get("currency_to")
    # if not currency_to:
    #     currency_to = DEFAULTS['currency_to']
    # rate, currencies = get_rate(currency_from, currency_to)
    # return render_template(
    #     "home.html", publications=RSS_FEEDS.keys(), pub_display=publication.upper(),
    #     articles=articles, weather=weather, 
    #     currency_from=currency_from, currency_to=currency_to, 
    #     rate=rate, currencies=sorted(currencies)
    #     )
    return render_template(
        "home.html", publications=RSS_FEEDS.keys(), pub_display=publication,
        articles=articles
        )

@app.route("/articletext")
def article_text():
    article_link = request.args.get("article_link")
    title = request.args.get("title")
    article_content = get_content_from_link(article_link)
    return render_template(
        "article_text.html", 
        publication_to_show=PUBLICATION_TO_SHOW,
        title=title, 
        link=article_link, 
        article_content=article_content)

def get_content_from_link(link):
    f = urllib.urlopen(link)
    response = f.read()
    soup = BeautifulSoup(response, 'html.parser')
    content_sents = []
    for line in soup.find_all('p'):
        if len(line.contents) != 0:
            content_sents.append(line.contents[0])
    return content_sents

def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    for i in feed['entries']:
        try:    
            if i.summary and i.summary.find('<'):
                i.summary = i.summary[0: i.summary.find('<')]
        except AttributeError:
            pass
    return feed['entries']


def get_weather(query):
    query = urllib.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    
    if parsed.get('weather'):
        weather = {
        'description': parsed['weather'][0]['description'],
        'temperature': parsed['main']['temp'],
        'city': parsed['name'],
        'country': parsed['sys']['country']
        }
    return weather

def get_rate(frm, to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate, parsed.keys())



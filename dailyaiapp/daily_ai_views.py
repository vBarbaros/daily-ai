from dailyaiapp import app
from algs_nlp.sumbasic import SumBasicImplementation
from utils.html_to_text_preprocess import get_text_from_bbc, get_content_from_link

from flask import render_template
from flask import request

import feedparser
import json
import urllib2
import urllib
import nltk
import re
from bs4 import BeautifulSoup


RSS_FEEDS = {
    'bbc'                     : 'http://feeds.bbci.co.uk/news/rss.xml',
    # 'cnn'                     : 'http://rss.cnn.com/rss/edition.rss',
    # 'fox'                     : 'http://feeds.foxnews.com/foxnews/latest',
    # 'iol'                     : 'http://www.iol.co.za/cmlink/1.640',
    # 'reuters'                 : 'http://feeds.reuters.com/news/wealth',
    # 'marketwatch-top stories' : 'http://www.marketwatch.com/rss/topstories',
    'financial post'          : 'https://business.financialpost.com/feed/',
    # 'montreal gazette'        : 'http://feeds.feedburner.com/GazetteOnlineLocalNews',
    # 'la presse - actualite'   : 'https://www.lapresse.ca/rss/178.xml'
    }
    
DEFAULTS = {
    'publication':'bbc', 'city': 'Montreal,CA',
    'currency_from': 'CAD', 'currency_to': 'USD'
    }

PUBLICATION_TO_SHOW = DEFAULTS['publication']

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=97cdbe13097f09f5a3334076e1d5eca4'
CURRENCY_URL = 'https://openexchangerates.org//api/latest.json?app_id=7c049d68cc6b4274970cca63852e1e99'

SBI = SumBasicImplementation()

@app.route("/")
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    PUBLICATION_TO_SHOW = publication
    articles = get_news(publication)
    return render_template(
        "home.html", publications=RSS_FEEDS.keys(), pub_display=PUBLICATION_TO_SHOW,
        articles=articles
        )

@app.route("/articletext")
def article_text():
    article_link = request.args.get("article_link")
    title = request.args.get("title")
    PUBLICATION_TO_SHOW = request.args.get("pub_to_display")
    article_content = get_content_from_link(article_link, PUBLICATION_TO_SHOW)
    # print '>>>>: ', article_content
    
    article_content_new = SBI.main_web(article_content)

    return render_template(
        "article_text.html", 
        publication_to_show=PUBLICATION_TO_SHOW,
        title=title, 
        link=article_link,
        article_summary=article_content_new,
        article_content=article_content)

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
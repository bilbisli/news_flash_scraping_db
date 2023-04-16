from flask import Flask, redirect, render_template, request, url_for
import pymongo
from pymongo import MongoClient
import requests

from scraping import scrape_maariv, scrape_walla, scrape_ynet


app = Flask(__name__)
client = MongoClient("mongodb+srv://news_flash_user:nwPRrLePEgy8cv25@cluster0.jddwckk.mongodb.net/?retryWrites=true&w=majority")
db = client['app_db']
collection = db['news_flash']
# db.news_flash.create_index([('Title', pymongo.TEXT), ('Text', pymongo.TEXT)], name='newsflash_index', default_language='none', unique=True)

# define the scraping tools and websites as lists
scraping_tools = ['requests', 'BeautifulSoup', 'selenium']
websites = {'maariv': scrape_maariv, 'walla': scrape_walla, 'ynet': scrape_ynet}


def add_to_db(df):
    db.news_flash.insert_many(df.to_dict('records'))

@app.route('/')
def newsflash_page():
    news_flash = list(db.news_flash.find())
    fields = list(news_flash[1].keys())[1:] if news_flash else []
    date_fields = list(filter(lambda f: 'date'.casefold() in f.casefold(), fields))
    sort_by_field = date_fields[0] if date_fields else None
    return render_template('newsflash_page.html', websites=websites.keys(), news_flash=news_flash, fields=fields, sort_by_field=sort_by_field)

@app.route('/scrape', methods=['POST'])
def scrape():
    # get the selected scraping website from the form
    website = request.form.get('website')
    websites[website](add_to_db)
    
    return redirect(url_for('newsflash_page'))

if __name__ == '__main__':
    app.run(debug=True)

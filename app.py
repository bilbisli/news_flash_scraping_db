from flask import Flask, render_template, request
from pymongo import MongoClient

from scraping.scrape_maariv import scrape_maariv


app = Flask(__name__)
client = MongoClient("mongodb+srv://bilbisli:GoKAMYlEnwV5wC6G@cluster0.jddwckk.mongodb.net/?retryWrites=true&w=majority")
db = client['app_db']
collection = db['news_flash']

def add_to_db(df):
    db.news_flash.insert_many(df.to_dict('records'))

@app.route('/', methods=['GET', 'POST'])
def newsflash_page():
    if request.method == 'POST':
        scrape_maariv(add_to_db)
        return 'Data saved to MongoDB!'
    return render_template('newsflash_page.html')


if __name__ == '__main__':
    app.run(debug=True)

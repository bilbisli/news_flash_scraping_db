# Hebrew Newsflash Scraping and Saving in Remote Database
Scraping Israeli news web sites for newsflash


## Features
- Retrieving newsflash articles that are currently on [Maariv](https://www.maariv.co.il/breaking-news), [Walla](https://news.walla.co.il/breaking) and [Ynet](https://www.ynet.co.il/news/category/184)
- Saved newsflash display
- Search options (text, title, author, date and source)
- Filtering options (for each column)


## Installation
The project was developed in _python 3.10.6_ with _Selenium_, _BeautifulSoup4_ and requests for scraping

Open a shell and clone the repository (must have git installed previously):
```sh
git clone https://github.com/bilbisli/news_flash_scraping_db.git
```
or download the repository directly from the hub instead.

Change directory to the main directory:
```sh
cd news_flash_scraping_db
```

Create a virtual env:
```sh
python -m venv scraping_db_env
```

Activate virtual enviroment (windows):
```sh
scraping_db_env\Scripts\activate
```

Install the dependencies using the requirements.txt:
```sh
pip install -r requirements.txt
```
* Finally, add the 'web_scraping' module to **`PATH`**


## Usage
Launch the flask app (debug mode):
```sh
flask --app app.py --debug run
```
Retrieve newsflash from the desired website using the interface:
![alt text](https://github.com/bilbisli/news_flash_scraping_db/blob/main/newsflash_scraping.gif?raw=true)

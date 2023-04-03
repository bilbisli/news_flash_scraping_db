import requests
from bs4 import BeautifulSoup
# from selenium.webdriver.common.by import By
# from selenium import webdriver
import csv
import pandas as pd
import os
from os.path import exists
from datetime import date
from dateutil.parser import parse
from tqdm.auto import tqdm


def scrape_walla(add_to_db_func=None,):
    # creating the date object of today's date
    todays_date = date.today()
    # printing todays date
    print("Current date (last run): ", todays_date)

    BASE_URL = 'http://news.walla.co.il'
    url = requests.get(f'{BASE_URL}/breaking')

    soup = BeautifulSoup(url.text, 'html.parser')
    try:
        pages = soup.find("div", class_="breaking-pagination").find_all("a")
        pages = [page.text for page in pages]
        pages = list(filter(None, pages))   # get rid of empty strings
    except AttributeError as e:
        pages = [1]
    print('pages', pages)
    titles = []
    texts = []
    authors = []
    dates = []
    article_count = 0
    for page in tqdm(reversed(pages), desc='page', total=len(pages), disable=len(pages)==0):
        url = f'{BASE_URL}/breaking?page={page}'
        url = requests.get(url)
        content = BeautifulSoup(url.text, 'html.parser')
        content = content.find("ul", class_="breaking-list")
        left_sides = content.find_all('div', class_='left-side')
        article_urls = [f"{BASE_URL}{article.find('a').get('href')}" for article in left_sides]
        for article_url in tqdm(reversed(article_urls), desc='page articles', leave=False, total=len(article_urls), disable=len(article_urls)==0):
            article_url = requests.get(article_url)
            article_html = BeautifulSoup(article_url.text, 'html.parser')
            article_title = article_html.find("h1", class_="title")
            if not article_title:
                continue
            article_text = article_html.find("p", class_="article_speakable")
            if not article_text:
                continue
            try:
                article_date = parse(article_html.find('div', class_='date-part-1').text, fuzzy=True, dayfirst=True)   # get the proper date from the date text

            except Exception as e:
                print('date failed')
                article_date = ''
            try:
                article_time = article_html.find('div', class_='time').text
                article_date_time = f"{(str(article_date.strftime('%d/%m/%Y')) + ' ') if article_date else ''}{article_time if article_time else ''}"
            except Exception as e:
                article_date_time = article_date
            try:
                article_author = article_html.find("div", class_="author").text
            except Exception as e:
                article_author = ''
            titles.append(article_title.text)
            texts.append(article_text.text)
            authors.append(article_author)
            dates.append(article_date_time)
            article_count += 1


    print('total articles:', article_count)


    path = os.path.abspath(os.getcwd()) + '/WallaDataset.csv'

    dataset = pd.DataFrame({'Text':texts, 'Title':titles, 'Author': authors, 'Date': dates, 'Source': ['walla']*len(titles)})
    dataset.set_index('Text')
    if os.path.exists(path):
        old_data = pd.read_csv(path)
        old_data.set_index('Text')
        dataset = old_data.append(dataset, ignore_index=True)
        # dups = dataset.duplicated(subset=['Text', 'Label'], keep='last')
        # display(dups[dups==True])
        dups = dataset.duplicated(subset=['Text', 'Title'], keep='first')
        print('new added:', article_count - len(dups[dups==True]))
        dataset = dataset.drop_duplicates(subset=['Text', 'Title'], keep='last', ignore_index=True)
    
    if add_to_db_func is None:
            dataset.to_csv(path, index=False, encoding='utf-8-sig')
    else:
        add_to_db_func(dataset)

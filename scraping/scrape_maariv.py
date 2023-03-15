import requests
from bs4 import BeautifulSoup
# from selenium.webdriver.common.by import By
import csv
import pandas as pd
import os
from os.path import exists
from tqdm.auto import tqdm
from datetime import date


MONTHS_IN_YEAR = 12

def scrape_maariv(add_to_db_func=None, save_every=5000, save_during_run=True, stop_at_page=20):
    # creating the date object of today's date
    todays_date = date.today()
    
    # printing todays date
    print("Current date: ", todays_date)

    start_year = todays_date.year       # default is current year (earliest in archive is 2013)
    stop_at_year = None                 # default is None for maximum year
    start_month = todays_date.month     # default is current month
    stop_at_month = None                # default is None for maximum month
                       # default is None for maximum page (pages are loaded in descending order)

    BASE_URL = 'http://www.maariv.co.il'
    path = os.path.join(os.path.abspath(os.getcwd()), 'MaarivDataset.csv')

    titles = []
    descriptions = []
    authors = []
    dates = []

    article_count = 0
    prev_count = 0
    a_date = ''


    if stop_at_year or start_year != 2013:
        print(f'Loading years: {start_year}-{stop_at_year}')
    if stop_at_month or start_month != 1:
        print(f'Loading months: {start_month}-{stop_at_month}')
    if stop_at_page:
        print(f'Loading pages: {stop_at_page}-{1} (descending)')

    year_bar = tqdm(range(start_year, (stop_at_year if stop_at_year else todays_date.year) + 1))
    for year in year_bar:
        year_bar.set_description(f'year {year}')

        end_month = (stop_at_month if stop_at_month else todays_date.month if year == todays_date.year else MONTHS_IN_YEAR) + 1
        month_bar = tqdm(range(start_month, end_month), leave=False)
        for month in month_bar:
            month_bar.set_description(f'month {month}')
            if not stop_at_page:
                url = f'{BASE_URL}/ArticleArchive/Category/2/year/{year}/month/{month}/page/1'
                url = requests.get(url)
                soup = BeautifulSoup(url.text, 'html.parser')
                pages = soup.find_all("a", class_="page-link")
                if pages:   # get rid of 'prev' and 'next' button pages
                    pages = pages[1:-1]
            else:
                pages = range(1, stop_at_page + 1)
            for page in tqdm(reversed(pages), desc='page', leave=False, total=len(pages), disable=len(pages)==0):
                if not stop_at_page:
                    page = int(page.text.strip())
                page_url = f'{BASE_URL}/ArticleArchive/Category/2/year/{year}/month/{month}/page/{page}'
                # print(page)
                page_url = requests.get(page_url)
                soup = BeautifulSoup(page_url.text, 'html.parser')
                articles = soup.find_all("div", class_="three-articles-in-row")
                for article_url in tqdm(reversed(articles), desc='page articles', leave=False, total=len(articles), disable=len(articles)==0):
                    try:
                        reporter_date = article_url.find('div', class_='three-articles-in-row-reporter-and-date').findAll('span')
                        reporter = reporter_date[0].text
                        a_date = reporter_date[1].text
                    except Exception as e:
                        print(e)
                        print('date/author read failed')
                        a_date = f'{month}/{year}'
                        reporter = ''
                    article_url = article_url.find('a', recursive=False).get('href')
                    if article_url and BASE_URL not in article_url and BASE_URL.replace('http', 'https') not in article_url:
                        article_url = BASE_URL + article_url
                    # print('\t\t', article_url)
                    try:
                        article_url = requests.get(article_url)
                        soup = BeautifulSoup(article_url.text, 'html.parser')
                        
                        title = soup.find('div', class_='article-title').text
                        if not title:
                            continue
                        titles.append(title)
                        description = soup.find('div', class_='article-description').text
                        if not description:
                            titles.pop()
                            continue
                        descriptions.append(description)
                        article_count += 1
                        dates.append(a_date)
                        authors.append(reporter)
                        # print(a_date)

                        if save_during_run and article_count % save_every == 0:
                            dataset = pd.DataFrame({'Text': descriptions, 'Title': titles, 'Author': authors, 'Date': dates})
                            dataset.set_index('Text')
                            if os.path.exists(path):
                                old_data = pd.read_csv(path)
                                dataset = old_data.append(dataset, ignore_index=True)
                                dataset.set_index('Text')
                                dataset = dataset.drop_duplicates(subset=['Text', 'Title'], keep='last', ignore_index=True)
                            if add_to_db_func is None:
                                dataset.to_csv(path, index=False, encoding='utf-8-sig')
                            else:
                                add_to_db_func(dataset)
                            titles = []
                            descriptions = []
                            authors = []
                            dates = []
                            print('saved until:', a_date)
                    except Exception as e:
                        print(e)
                        print('article date:', a_date)
            if article_count != prev_count:
                print('\t\tArticles so far:', article_count)
            prev_count = article_count
    print('Total Articles:', article_count)
    if not save_during_run or article_count % save_every != 0:
        dataset = pd.DataFrame({'Text': descriptions, 'Title': titles, 'Author': authors, 'Date': dates})
        dataset.set_index('Text')
        if os.path.exists(path):
            old_data = pd.read_csv(path)
            dataset = old_data.append(dataset, ignore_index=True)
            dataset.set_index('Text')
            dups = dataset.duplicated(subset=['Text', 'Title'], keep='first')
            print('new added:', article_count - len(dups[dups==True]))
            dataset = dataset.drop_duplicates(subset=['Text', 'Title'], keep='last', ignore_index=True)
        if add_to_db_func is None:
            dataset.to_csv(path, index=False, encoding='utf-8-sig')
        else:
            add_to_db_func(dataset)
        

if __name__ == '__main__':
    scrape_maariv()


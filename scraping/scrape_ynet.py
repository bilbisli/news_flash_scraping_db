import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from datetime import datetime, timedelta


def get_text_in_last_brackets(text):
    author_re = r"(?<=\()[^\(\)]*(?=\)|\Z)"
    matches = re.findall(author_re, text)
    if matches:
        return matches[-1]
    else:
        return ''

def scrape_ynet(add_to_db_func=None):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
    # creating the date object of today's date
    todays_date = datetime.today()
    # printing todays date
    print("Current date (last run): ", todays_date)

    url = 'https://www.ynet.co.il/news/category/184'
    driver.get(url)

    python_button = driver.find_element("xpath", "(//div[@class='blackCircleInput'])[1]")
    driver.execute_script("arguments[0].click();", python_button)
    soup = BeautifulSoup(driver.page_source, "html")
    driver.close()
    titles = soup.find_all("div", class_="title")
    titles = list(map(lambda x: x.text, titles))
    texts = soup.find_all("div", class_="itemBody")
    texts = list(map(lambda x: x.text, texts))
    times = list(map(lambda x: x.text, soup.find_all('span', class_='DateDisplay')))
    dates = [f"{(todays_date - timedelta(days=1)  if 'אתמול' in article_time else todays_date).strftime('%d/%m/%Y')} {article_time.replace('אתמול | ', '')}" for article_time in times]
    authors = [get_text_in_last_brackets(text) or '' for text in texts]
    
    print(len(texts), len(titles), len(authors), len(dates))
    dataset = pd.DataFrame({'Text': texts, 'Title': titles, 'Author': authors, 'Date': dates, 'Source': ['ynet']*len(titles)})
    dataset.set_index('Text')
    path = os.path.abspath(os.getcwd()) + '/WallaDataset.csv'
    if os.path.exists(path):
        old_data = pd.read_csv(path)
        old_data.set_index('Text')
        old_data = old_data.append(dataset, ignore_index=True)
        dups = old_data.duplicated(subset=['Text', 'Label'], keep='first')
        print('new added:', len(texts) - len(dups[dups==True]))
        old_data = old_data.drop_duplicates(subset=['Text', 'Label'], keep='first', ignore_index=True)
        dataset = old_data

    if add_to_db_func is None:
            dataset.to_csv(path, index=False, encoding='utf-8-sig')
    else:
        add_to_db_func(dataset)

    print('total articles:', len(texts))

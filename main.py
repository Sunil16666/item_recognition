#! /usr/bin/python3

import csv
import os
import numpy
from selenium import webdriver
from bs4 import BeautifulSoup
import re
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

ELEMENT_TO_SEARCH = input("enter element to search for: ")
PATH_TO_CHROME_EXTENSION = r'/Users/linushenn/Library/Application Support/Google/Chrome/Default/Extensions/cjpalhdlnbpafiamejdnhcphjbkeiagm'
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument('load extension=' + PATH_TO_CHROME_EXTENSION)
URL_TO_SCAN = f"https://www.ebay-kleinanzeigen.de/s-muenster-%28westfalen%29/{ELEMENT_TO_SEARCH}/k0l929"
driver = webdriver.Chrome(executable_path='/Users/linushenn/Desktop/Chromedriver/chromedriver', options=chrome_options)


def interceptor(request):
    request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, ' \
                                    'like Gecko) Chrome/105.0.0.0 Safari/537.36 '


driver.request_interceptor = interceptor


def handling_items_csv():
    user_input = input("Do you want do keep items.csv? (y) for YES and (n) for NO: ")
    while True:
        if user_input == 'n':
            os.remove("items.csv")
            break
        elif user_input == 'y':
            break
        else:
            print('wrong input')


def scanning():
    products = []
    locations = []
    prices = []

    driver.get(URL_TO_SCAN)

    content = driver.page_source

    soup = BeautifulSoup(content, 'html.parser')
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, 'gdpr-banner-accept')))
    driver.find_element(By.ID, 'gdpr-banner-accept').click()

    def get_element():
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'aditem')))
        for a in soup.find_all('article', attrs={'class': 'aditem'}):
            price = a.find('p', attrs={
                'class': 'aditem-main--middle--price' and 'aditem-main--middle--price-shipping--price'})
            product = a.find('a', attrs={'class': 'ellipsis'})
            location = a.find('div', attrs={'class': 'aditem-main--top--left'})
            # fix: checking if price exists
            products.append(re.sub(r"\([^)]*\)", '', str(product.text).replace(" ", "")))
            if len(driver.find_elements(By.CSS_SELECTOR, '#srchrslt-adtable > li:nth-child(1) > article > div.aditem-main > div.aditem-main--middle > div.aditem-main--middle--price-shipping > p')) != 0:
                prices.append(str(price.text).replace("  ", "").replace('\n', ''))
            else:
                prices.append('n/a')
            locations.append(str(location.text).replace(" ", "").replace('\n', ''))
            try:
                if driver.find_elements(By.CSS_SELECTOR, '#srchrslt-pagination > div > div.pagination-nav > a'):
                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, 'pagination-next'))).click()
                else:
                    pass
            except NoSuchElementException and TimeoutException:
                pass

    get_element()
    while driver.find_elements(By.CSS_SELECTOR, '#srchrslt-pagination > div > div.pagination-nav > a') != 0:
        get_element()
    else:
        driver.close()
    print(products)
    print(prices)
    print(locations)

    with open('items.csv', 'w', newline='') as item_storing:
        writer = csv.writer(item_storing, quoting=csv.QUOTE_ALL)
        writer.writerow(products)
        writer.writerow(prices)
        writer.writerow(locations)

    'make proper sorting based on the price'
    # numpy.sort(products, axis=-1, kind='quicksort')


scanning()
handling_items_csv()

# Web search for news items with user defined keywords at http://rg.ru
# extracting the urls and loading them to DB

from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
import time
import math
import sqlite3

# build search_url by concatenating user keywords
keywords = input("Enter keywords to search www.rg.ru: ")
key_dic = keywords.split(' ')
#search_url_start = "https://rg.ru/search/?keywords="
search_url_start = "https://rg.ru/search/?keywords="
for i in key_dic:
    search_url_start += i
    search_url_start += '%20'
search_url = search_url_start[:-3]
print(search_url)

# create webdriver object
driver = webdriver.Chrome('C:/Users/Dmitry/Desktop/Chromedriver/chromedriver.exe')
# get rg.ru's search results page with the limited list of urls
driver.get(search_url)
# wait till the page is loaded
time.sleep(7)


# retrive page's html
# find how many search results for given keywords are there
# get rid of " найдено" in the retrieved result
search_results = driver.page_source
soup_search = BeautifulSoup(search_results, 'html.parser',
                parse_only=SoupStrainer('div',
                    class_='b-search-info__meta'))
items = soup_search.get_text()
items_found = int(items[:-8])
print("Items found:", items_found)
clicks_needed = math.floor(items_found / 20)

# find the element to load more search results in the page decode
# the element wasn't clickable and the following line solved the problem
# thanks to this source: https://stackoverflow.com/questions/48665001/
#can-not-click-on-a-element-elementclickinterceptedexception-in-splinter-selen
# wait till the loop of clicks above loads the search page
# may need several seconds to complete loading
if items_found > 20:
    print(f"To get the full results, it will take {clicks_needed} iterations")
    input("Press enter to proceed or ctrl+c to exit: ")
    for i in range(clicks_needed): # adjust the range to get larger search results
        element = driver.find_element_by_xpath(
                        '//*[@id="searchResults"]/div[2]/span')
        driver.execute_script("arguments[0].click();", element)
if clicks_needed < 5:
    print("The programm is paused for 5 seconds to load the search results!")
    time.sleep(5)
else:
    print("The programm is paused for 10 seconds to load the search results!")
    time.sleep(10)


# extracting urls in the html format to soup_get
html = driver.page_source
soup_get = BeautifulSoup(html, 'html.parser',
        parse_only=SoupStrainer('h2',
                class_="b-news-inner__list-item-title"))
items_retrieved = len(soup_get)
print("Items retrieved:", items_retrieved)
driver.close()


# load urls and keywords to the database
conn = sqlite3.connect('climate_news.sqlite')
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS urls")
cur.execute('''CREATE TABLE IF NOT EXISTS urls
            (id INTEGER PRIMARY KEY
            , address TEXT UNIQUE
            , keywords TEXT)''')
for i in soup_get.find_all('a'):
    address = 'https://rg.ru/' + str(i['href'])
    print(address)
    cur.execute('''INSERT OR IGNORE INTO urls
                (address, keywords) VALUES (?,?)''', (address, keywords))
conn.commit()
cur.close()

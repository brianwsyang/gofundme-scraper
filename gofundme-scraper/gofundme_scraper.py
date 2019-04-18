# -*- coding: utf-8 -*-
"""
@author: brianwsyang
@date: Wed Apr 17 2019
@reference: https://github.com/lmeninato/GoFundMe
"""
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from time import sleep
import numpy as np
import pandas as pd
import requests
import re

# Santa Rosa Fire
# url = 'https://www.gofundme.com/mvc.php?route=homepage_norma/search&term=santa%20rosa%20fire'

# Paradise Fire
url = 'https://www.gofundme.com/mvc.php?route=homepage_norma/search&term=paradise%20fire'

driver = webdriver.Chrome('/Users/goomibear/Desktop/chromedriver')
driver.get(url)

show_more = True
for i in range(5):
    for elem in driver.find_elements_by_link_text('Show More'):
            try:
                elem.click()
                print("Successful click")
            except:
                show_more = False
            sleep(0.8)
source = driver.page_source
driver.close()

soup = bs(source, 'lxml')

urls = []
fundraisers = soup.findAll("a", {"class": "campaign-tile-img--contain js-lazy"})
for f in fundraisers:
    urls.append(f.attrs['href'])

def scrape_url(row_index):
    single_row = mydf.iloc[row_index]
    url = urls[row_index]
    
    page = requests.get(url)
         
    soup = bs(page.text, 'lxml')
    try:
        container = soup.find_all("div",{"class":"layer-white hide-for-large mb10"})
        info_string = container[0].text
        info_string = info_string.splitlines()
        info_string = list(filter(None, info_string))
        
        amount_raised = int(info_string[0][1:].replace(',',''))
        
        goal = re.findall('\$(.*?) goal', info_string[1])[0]
        
        NumDonators = re.findall('by (.*?) people', info_string[2])[0]
        
        timeFundraised = re.findall("in (.*)$", info_string[2])[0]
    except:
        amount_raised = np.nan
        goal = np.nan
        NumDonators = np.nan
        timeFundraised = np.nan
    
    #<h1 class="campaign-title">Help Rick Muchow Beat Cancer</h1>
    title_container = soup.find_all("h1",{"class":"campaign-title"})
    
    try:
        title = title_container[0].text
    except:
        title = np.nan
    
    text_container =  soup.find('meta', attrs={'name': 'description'})
    
    try:
        all_text = text_container['content']
    except:
        all_text = np.nan
    
    try:
        FB_shares_container = soup.find_all("strong", {"class":"js-share-count-text"})
        FB_shares = FB_shares_container[0].text.splitlines()
        FB_shares = FB_shares[1].replace(" ", "").replace("\xa0", "")
    except:
        FB_shares = np.nan
        
    try:
        hearts_container = soup.find_all("div", {"class":"campaign-sp campaign-sp--heart fave-num"})
        hearts = hearts_container[0].text
    except:
        hearts = np.nan
    
    try:
        location_container = soup.find_all("div", {"class":"pills-contain"})
        location = location_container[0].text.splitlines()[-1]
        location = location.replace('\xa0', '').strip()
    except:
        location = np.nan
        
    temp_row = np.array([[url, title, location, amount_raised, goal, 
                          NumDonators, timeFundraised, FB_shares, hearts, all_text]])
    temp_df = pd.DataFrame(temp_row, columns = headers)
    
    return(temp_df)


headers = ["Url", "Title", "Location", "Amount_Raised", "Goal", 
           "Number_of_Donors", "Length_of_Fundraising", "FB_Shares", "GFM_hearts", "Text"]

mydf = pd.DataFrame(index=np.arange(len(urls)), columns=headers)

for i in range(len(urls)):
    mydf.loc[i] = scrape_url(i).loc[0]



mydf.to_excel("gfm_output.xlsx")


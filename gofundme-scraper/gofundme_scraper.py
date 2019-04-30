#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-
"""
@author: brianwsyang
@date: Mon Apr 29 2019
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
# if show_more:
for i in range(3):
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


# In[2]:


def extract_value_embedded_arr(array):
    for a in array:
        if not len(a) == 0:
            return a[0]
    return None


# In[3]:


def scrape_url(row_index):
    single_row = mydf.iloc[row_index]
    url = urls[row_index]
    
    page = requests.get(url)
         
    soup = bs(page.text, 'lxml')
    try:
        container = soup.find_all("div",{"class":"layer-white hide-for-large mb10"})
        info = container[0].text.splitlines()
        info = list(filter(None, info))
        
        num_donors = extract_value_embedded_arr([re.findall('by ([\d]*) people', i) for i in info])
        timeFundraised = extract_value_embedded_arr([re.findall('\D ([\d]*) months', i) for i in info])
    except:
        num_donors = np.nan
        timeFundraised = np.nan
    
    try:
        container = soup.find_all("h2",{"class":"goal"})
        money = container[0].text.splitlines()
        money = list(filter(None, money))
        if len(money) == 2:
            amt_raised = money[0]
            goal = re.findall('(.[\d|,]*) goal', money[1])[0]
        elif len(money) == 1:
            amt_raised = np.nan
            goal = re.findall('(.[\d|,]*) goal', money[0])[0]
    except:
        amt_raised = np.nan
        goal = np.nan
    
    try:
        title_container = soup.find_all("h1", {"class":"campaign-title"})
        title = title_container[0].text
    except:
        title = np.nan
    
    try:
        text_container =  soup.find('meta', attrs={'name': 'description'})
        all_text = text_container['content']
    except:
        all_text = np.nan
    
    try:
        container = soup.find_all("strong", {"class":"js-share-count-text"})
        fb_shares = container[0].text.splitlines()
        fb_shares = fb_shares[1].replace(" ", "").replace("\xa0", "")
    except:
        fb_shares = np.nan
        
    try:
        container = soup.find_all("div", {"class":"campaign-sp campaign-sp--heart fave-num"})
        hearts = container[0].text
    except:
        hearts = np.nan
    
    try:
        container = soup.find_all("div", {"class":"pills-contain"})
        loc = container[0].text.splitlines()
        loc = loc[-1].replace('\xa0', '').strip()
    except:
        loc = np.nan
    
    temp_row = np.array([[url, title, loc, amt_raised, goal, 
                          num_donors, timeFundraised, fb_shares, hearts, all_text]])
    temp_df = pd.DataFrame(temp_row, columns = headers)
    
    return(temp_df)


# In[4]:


headers = ["Url", "Title", "Location", "Amount_Raised", "Goal", 
           "Number_of_Donors", "Length_of_Fundraising", "fb_Shares", "GFM_hearts", "Text"]

mydf = pd.DataFrame(index=np.arange(len(urls)), columns=headers)

for i in range(len(urls)):
    mydf.loc[i] = scrape_url(i).loc[0]


# In[5]:


mydf.to_excel("gfm_output.xlsx")


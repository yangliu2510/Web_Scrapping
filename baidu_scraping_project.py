#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 08:43:12 2017

@author: liuyang
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 05:06:56 2017

@author: liuyang
"""

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import json
import re
import pandas as pd
import time
import string
import multiprocessing

def get_shop_category_list():
    #start from an inital webpage
    driver = webdriver.Chrome('/Applications/chromedriver')
    #driver = webdriver.PhantomJS()
    driver.get('http://waimai.baidu.com/waimai/shoplist/53fbb7b5c32e8b81')
    driver.implicitly_wait(5)
    
    #get category list
    data =driver.page_source
    soup = BeautifulSoup(data, 'lxml')
    category = soup.find_all('div', class_='item-text')
    cat_list = []
    for i in category:
        cat_list.append(i.text)
    driver.quit()
    return cat_list


def get_station_shop_list(station, cat_list):

    cat_shop_list = {}
    driver = webdriver.Chrome('/Applications/chromedriver')
    #driver = webdriver.PhantomJS()
    driver.get('http://waimai.baidu.com/waimai/shoplist/53fbb7b5c32e8b81')
    driver.implicitly_wait(5)
    
    #input and search for subway stations
    driver.find_element_by_class_name('s-con').click()
    driver.find_element_by_id('s-con').send_keys(station + u'地铁站')
    time.sleep(8)
    driver.find_element_by_tag_name('li').click()
    time.sleep(3)
    driver.find_element_by_tag_name('li').click()
    time.sleep(3)

    for cat_index in xrange(1): ###13 test change
        #click shop categories
        css = "li[data-name=\"" + cat_list[cat_index] + "\"]"
        driver.find_element_by_css_selector(css).click()
        time.sleep(3)
        
        #scroll down to load more shops
        n_page = 2 ###change for test
        for n in xrange(n_page):
            driver.execute_script("window.scrollBy(0,600000)")
            time.sleep(5)
    
        #get page source
        data = driver.page_source
        soup = BeautifulSoup(data, 'lxml')
        
        #back to page top
        driver.execute_script("window.scrollTo(0,0)")  
        time.sleep(10)
    
        #get shop list
        shop_list = get_shop_list(soup)
        cate_name = cat_list[cat_index]
        cat_shop_list[cate_name] = shop_list
        
        time.sleep(15)
    
    driver.quit()
    return cat_shop_list

def get_shop_list(soup):
   
    shop_list = []
    rank = 1
    for shop in soup.find('ul', class_="shopcards-list").find_all('li'):
        poiid = re.compile(r'data="([0-9]*?)"', re.DOTALL).findall(str(shop))
        name = shop.find('div', class_='title')['title']
        star_score = shop.find('div', class_='f-col f-star star-control')['data-star']
        monthly_sale = shop.find('div', class_='f-col f-sale').text.strip()
        deliver_price = shop.find('div', class_='f-col f-price').find('span', class_='item-value').text.strip()
        deliver_fee = shop.find('div', class_='f-col f-cost').find('span', class_='item-value').text.strip()
        deliver_time = shop.find('div', class_='f-col f-time').text.strip()
        #shop_url = 'https://waimai.baidu.com/waimai/shop/' + poiid[0]
        if u'小时' not in deliver_time:
            shop_list.append([rank, poiid, name, star_score, monthly_sale,
                             deliver_price, deliver_fee, deliver_time])
        rank = rank + 1

    return shop_list

def record_shop_list(station, cat_list):
    cat_shop_list = get_station_shop_list(station, cat_list)
    file_addr = "/Users/liuyang/Desktop/RA" + station + ".txt" 
    with open(file_addr, "wb") as f:
        json.dump(cat_shop_list, f)
        f.close()

def get_station_list():
    driver = webdriver.Chrome('/Applications/chromedriver')
    #driver = webdriver.PhantomJS()
    driver.get('http://www.bjsubway.com/station/xltcx/')
    data = driver.page_source
    soup = BeautifulSoup(data, 'lxml')
    station_raw_list = soup.find_all("div", class_="station")
    driver.quit()
    
    station_list = []
    
    for i in station_raw_list:
        station_list.append(i.text)
        
    station_list = list[set(station_list)]
    return station_list

#def get_all_shop_list(station_list):
        
    #station_list = get_station_list()
    #cat_list = get_shop_category_list()
    
    #pool = multiprocessing.Pool(multiprocessing.cpu_count())
    #for station in station_list:
    #    pool.apply(record_shop_list, (station, cat_list, ))
        
    #    pool.close()
    #    pool.join()


#get_all_shop_list(station_list[49:])
cat_list = get_shop_category_list()
station = u'昌平西山口'
cat_shop_list = get_station_shop_list(station, cat_list)
record_shop_list(station,cat_list)


#for station in station_list[61:]:
#    record_shop_list(station, cat_list)
#    time.sleep(120)
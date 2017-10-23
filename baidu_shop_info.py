# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
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
import random
import numpy as np
import pandas as pd
import csv

def get_all_shop_info(shop_id_all_list, chunk_num):
    
    shop_id_chunk_list = np.array_split(shop_id_all_list, chunk_num)
    print shop_id_chunk_list
    
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    for i in xrange(len(shop_id_chunk_list)):
        shop_id_list = shop_id_chunk_list[i]
        pool.apply_async(record_shop_info, (shop_id_list, i, ))
        #pool.close()
        #pool.join()

def record_shop_info(shop_id_list, num):
    
    shop_info_list = []
    
    for shop_id in shop_id_list:
		try：
			shop_info = get_shop_info(shop_id)
			shop_info_list.append(shop_info)
			file_addr = '/Users/liuyang/Desktop/RA/testing_data/'+ str(num) + '.txt' ###save path
			abnormal_shop = '/Users/liuyang/Desktop/RA/testing_data/abnormal_shop.csv'
			with open(file_addr, "wb") as f:
				json.dump(shop_info_list, f)
				f.close()
		except:
			with open(abnormal_shop, 'ab') as f:
				writer = csv.writer(f)
				writer.writerow(shop_id)
				f.close()




def get_shop_info(shop_id):
    
    shop_url = 'https://waimai.baidu.com/waimai/shop/' + shop_id
    
    #get shop page source
    driver2 = webdriver.Chrome('/Applications/chromedriver') ###need to download chromedriver
    #print 'opened!'
    #driver2 = webdriver.PhantomJS()
    driver2.get(shop_url)
    driver2.implicitly_wait(10)
    shop_soup = BeautifulSoup(driver2.page_source, 'lxml')
    driver2.quit()
    
    #get shop basic information
    shop_name = shop_soup.find('div', class_="one-line").find('h2').text
    shop_address = shop_soup.find_all('dd')[2].text.strip()
    shop_detail_score = get_detail_score(shop_soup)    
    
    #get shop price information
    dish_info_list = get_dish_info(shop_soup)
    average_price = get_average_price(dish_info_list)
    
    shop_info = [shop_id, shop_name, shop_address, shop_detail_score, dish_info_list, average_price]
    return shop_info


def get_detail_score(shop_soup):
    score_table = shop_soup.find('table', class_="rate-table")
    score_list = re.compile(r'<td>([0-9]*)\xe4\xba\xba</td>', re.DOTALL).findall(str(score_table))
    return score_list
    

def get_dish_info(shop_soup):

    dish_info_list = []
    for dish in shop_soup.find_all('li', class_='list-item'):
        dish_name = dish.find('h3')['data-title']
        dish_price = dish.find('strong').text
        dish_sales = dish.find_all('span', class_='sales-count')[1].text
        dish_recommend = dish.find_all('span', class_='sales-count')[0].text
        dish_info_list.append([dish_name, dish_price, dish_sales, dish_recommend])
        
    return dish_info_list

def get_average_price(dish_info_list):
    dish_df = pd.DataFrame(dish_info_list)
    dish_df['unit_price'] = dish_df[1].apply(lambda x: float(re.findall(r"\d+\.?\d*",x)[0]))
    dish_df['sales'] = dish_df[2].apply(lambda x: float(re.findall(r"\d+\.?\d*",x)[0]))
    dish_df['profit'] = dish_df['unit_price']*dish_df['sales']
    dish_price_df = dish_df.sort_values(['sales'],ascending=False) 
    dish_price = sum(dish_price_df['profit'])/sum(dish_price_df['sales'])
    return dish_price




shop_id_all_list = ['2018036774', '1874138249', '1438077964', '2015655825',
                     '1476706394', '1699319117', '1875481172', '1810035098']

if __name__ == '__main__':
    get_all_shop_info(shop_id_all_list, 5)
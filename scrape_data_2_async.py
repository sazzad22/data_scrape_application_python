import asyncio
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import os
import requests
from bs4 import BeautifulSoup



async def scrape_product_links():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
        
    driver.get("https://www.daraz.com.bd/#")
    
    # slow scroll
    SCROLL_PAUSE_TIME = 0.5
    
    
    
    
    # scroll
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        # scroll to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # wait to load page
        await asyncio.sleep(SCROLL_PAUSE_TIME)
        # calc new scroll height and compare with the last scroll height. if there is no more content loaded then they would be same and loop breaks
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # wait for page to load
   
    
    # get all product links
    # now that all products have loaded, you can extract the data you need
    product_a_tags = driver.find_elements(By.CLASS_NAME, "card-jfy-li-content")
    
    links = []
    for product_a_tag in product_a_tags:
        links.append(product_a_tag.get_attribute('href'))
    
    
    # close driver and return links
    driver.quit()
    
    return links


async def scrape_product(link,driver):

    info_dict = {}
    info_dict['link'] = link
    try:
        # Get the current window handle
        current_window = driver.current_window_handle
        
        # Open the product link in a new tab
        driver.execute_script("window.open('{}', '_blank');".format(link))
        
        # Switch to the new tab
        for window_handle in driver.window_handles:
            if window_handle != current_window:
                driver.switch_to.window(window_handle)
                break
        await asyncio.sleep(3)
        
        try:
            element_present = EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div[3]/div[2]/div/div[1]/div[3]/div/div/span'))
            WebDriverWait(driver, 5).until(element_present)
        except TimeoutException:
            print("Timed out waiting for product page to load")
            
        html = driver.page_source 
        # return the driver.page_source
        print(type(html))
        print(html)
        return html
    except Exception as e:
        print(e)


def save_info_to_json(product_infos):
    with open("async_product_info.json", "w") as f:
        json.dump(product_infos, f)

async def main():
    links = await scrape_product_links()
    
    # set up the driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    # scrape product concurrently
    tasks = []
    for link in links[:2]:
        tasks.append(asyncio.create_task(scrape_product(link,driver)))
    
    # wait for all tasks to complete
    products_html_list: list = await asyncio.gather(*tasks)
    
    product_infos = []
    product_info = {}
    for i,product_html in enumerate(products_html_list):
        print(product_html)
        product_info = {}
        product_info["link"]=links[i]
        soup = BeautifulSoup(product_html, 'lxml')
        product_info['title'] = soup.find("span",class_="pdp-mod-product-badge-title")
        product_infos.append(product_info)
    
    
    
    # save info to JSON 
    save_info_to_json(product_infos)
    
    

if __name__ == "__main__":
    asyncio.run(main())
    
    
        
        
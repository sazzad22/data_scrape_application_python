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

from pyppeteer import launch

async def scrape_product(link,browser):
    print(' page')
    
    page = await browser.newPage()
    print('created page')

    # navigate to the dynamic website and scroll to the bottom
    await page.goto(link)
    print('goto link')
    

    # extract products info
    
    # close browser and return links
    await browser.close()
    print('browser closed')
    
    return {link}

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

def save_info_to_json(product_infos):
    with open("async_product_info.json", "w") as f:
        json.dump(product_infos, f)

async def main():
    links = await scrape_product_links()
    
    # set up the driver
    # options = webdriver.ChromeOptions()
    # options.add_argument("--start-maximized")
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    # set up chromium driver
    try:
        browser = await launch()
        print('browser created')
    except Exception as e:
        print(e)
    
    
    # scrape product concurrently
    tasks = []
    for link in links[:3]:
        tasks.append(asyncio.create_task(scrape_product(link,browser)))
    
    # wait for all tasks to complete
    product_infos = await asyncio.gather(*tasks)
    
    
    
    # save info to JSON 
    save_info_to_json(product_infos)
    
    

if __name__ == "__main__":
    asyncio.run(main())
    
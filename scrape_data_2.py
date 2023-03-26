import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from webdriver_manager.chrome import ChromeDriverManager
from multiprocessing import Pool
import asyncio
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidSessionIdException
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import requests
import traceback
import re


def scrape_product(link, src_link):
    
    info_dict = {}
    info_dict['link'] = link
    
    # set up the driver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    
    try:
        # open the link in new tab
        driver.get(link)
        # driver.execute_script("window.open('about:blank','tab2');")
        # driver.switch_to.window('tab2')
        
        # Wait for the page to load
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'pdp-mod-product-badge-title'))
            WebDriverWait(driver, 10).until(element_present)
        except TimeoutException:
            print("Timed out waiting for product page to load")
            
        
        
        
        # extract data from the product page
        try:
            product_title = driver.find_element(By.CLASS_NAME, 'pdp-mod-product-badge-title').text
            info_dict["title"] = product_title
        except NoSuchElementException:
            info_dict["title"] = "Error: could not get product information"
        
        
        try:
            product_price_str = driver.find_element(By.XPATH, '//*[@id="module_product_price_1"]/div/div/span').text
            # find the last word of the string
            match = re.search(r'\S+$', product_price_str)
            product_price = match.group(0)
            info_dict["price"] = product_price
        except NoSuchElementException:
            info_dict["price"] = None
        
        try:
            product_catagory = driver.find_element(By.XPATH, '//*[@id="J_breadcrumb"]/li[2]/span/a/span').text
            info_dict["catagory"] = product_catagory
        except NoSuchElementException:
            info_dict["catagory"] = None
        
        
        # Wait for the image to load completely
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'gallery-preview-panel__content')))
        except:
            print("could not find the image div")
        
        
        # download product images-----------------
        try:
            image = driver.find_element(By.XPATH,'.//*[@id="module_item_gallery_1"]/div/div[1]/div/img')
            print(image,"images----------")
            img_url = image.get_attribute('src')
            # create directory to save images if it doesn't exist
            if not os.path.exists("product_images"):
                os.makedirs("product_images")
            response = requests.get(img_url)
            print(response)
            
            
            with open(f"product_images/{product_title}.jpg", "wb") as f:
                f.write(response.content)
                    
        except Exception as e:
            print(e, "error downloading photo")
            
        
    
    
    except TimeoutException:
        info_dict["title"] = "Error: timed out while waiting for page to load"
        info_dict["price"] = None
        

    except Exception as e:
        info_dict["title"] = f"Error: {str(e)}"
        info_dict["price"] = None
        info_dict["image"] = f"Error: {str(e)}"
        
            
    finally:
         
        # Close the new tab and switch back to the main window
        try:
            driver.close()
        except : 
            pass
        # driver.switch_to.window(driver.window_handles[0])
    
    return info_dict


# function to save list of product information to JSON file
def save_info_to_json(info):
    # info is an array
    with open('product_info.json', 'w') as f:
        json.dump(info, f)


def main():
    info = []
    
    # set up driver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


    # navigate to the website
    driver.get("https://www.daraz.com.bd/#")


    # slow scroll
    SCROLL_PAUSE_TIME = 0.5

    # wait for page to load
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'card-jfy-li-content'))
        WebDriverWait(driver, 10).until(element_present)
    except TimeoutException:
        print("Timed out waiting for home page to load")

    # keep scrolling until there are no more products to load
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        # scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
    # a tag -all products
    # card-jfy-li-content




    # now that all products have loaded, you can extract the data you need
    product_a_tags = driver.find_elements(By.CLASS_NAME, "card-jfy-li-content")
    product_img_tags = driver.find_elements(By.CLASS_NAME, "image")
    
    links = []
    for product_a_tag in product_a_tags:
        links.append(product_a_tag.get_attribute('href'))
    product_img_src_links = []
    for product_img_tag in product_img_tags:
        product_img_src_links.append(product_img_tag.get_attribute('src'))
    
    args_list = [(link,product_img_src_links[i]) for i, link in enumerate(links)]
    
    # print(links[:3])

    
        
    # close the browser
    driver.quit()
    
    

    
    
    with Pool(processes=4) as pool:
        # apply scrape_product_info function to each product link
        results = pool.starmap(scrape_product, args_list)
        # iterate through results and append product information to info list
        for result in results:
            info.append(result)
    
    # save info to JSON file
    save_info_to_json(info)
        
    





if __name__ == "__main__":
    
    main()
    print(titles,'--------------')
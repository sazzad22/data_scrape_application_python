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
    # Extract the product information
    
    try:
        
        try:
            element_present = EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div[3]/div[2]/div/div[1]/div[3]/div/div/span'))
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
            if not os.path.exists("async_product_images"):
                os.makedirs("async_product_images")
            response = requests.get(img_url)
            print(response)
            
            
            with open(f"async_product_images/{product_title}.jpg", "wb") as f:
                f.write(response.content)
                    
        except Exception as e:
            print(e, "error downloading photo")
    
    except TimeoutException:
        info_dict["title"] = "Error: timed out while waiting for page to load"
        info_dict["price"] = None
        

    except Exception as e:
        info_dict["title"] = f"Error: {str(e)}"
        info_dict["price"] = None
    
    
    finally:
        
        # Close the new tab and switch back to the main window
        try:
            driver.close()
            # Switch back to the original tab
            # driver.switch_to.window(current_window)
            driver.switch_to.window(driver.window_handles[0])
        except : 
            pass
    
    # return the product info as dictionary
    return info_dict
    
    
    
    
   

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
    for link in links[:6]:
        tasks.append(asyncio.create_task(scrape_product(link,driver)))
    
    # wait for all tasks to complete
    product_infos = await asyncio.gather(*tasks)
    
    
    
    # save info to JSON 
    save_info_to_json(product_infos)
    
    

if __name__ == "__main__":
    asyncio.run(main())
    
    
        
        
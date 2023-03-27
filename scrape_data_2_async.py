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
import pandas as pd

class ScrapeData:
    
    """
    This ScrapeData class is designed to scrape product data from the Daraz website, specifically the homepage and individual product pages.
    
    This code appears to scrape data from a website using Selenium WebDriver, specifically the website "https://www.daraz.com.bd/#". The __init__ method sets the home URL for the website.

    The __scrape_product_links method uses WebDriver to access the website and scrape the URLs of all products listed on the Daraz homepage. It scrolls to the bottom of the page and then extracts the URLs of each product.

    The __scrape_product method is an asynchronous method that uses WebDriver to access a specific product page and extract information about the product. The method takes a URL as input and returns a dictionary containing information about the product, including the title, price, category, and image link. It also downloads the product image and saves it to the "async_product_images" directory if it doesn't already exist. If an error occurs during the scraping process, the corresponding error message is returned in the title field and the price field is set to None.

    
    """
    
    
    def __init__(self) -> None:
        self.__daraz_home_url = "https://www.daraz.com.bd/#"
    
    async def __scrape_product_links(self):
 
        """
        Scrape the links of all products listed on the Daraz homepage.

        Returns:
        --------
        list:
            A list of URLs for each product listed on the homepage.
        """
        
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        
            
        driver.get(self.__daraz_home_url)
        
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
    
    async def __scrape_product(self,link):

        """
        Private asynchronous method that scrapes a product page using Selenium WebDriver and returns a dictionary containing product information.

        Args:
            link (str): The URL of the product page to be scraped.

        Returns:
            dict: A dictionary containing the product information extracted from the product page, including the product title, price, category, and image link. If any error occurs during the scraping process, the corresponding error message is returned in the title field and the price field is set to None.

        """

        # set up the driver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        
        info_dict = {}
        info_dict['link'] = link
        
        
        await asyncio.sleep(3)
        # Extract the product information
        
        try:
            # open the link
            driver.get(link)
            
            
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
                info_dict["image_link"] = img_url
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
   
    @staticmethod
    def save_info_to_json(product_infos):
        """
        This static method saves the given product_infos list as a JSON file with the name "async_product_info.json".

        Args:

            product_infos: A list of dictionaries containing product information.

        Returns:

            None.
        """
        with open("async_product_info.json", "w") as f:
            json.dump(product_infos, f)
    
    @staticmethod
    def save_info_to_excel(product_infos, filename):
        """
        This static method saves the given product_infos list as a Exel file with the passed in filename

        Args:

            product_infos: A list of dictionaries containing product information.
            filename: a string ,which the name of the Exel file with .xls extension

        Returns:

            None.
        """
        df = pd.DataFrame(product_infos)
        file_path = os.path.join(os.getcwd(), filename)
        df.to_excel(file_path, index=False)

    async def scrape_and_save_data(self):
        
        """
        This async method scrapes product information from a list of product links and saves the information as JSON. It first calls the private method __scrape_product_links to obtain the links, and then creates a task for each link to be processed concurrently using the private method __scrape_product.
        
        The method then waits for all tasks to complete using asyncio.gather. The scraped product information is stored as a list of dictionaries in the product_infos instance variable.
        """
        
        links = await self.__scrape_product_links()
        
                
        # scrape product concurrently
        tasks = []
        for link in links[:6]:
            tasks.append(asyncio.create_task(self.__scrape_product(link)))
        
        # wait for all tasks to complete
        self.product_infos = await asyncio.gather(*tasks)
        
        
        
        # save info to JSON 
        # self.__save_info_to_json(product_infos)





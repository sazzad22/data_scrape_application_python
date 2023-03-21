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

# fucntion to scrape the data
async def scrape_product(link):
    # set up the driver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    try:
        # open the link in new tab
        await driver.get(link)
        driver.execute_script("window.open('about:blank','tab2');")
        driver.switch_to.window('tab2')
        
        # Wait for the page to load
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1[@class='product-title']")))
        
        # extract data from the product page
        
    finally:    
        # Close the new tab and switch back to the main window
        await driver.close()
        await driver.switch_to.window(driver.window_handles[0])


# Define the multiprocessing function
def scrape_products_multiprocessing(links):
    with Pool(processes=4) as pool:
        # Run the asynchronous scraping function for each link using the multiprocessing pool
        results = pool.map_async(asyncio.run, [scrape_product(link) for link in links])
        pool.close()
        pool.join()
        return results.get()


async def main():
    
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
        print("Timed out waiting for page to load")

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
    
    links = []
    for product_a_tag in product_a_tags:
        links.append(product_a_tag.get_attribute('href'))
    print(links)

    
        
    # close the browser
    driver.quit()
    
     # scrape data for every link in links using multiprocessing
    pool = Pool(processes=4)  
    pool.map(scrape_product, links)
    pool.close()
    pool.join()
    





if __name__ == "__main__":
    
    main()
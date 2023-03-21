import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from multiprocessing import Pool


# Define the scraping function
async def scrape_product_async(link):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Load the product page
        await driver.get(link)

        # Wait for the product data to load
        await asyncio.sleep(5)

        # Extract the product data from the page
        product_title = await driver.find_element(By.XPATH, "//h1[@class='product-title']")
        product_price = await driver.find_element(By.XPATH, "//span[@class='product-price']")
        product_description = await driver.find_element(By.XPATH, "//div[@class='product-description']")

        # Print the extracted data
        print(f"Product Title: {await product_title.text}")
        print(f"Product Price: {await product_price.text}")
        print(f"Product Description: {await product_description.text}")

    finally:
        # Close the driver
        await driver.quit()


# Define the multiprocessing function
def scrape_product_multiprocessing(link):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Load the product page
        driver.get(link)

        # Wait for the product data to load
        time.sleep(5)

        # Extract the product data from the page
        product_title = driver.find_element(By.XPATH, "//h1[@class='product-title']")
        product_price = driver.find_element(By.XPATH, "//span[@class='product-price']")
        product_description = driver.find_element(By.XPATH, "//div[@class='product-description']")

        # Print the extracted data
        print(f"Product Title: {product_title.text}")
        print(f"Product Price: {product_price.text}")
        print(f"Product Description: {product_description.text}")

    finally:
        # Close the driver
        driver.quit()


# Scrape product data using asyncio
async def scrape_products_async(links):
    await asyncio.gather(*[scrape_product_async(link) for link in links])


# Scrape product data using multiprocessing
def scrape_products_multiprocessing(links):
    with Pool(processes=4) as pool:
        pool.map(scrape_product_multiprocessing, links)


if __name__ == "__main__":
    # Get the product links
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.example.com/products")
        product_a_tags = driver.find_elements(By.XPATH, "//a[@class='product-link']")

        links = []
        for product_a_tag in product_a_tags:
            links.append(product_a_tag.get_attribute('href'))

    finally:
        driver.quit()

    # Scrape product data using asyncio
    asyncio.run(scrape_products_async(links))

    #

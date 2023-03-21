import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from multiprocessing import Pool


# Define the asynchronous scraping function
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

        # Return the extracted data as a dictionary
        return {
            'link': link,
            'title': await product_title.text,
            'price': await product_price.text,
            'description': await product_description.text,
        }

    finally:
        # Close the driver
        await driver.quit()


# Define the multiprocessing function
def scrape_products_multiprocessing(links):
    with Pool(processes=4) as pool:
        # Run the asynchronous scraping function for each link using the multiprocessing pool
        results = pool.map_async(asyncio.run, [scrape_product_async(link) for link in links])
        pool.close()
        pool.join()
        return results.get()


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

    # Scrape product data using asyncio and multiprocessing
    print("Scraping products using asyncio and multiprocessing...")
    start_time = time.time()
    results = scrape_products_multiprocessing(links)
    end_time = time.time()
    print(f"Scraping complete in {end_time - start_time:.2f} seconds")

    # Print the extracted data
    for result in results:
        print(f"Product Title: {result['title']}")
        print(f"Product Price: {result['price']}")
        print(f"Product Description: {result['description']}")

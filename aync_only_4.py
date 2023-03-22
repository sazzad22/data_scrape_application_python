import asyncio
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager



async def scrape_product(link):
    # set up the driver
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    try:
        # open the link in a new tab
        await driver.execute_script("window.open('about:blank','tab2');")
        await driver.switch_to.window(driver.window_handles[1])
        await driver.get(link)

        # Wait for the page to load
        # await asyncio.wait_for(driver.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[@class='product-title']"))), timeout=10)

        # extract data from the product page

    finally:
        # Close the new tab and switch back to the main window
        await driver.close()
        await driver.switch_to.window(driver.window_handles[0])


async def main():

    # set up driver
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    # navigate to the website
    driver.get("https://www.daraz.com.bd/#")

    # slow scroll
    SCROLL_PAUSE_TIME = 0.5

    # wait for page to load
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'card-jfy-li-content'))
        await asyncio.wait_for(WebDriverWait(driver, 10).until(element_present), timeout=10)
    except TimeoutError:
        print("Timed out waiting for page to load")

    # keep scrolling until there are no more products to load
    while True:
        last_height = await driver.execute_script("return document.body.scrollHeight")
        # scroll down to bottom
        await driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # wait to load page
        await asyncio.sleep(SCROLL_PAUSE_TIME)
        # calculate new scroll height and compare with last scroll height
        new_height = await driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # a tag -all products
    # card-jfy-li-content

    # now that all products have loaded, you can extract the data you need
    product_a_tags = await driver.find_elements(By.CLASS_NAME, "card-jfy-li-content")

    links = []
    for product_a_tag in product_a_tags:
        links.append(await product_a_tag.get_attribute('href'))

    print(links[:3])

    # close the browser
    await driver.quit()

    # scrape data for every link in links using asyncio
    start_time = time.time()
    await asyncio.gather(*[scrape_product(link) for link in links])
    end_time = time.time()

    print(f"Scraping complete in {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())

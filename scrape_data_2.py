from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from webdriver_manager.chrome import ChromeDriverManager



# create a new instance of the Chrome driver

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



# //*[@id="hp-just-for-you"]/div[2]/div[1]/div/div[2]/div[1]/a/div/div[2]/div[2]/span

# now that all products have loaded, you can extract the data you need
product_items = driver.find_elements(By.CLASS_NAME, "card-jfy-item")

products_items = []
for products in product_items:
    products_items.append(products.find_element(By.CLASS_NAME, "card-jfy-item-desc"))
    # print(products_items, 'product items')


product_titles = []
for products in product_items:
    product_titles.append(products.find_element(By.CLASS_NAME, "card-jfy-title"))
    # print(product_titles, 'product title')

product_title_span = []
for products in product_titles:
    element = products.find_element(By.CLASS_NAME, "title").text
    product_title_span.append(element)
    print(product_title_span)
    
# close the browser
driver.quit()



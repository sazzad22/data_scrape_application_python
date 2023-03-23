import asyncio
import json
from pyppeteer import launch

async def scrape_product_links():
    browser = await launch()
    page = await browser.newPage()

    # navigate to the dynamic website and scroll to the bottom
    await page.goto('https://example.com')
    await page.waitForSelector('.product')
    num_products = await page.evaluate('() => document.querySelectorAll(".product").length')
    while True:
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.waitForTimeout(2000)  # wait for products to load
        new_num_products = await page.evaluate('() => document.querySelectorAll(".product").length')
        if new_num_products == num_products:
            break
        num_products = new_num_products

    # extract product links
    links = []
    for product in await page.querySelectorAll('.product'):
        link = await product.querySelectorEval('a', '(element) => element.href')
        links.append(link)

    # close browser and return links
    await browser.close()
    return links

async def scrape_product(link):
    browser = await launch()
    page = await browser.newPage()

    # navigate to product link and wait for it to load
    await page.goto(link)
    await page.waitForSelector('.product-title')

    # extract product title and price
    title = await page.querySelectorEval('.product-title', '(element) => element.textContent')
    price = await page.querySelectorEval('.product-price', '(element) => element.textContent')

    # close browser and return product info
    await browser.close()
    return {"title": title, "price": price}

async def main():
    # scrape product links
    links = await scrape_product_links()

    # scrape product info concurrently
    tasks = []
    for link in links:
        tasks.append(asyncio.ensure_future(scrape_product(link)))

    # wait for all tasks to complete
    info = []
    for task in asyncio.as_completed(tasks):
        result = await task
        info.append(result)

    # save product info to json file
    with open('product_info.json', 'w') as f:
        json.dump(info, f)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

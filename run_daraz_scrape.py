from scrape_data_2_async import ScrapeData
import asyncio

# create obj
daraz_data = ScrapeData()

asyncio.run(daraz_data.scrape_and_save_data())

ScrapeData.save_info_to_excel(daraz_data.product_infos, 'async_product_info.xls')
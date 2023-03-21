import requests
import re
import selenium
from bs4 import BeautifulSoup


PATH = "/run/media/joy/New Volume/game/chromedriver.exe"

class ScrapeData:
    
    def __init__(self,url) -> None:
        self.url = url
        
    def fetch_data(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content,'lxml')
        
        return soup

    def scrape_data(self):
        soup = self.fetch_data()
        pattern = re.compile(r'\bcard-jfy-item\b')
        product_divs = soup.find_all('div', class_=pattern)
        
        product_data = []
        
        
              
            
        for product in product_divs:
            product_data.append(product.span)
        
        return product_data
                
        
        
daraz_data = ScrapeData('https://www.daraz.com.bd/#')



data = daraz_data.scrape_data()
print(data)


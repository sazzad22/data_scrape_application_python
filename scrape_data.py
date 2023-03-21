from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

driver = webdriver.Chrome(ChromeDriverManager().install())

url = 'https://www.youtube.com/@trailerspot4k/videos'



driver.get(url)

# style-scope ytd-rich-item-renderer
# //*[@id="video-title"]
# //*[@id="metadata-line"]/span[1]
# //*[@id="metadata-line"]/span[2]

videos = driver.find_elements(By.CLASS_NAME,'style-scope ytd-rich-item-renderer')

for video in videos:
    title = video.find_element(By.XPATH, './/*[@id="video-title"]').text
    view = video.find_element(By.XPATH, './/*[@id="metadata-line"]/span[1]').text    
    when = video.find_element(By.XPATH, './/*[@id="metadata-line"]/span[2]').text
    
    print(title, view, when, sep='\n')
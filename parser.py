import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

options = Options()
options.add_argument("--headless")  
options.add_argument("--disable-gpu") 
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
options.add_argument("--window-size=1920x1200")
options.add_argument("--log-level=3")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
driver.get("https://realtylink.org/en/properties~for-rent")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.description')))

html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')
listings = soup.find_all('div', class_="description")

collected_listings = 0
max_listings = 60

listings_info = []

try:
    while collected_listings < max_listings:

        for listing in listings:
            if collected_listings >= max_listings:
                break

            title_div = listing.find('span', class_='category')
            title = title_div.find('div').text.strip() if title_div and title_div.find('div') else 'Title not available'
            
            price_div = listing.find('div', class_='price')
            price = price_div.text.strip() if price_div else 'Price not available'
            
            features_container = listing.find('div', class_='features')
            rooms = features_container.find('div', class_='cac').text.strip() if features_container and features_container.find('div', class_='cac') else 'Room count not available'
            square_footage = features_container.find('span', class_='sqft').text.strip() if features_container and features_container.find('span', class_='sqft') else 'Square footage not available'

            address_div = listing.find('span', class_='address')
            if address_div:
                address_divs = address_div.find_all('div')
                address = address_divs[0].text.strip() if address_divs and len(address_divs) > 0 else 'Address not available'
                region = address_divs[1].text.strip() if address_divs and len(address_divs) > 1 else 'Region not available'
            else:
                address = 'Address not available'
                region = 'Region not available'

            link = listing.find('a', class_='a-more-detail')['href'] if listing.find('a', class_='a-more-detail') else None
            full_link = f"https://realtylink.org{link}" if link else 'Link not available'
            
            if full_link == 'Link not available':
                continue
				
            driver.get(full_link)
            time.sleep(1)
             
            photo_urls = driver.execute_script("return window.MosaicPhotoUrls;")
            
            detailed_html_content = driver.page_source
            detailed_soup = BeautifulSoup(detailed_html_content, 'html.parser')
            
            description_div = detailed_soup.find("div", itemprop="description")
            description = description_div.text.strip() if description_div else 'No description'

            listing_info = {
                "title": title,
                "price": price,
                "address": address,
                "region": region,
                "rooms": rooms,
                "description": description,
                "square_footage": square_footage,
                "link": full_link,
                "photo_urls": photo_urls
            }

            listings_info.append(listing_info)
            
            collected_listings += 1

        next_button = driver.find_elements(By.CSS_SELECTOR, "li.next a")
        if next_button:
            next_button[0].click()
            time.sleep(2)
        else:
            print("No more pages to process.")
            break

finally:
    driver.quit()

with open('listings.json', 'w') as json_file:
    json.dump(listings_info, json_file, indent=2)

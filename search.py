import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
from translator import Trans

CHROMEDRIVER = "/Users/julien/Downloads/chromedriver-mac-x64 2/chromedriver"

class Search:
    def __init__(self) -> None:
        pass

    def get_duckduckgo_search_links(self, queries):
        already_added_urls = []
        urls = {}
        for query in queries:
            print(query)
            query = query.replace(" ", "+")
            options = Options()
            options.add_argument('--lang=en')
            service = Service(CHROMEDRIVER)
            driver = webdriver.Chrome(service=service, options=options)
            
            driver.get(f'https://duckduckgo.com/?q={query}&t=h_&ia=web')
            actions = ActionChains(driver)
            
            wait = WebDriverWait(driver, 10)
            button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div/section/nav/ul[2]/li[2]/button/span[2]/span/div/a")))
            actions.move_to_element(button).click().perform()
            button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="setting_kad"]')))
            actions.move_to_element(button).click().perform()
            button.send_keys("e")
            button = wait.until(EC.presence_of_element_located((By.ID, "more-results")))
            button.send_keys(Keys.RETURN)
            time.sleep(2)            
            

            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            
            articles = soup.find_all("article")
            
            try:                
                sites = []
                for article in articles[2:]:
                    url = article.find(class_="Rn_JXVtoPVAFyGkcaXyK").get("href")
                    already_added = url in already_added_urls
                    if not already_added:
                        title = article.find(class_="eVNpHGjtxRBq_gLOfGDr").get_text()
                        website_preview = article.find(class_="kY2IgmnCmOGjharHErah").get_text()
                        site = {
                            "url" : url,
                            "title" : title,
                            "website_preview" : website_preview
                        }

                        if "/en" in url or Trans.is_english(website_preview) or Trans.is_english(title):
                            sites.append(site)
                            already_added_urls.append(url)
                    
                urls[query] = sites
                
            except:
                pass
            
            driver.quit()
        with open('web_search_links.json', 'w') as json_file:
            json.dump(urls, json_file, indent=4)
        return urls
    
    def google_search(self, query, num_results=30, language='lang_en'):
        api_key = ''
        search_engine_id = ''
        url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}&num={num_results}&lr={language}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.status_code)
            return None

    def extract_urls(self, search_results):
        urls = []
        if 'items' in search_results:
            for item in search_results['items']:
                urls.append(item['link'])
        return urls

    def get_search_results(self, keywords, num_results=30, language='lang_en'):
        all_results = {}
        for keyword in keywords:
            search_results = self.google_search(keyword, num_results, language)
            if search_results:
                urls = self.extract_urls(search_results)
                all_results[keyword] = urls
            else:
                all_results[keyword] = []
        return all_results
import json
import requests
from bs4 import BeautifulSoup
import hashlib
from translator import Trans
from langdetect import detect
import os

translator = Trans
HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

class Scraper:
    def __init__(self, websites_data = {}) -> None:
        self.websites_data = websites_data
        
    def scrape_initial_frontier(self, initial_frontier):
        print()
        for keyword, sites in initial_frontier.items():
            for site in sites:
                try:
                    website_data = self.fetch_website_data(site)
                    if website_data:
                        unique_id = self.generate_unique_id(site["url"])
                        self.websites_data[unique_id] = website_data
                except Exception as e:
                    print(e)
        self.save_website_data()
                    
    def save_website_data(self):
        file_name = "websites_data.json"
        with open(file_name, 'w') as json_file:
            json.dump(self.websites_data, json_file, indent=4)

    def fetch_website_data(self, site):
        try:
            is_dict = self.is_dict(site)
            if is_dict:
                url = site.get("url")
                website_preview = site.get("website_preview")
                headline = site.get("title")
            else:
                url = site
                
            if "doi.org" in url or "ncbi" in url or "handle.net" in url or "vis.uni-stuttgar" in url or "scholar.google" in url:
                return None
            
            response = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            if response.status_code == 200 and self.check_if_tuebingen_relevant(soup):
                
                html_text = self.correct_html_text(soup.get_text())
                
                # relevant_text = self.get_relevant_text(soup)
                all_headlines = self.get_all_headlines(soup)
                all_paragraphs = self.get_all_paragraphs(soup)
                    
                if not is_dict:
                    # Extracting headline
                    headline = soup.title.string if soup.title else 'No Title'
                    
                    # Extracting the first three sentences of the <p> text
                    paragraphs = soup.find("body").find_all('p')[:-1]
                    first_three_sentences = []
                    for p in paragraphs:
                        sentences = p.get_text().split('. ')
                        for sentence in sentences:
                            if len(first_three_sentences) < 3:
                                first_three_sentences.append(sentence)
                            else:
                                break
                        if len(first_three_sentences) >= 3:
                            break
                    website_preview = '. '.join(first_three_sentences) + '.'
                
                # Extracting keywords (meta tags)
                keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
                keywords = keywords_meta['content'] if keywords_meta else ''
                
                # Extracting outgoing URLs
                outgoing_urls = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]
                
                # Extracting images' alt text
                images = soup.find_all('img')
                images_alt = [img['alt'] for img in images if 'alt' in img.attrs]
                
                return {
                    'url': url,
                    'html_text': html_text,
                    # 'relevant_text' : relevant_text,
                    'headline': headline,
                    'all_headlines' : all_headlines,
                    'all_paragraphs' : all_paragraphs,
                    'website_preview': website_preview,
                    'keywords': keywords,
                    'outgoing_urls': outgoing_urls,
                    'images_alt': images_alt
                }
            else:
                print(response.reason, url)
                return None
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def generate_unique_id(self, url):
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_all_headlines(self, soup):
        body = soup.find("body")
        if body is not None:
            elements = body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            return [element.get_text() for element in elements]
        else:
            return []
    
    def get_all_paragraphs(self, soup):
        body = soup.find("body")
        if body is not None:
            elements = body.find_all(["p"])
            return [element.get_text() for element in elements]
        else:
            return []
        
    def get_relevant_text(self, soup):
        body = soup.find("body")
        elements = body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])

        text = ""
        for element in elements:
            text = text + " " + element.text.strip()
        return text
    
    def is_dict(self, variable):
        return isinstance(variable, dict)
    
    def correct_html_text(self, html):
        html = html.replace('\\', '\\\\')
        html = html.replace("'", '"')
        html = html.replace('\\"', '"')
        html = html.replace(',}', '}').replace(',]', ']')
        return html
    
        # for example check_if_tuebingen_relevant(response.content)
    def check_if_tuebingen_relevant(self, soup):
        language = detect(soup.get_text())
        text = soup.get_text(separator=' ').lower()
        if language == 'en':
            if 'tuebingen' in text:
                return True
            elif 'tübingen' in text:
                return True 
        return False
    
    def sum_all_scraped_websites(self):
        
        directory = 'scraped_websites'
        files = os.listdir(directory)
        json_files = [f for f in files if f.endswith('.json')]
        
        all_json_data = {}
        for json_file in json_files:
            file_path = os.path.join(directory, json_file)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    important_json = {
                        'url': data["url"],
                        'html_text': data["html_text"],
                        # 'relevant_text' : relevant_text,
                        'headline': data["headline"],
                        'website_preview': data["website_preview"],
                    }
                    all_json_data[json_file.replace('.json', '')] = important_json
            except FileNotFoundError:
                print(f"The file {json_file} was not found.")
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file {json_file}.")

        
        with open("websites_data.json", 'r') as f:
            websites_data = json.load(f)

        news_websites_data = {}
        for key in websites_data:
            data = websites_data[key]
            important_json = {
                'url': data["url"],
                'html_text': data["html_text"],
                # 'relevant_text' : relevant_text,
                'headline': data["headline"],
                'website_preview': data["website_preview"],
            }
            news_websites_data[key] = important_json

        output_file = 'all_json_data.json'
        combined_data = {**all_json_data, **news_websites_data}
        try:
            with open(output_file, 'w') as outfile:
                json.dump(combined_data, outfile, indent=4)
            print(f"All JSON data has been saved to {output_file}")
        except Exception as e:
            print(f"An error occurred while saving the JSON data: {e}")

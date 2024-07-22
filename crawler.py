import pandas as pd
import scrape
import json
import gzip
from concurrent.futures import ThreadPoolExecutor
import threading
import os
import urllib.parse

frontier_lock = threading.Lock()
crawled_lock = threading.Lock()
problem_lock = threading.Lock()

class Crawler:
    def __init__(self) -> None:
        pass
    
    def crawl(self, url):
        data = scrape.Scraper().fetch_website_data(url)
        return data

    def delete_url_from_frontier(self, url):
        with frontier_lock:
            df = pd.read_csv('crawler_files/frontier.csv')
            df = df[df['url'] != url]
            df.to_csv('crawler_files/frontier.csv', index=False)

    def add_url_to_already_crawled(self, url):
        with crawled_lock:
            df = pd.read_csv('crawler_files/urls_already_crawled.csv')
            url_to_append = pd.DataFrame([url], columns=['url'])
            df = pd.concat([df, url_to_append], ignore_index=True)  # type: ignore
            df.to_csv('crawler_files/urls_already_crawled.csv', index=False)

    def add_urls_to_frontier(self, liste, lock=True):
        if lock:
            with frontier_lock:
                df = pd.read_csv('crawler_files/frontier.csv')
                crawled_urls = pd.read_csv('crawler_files/urls_already_crawled.csv')['url'].tolist()
                problem_urls = pd.read_csv('crawler_files/problem_urls.csv')['url'].tolist()
                liste = list(dict.fromkeys(liste))
                urls = [item.replace('"', '') for item in liste if item not in crawled_urls and item not in df['url'].tolist() and item not in problem_urls]
                urls_df = pd.DataFrame(urls, columns=['url'])
                df = pd.concat([df, urls_df], ignore_index=True)  # type: ignore
                df.to_csv('crawler_files/frontier.csv', index=False)
        else:
            df = pd.read_csv('crawler_files/frontier.csv')
            crawled_urls = pd.read_csv('crawler_files/urls_already_crawled.csv')['url'].tolist()
            problem_urls = pd.read_csv('crawler_files/problem_urls.csv')['url'].tolist()
            liste = list(dict.fromkeys(liste))
            urls = [item.replace('"', '') for item in liste if item not in crawled_urls and item not in df['url'].tolist() and item not in problem_urls]
            urls_df = pd.DataFrame(urls, columns=['url'])
            df = pd.concat([df, urls_df], ignore_index=True)  # type: ignore
            df.to_csv('crawler_files/frontier.csv', index=False)

    def add_url_to_problem_urls(self, url):  # type: ignore
        with problem_lock:
            df = pd.read_csv('crawler_files/problem_urls.csv')
            url_to_concat = pd.DataFrame([url], columns=['url'])
            df = pd.concat([df, url_to_concat], ignore_index=True)  # type: ignore
            df.to_csv('crawler_files/problem_urls.csv', index=False)

    def process_url(self, url):
        url = url.replace('"', '')
        try:
            data = self.crawl(url)
            if data is not None:
                self.add_urls_to_frontier(data['outgoing_urls'])
                self.add_url_to_already_crawled(url)
                hash_code = scrape.Scraper().generate_unique_id(url)
                
                dir = "scraped_websites"
                jsonfilename = os.path.join(dir, f'{hash_code}.json')
                with open(jsonfilename, 'w') as f:
                    json.dump(data, f)
                # with gzip.open(f'{jsonfilename}.gz', 'wb') as fout:       # Save as gzip
                #     with open(jsonfilename, 'rb') as fin:
                #         fout.write(fin.read())
            self.add_url_to_problem_urls(url)
            self.delete_url_from_frontier(url)
        except Exception as err:
            print(f"{err} occurred with {url}\n")
            self.add_url_to_problem_urls(url)
            self.delete_url_from_frontier(url)
            
    def add_initial_links_to_frontier(self):
        with open('websites_data.json', 'r') as file:
            data = json.load(file)

        all_outgoing_urls = []

        # Loop through each entry in the JSON data
        for entry in data.values():
            if 'outgoing_urls' in entry:
                all_outgoing_urls.extend(entry['outgoing_urls'])
        all_outgoing_urls = [urllib.parse.quote(url.replace("\n", ""), safe=':/') for url in all_outgoing_urls]
        self.add_urls_to_frontier(list(all_outgoing_urls), lock=False)

    def start_crawling(self):
        self.add_initial_links_to_frontier()
        while True:
            with frontier_lock:
                frontier = pd.read_csv('crawler_files/frontier.csv')
                if frontier.empty:
                    break
                urls = frontier['url'].tolist()

            with ThreadPoolExecutor(max_workers=20) as executor:  # Adjust max_workers as needed
                executor.map(self.process_url, urls)

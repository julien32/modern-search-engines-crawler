from search import Search
from scrape import Scraper
import json
from helpers import make_keywords
from crawler import Crawler
# keywords = ['tübingen food']
keywords = [
    'tübingen food',
    'tübingen food and drink',
    'uni tübingen',
    'university of tübingen',
    'tübingen research',
    'tübingen history',
    'tübingen culture',
    'tübingen tourism',
    'tübingen attractions',
    'tübingen museums',
    'tübingen restaurants',
    'tübingen hotels',
    'tübingen old town',
    'tübingen events',
    'tübingen nightlife',
    'tübingen public transport',
    'tübingen parks',
    'tübingen shopping',
    'tübingen student life',
    'tübingen science',
    'tübingen technology',
    'tübingen medical research',
    'tübingen economics',
    'tübingen sociology',
    'tübingen geography',
    'tübingen anthropology',
    'tübingen architecture',
    'tübingen art',
    'tübingen music',
    'tübingen literature',
    'tübingen theatre',
    'tübingen sports',
    'tübingen hiking',
    'tübingen biking',
    'tübingen riverside',
    'tübingen car repair',
    'tübingen cyber valley',
    'tübingen vegan',
    'tübingen vegetarian',
    'research institutes',
    'academic events',
    'libraries',
    'history',
    'museums',
    'theaters',
    'concerts',
    'old town',
    'castles',
    'stockerkahn',
    'botanical garden',
    'restaurants',
    'cafes',
    'schokomarkt',
    'markets',
]   

def main():
    crawler = Crawler()
    scraper = Scraper()
    search = Search()

    #Get initial frontier from duckduckgo
    initial_frontier = search.get_duckduckgo_search_links(make_keywords(keywords))  
    
    #Scrape initial frontier
    scraper.scrape_initial_frontier(initial_frontier)
    
    #Start crawling outgoing from initial frontier
    crawler.start_crawling()
    
    #save all scraped websites in one .json file
    scraper.sum_all_scraped_websites()
    
    
if __name__ == "__main__":
    main()
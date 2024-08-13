import requests
from bs4 import BeautifulSoup
import random
from categories import scrape_categories

# Function to get a random proxy
def get_random_proxy(proxies):
    return random.choice(proxies)

# Function to scrape with proxy rotation
def scrape_with_proxy_rotation(url, proxies):
    for i in range(10):  # Attempt to scrape 10 times
        proxy = get_random_proxy(proxies)
        print(f"Using proxy: {proxy}")

        try:
            response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=5)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                scrape_categories(soup)

                # Example: Find all the <h2> tags on the page
                h2_tags = soup.find_all('h2')

                # Print the text of each <h2> tag
                for tag in h2_tags:
                    print(tag.get_text())
                break  # Exit the loop if successful

            else:
                print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")


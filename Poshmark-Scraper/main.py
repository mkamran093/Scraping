import requests
from bs4 import BeautifulSoup

def main():

    url = "https://poshmark.com/brand/Nike-Men"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    divs = soup.find('div', class_='tiles_container').find_all('div', {'data-et-name': 'listing'})
    print(len(divs))
    
if __name__ == "__main__":
    main()
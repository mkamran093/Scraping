from bs4 import BeautifulSoup
import requests
import re

def scrape_product(product):
    print("Scraping product", product['name'], "...")
    response = requests.get(product['url'])
    soup = BeautifulSoup(response.content, 'html.parser')

    dimensions_dict = {}
    description_dict = {}
    product_overview = []
    images = []

    # Extract the product details
    product_name = soup.find('h1', {'data-hb-id': 'Heading'}).get_text(strip=True)
    sfprice_div = soup.find('div', class_='SFPrice').find_all('span')[0].get_text(strip=True)
    product_price = float(''.join(re.findall(r'\d+', sfprice_div)))
    product_description = soup.find('div', class_='RomanceCopy-text').get_text(strip=True)
    product_rating = soup.find('span', class_='ProductRatingNumberWithCount-rating').get_text(strip=True)
    div = soup.find('div', id='Pres_list_keyval_table::default')
    for dt, dd in zip(div.find_all('dt'), div.find_all('dd')):
        key = dt.get_text(strip=True)
        value = dd.get_text(strip=True)
        dimensions_dict[key] = value
    div = soup.find('div', class_='DescriptionList')
    for dt, dd in zip(div.find_all('dt'), div.find_all('dd')):
        key = dt.get_text(strip=True)
        value = dd.get_text(strip=True)
        description_dict[key] = value
    div = soup.find('div', {'data-hb-id': 'Box'})
    for p in div.find_all('p'):
        product_overview.append(p.get_text(strip=True))
    div = soup.find('div', class_=re.compile(r'\b' + re.escape('ProductDetailImageCarousel-carouselItem') + r'\b'))
    for img in div.find_all('img'):
        images.append(img['src'])
    availability = True if soup.find('span', class_='ShippingHeadlin-text').get_text(strip=True) == 'This Item Is Out Of Stock' else False


def scrape_sub_categories(sub_category):
    print("Scraping sub-category", sub_category['name'], "...")
    response = requests.get(sub_category['url'])
    soup = BeautifulSoup(response.content, 'html.parser')

    all_products = []

    total_products = int(re.sub(r'\D', '', soup.find('div', {'data-enzyme-id': 'ResultsText'}).text))

    while (len(all_products) < total_products):
        for product in soup.find_all('div', {'data-hb-id': 'ProductCard'}):
            product_url = product.find('a', {'data-enzyme-id': 'BrowseProductCardWrapper-component'})['href']
            all_products.append(product_url)
        
        # Check if there is a next page
        next_page = soup.find('a', {'data-enzyme-id': 'paginationNextPageLink'})['href']
        if next_page:
            response = requests.get(next_page)
            soup = BeautifulSoup(response.content, 'html.parser')
        else:
            break
    
    for product in all_products:
        scrape_product(product)


def scrape_categories(soup):
    category_name = soup.find('div', class_='CategoryCarousel-title').get_text(strip=True)

    # Extract the sub-categories
    sub_categories = []
    for item in soup.find_all('li', class_='CategoryCarousel-carouselItem'):
        sub_category_name = item.find('p', class_='CategoryCarousel-imageTitle').get_text(strip=True)
        sub_category_url = item.find('a', class_='CategoryCarousel-imageContainer')['href']
        
        scrape_sub_categories({
            'name': sub_category_name,
            'url': sub_category_url})
    


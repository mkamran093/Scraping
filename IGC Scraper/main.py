import requests
from bs4 import BeautifulSoup

# Define the target URL
url = 'https://importglasscorp.com/product/'

def scrape_product(partNo):
    # response = requests.get(url + partNo)

    with open('product.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    status_code = 200
    if status_code == 200:
        soup = BeautifulSoup(html_content, 'html.parser')
        # soup = BeautifulSoup(response.content, 'html.parser')
        
        try:
            product_name = soup.find('div', class_='col-md-8').find('p').text.strip()

            # Find the table with class 'table'
            table = soup.find('table', class_='table')
        except:
            print(f"Failed to retrieve desired content")
            return
        
        print(f"\nProduct Name: {product_name}")

        # Extract information for all parts
        print("\nAll Parts:")
        if table:
            for row in table.find_all('tr')[1:]:  # Skip header row
                tds = row.find_all('td')
                if len(tds) >= 3:
                    part_number = tds[0].text.strip()
                    part_price = tds[1].find('b').text.strip() if tds[1].find('b') else "Not found"
                    part_availability = tds[2].find('span', class_='label').text.strip() if tds[2].find('span', class_='label') else "Not found"
                    print(f"Part Number: {part_number}, Price: {part_price}, Availability: {part_availability}")

    else:
        print(f"Failed to retrieve the page. Status code: {status_code}")

def main():

    print('='*50)
    print("Welcome to the Import Glass Corp Scraper")
    print('='*50)
    print('\n\n')
    while True:
        # Ask the user for the part number
        partNo = input("Enter the part number to scrape: ")
        
        # Scrape the product details
        scrape_product(partNo)

        # Ask if the user wants to scrape another product
        choice = input("\nDo you want to scrape another product? (yes/no): ").strip().lower()

        if choice != 'yes':
            print("Exiting...")
            break

if __name__ == "__main__":
    main()

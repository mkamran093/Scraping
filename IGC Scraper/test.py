from bs4 import BeautifulSoup

# Load the HTML file
with open('product.html', 'r', encoding='utf-8') as file:
    html_content = file.read()
soup = BeautifulSoup(html_content, 'html.parser')

# Extract product name
product_name = soup.find('div', class_='col-md-8').find('p').text.strip()

# Find the table with class 'table'
table = soup.find('table', class_='table')

print(f"Product Name: {product_name}")

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
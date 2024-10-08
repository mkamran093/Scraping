# %%
import requests
from bs4 import BeautifulSoup

# %%
import requests
payload = {'api_key': '63655678cd36805b2cb76220', 'query':'marble' , 'country':'us'}
resp = requests.get('https://api.scrapingdog.com/google', params=payload)
print (resp.text)

# %%
import requests
import csv
  
api_key = "63655678cd36805b2cb76220"
url = "https://api.scrapingdog.com/google"
  
params = {
    "api_key": api_key,
    "query": "marble & granite",
    "results": 1000,
    "country": "us",
    "page": 0
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    
    results = data.get('results', []) 
    
    if results:
        headers = results[0].keys()
        with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)
        
        print("Data has been written to output.csv successfully.")
    else:
        print("No results found in the JSON response.")
else:
    print(f"Request failed with status code: {response.status_code}")

# %%
import os
import pandas as pd

folder_path = 'C:/Users/satch/Desktop/marble/'

dataframes = []

for file in os.listdir(folder_path):
    if file.endswith('.csv'):
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(file_path, engine='python', sep=',', on_bad_lines='warn') 
            dataframes.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

combined_df = pd.concat(dataframes, axis=0, ignore_index=True, sort=False)
combined_df.to_csv('marble_tracker.csv', index=False)

print("All CSV files combined successfully!")

# %%
import pandas as pd

# Load the new CSV
file_path = 'marble_tracker.csv'
df = pd.read_csv(file_path)
#df = df[['name', 'reviews', 'categories', 'rating', 'address']]
df.head()

# # Drop duplicate rows based on the 'name' column, keeping the first occurrence
# df_cleaned = df.drop_duplicates(subset=['name'], keep='first')

# # Save the cleaned DataFrame to a new CSV file (optional)


# %%
df.columns

# %%
from datetime import datetime

# Function to calculate hours between two time periods
def calculate_hours(start, end):
    fmt = '%H:%M'
    start = datetime.strptime(start, fmt)
    end = datetime.strptime(end, fmt)
    return (end - start).seconds / 3600

# Hours for each day
days = {
    "18/09/2024": [("8:30", "12:00"), ("13:00", "19:30")],
    "19/09/2024": [("8:30", "12:00"), ("13:00", "18:30")],
    "20/09/2024": [("9:00", "12:30"), ("14:00", "18:30")],
    "23/09/2024": [("8:30", "12:30"), ("13:30", "17:30")],
    "24/09/2024": [("8:30", "13:30"), ("14:30", "18:00")],
    "25/09/2024": [("8:30", "12:00"), ("13:00", "17:00")],
    "26/09/2024": [("8:30", "12:00"), ("13:00", "17:00")],
    "27/09/2024": [("8:30", "11:45"), ("12:45", "17:30")],
    "30/09/2024": [("8:30", "12:20"), ("12:50", "17:20")]
}

# Calculate total hours
total_hours = sum(
    calculate_hours(start, end) for day in days for start, end in days[day]
)

# Multiply total hours by 37.5
total_hours_multiplied = total_hours * 37.5
total_hours, total_hours_multiplied


# %%
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Test URL to scrape roofing companies from Yelp (example URL)
url = 'https://www.yelp.com/search?find_desc=Roofing&find_loc=United+States'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Lists to store the extracted data
company_names = []
phone_numbers = []
websites = []

# Find business listings
for business in soup.find_all('div', class_='container__09f24__sxa9-'):
    name = business.find('a', class_='css-1422juy').text if business.find('a', class_='css-1422juy') else 'N/A'
    phone = business.find('p', class_='css-8jxw1i').text if business.find('p', class_='css-8jxw1i') else 'N/A'
    website = business.find('a', class_='css-1um3nx')["href"] if business.find('a', class_='css-1um3nx') else 'N/A'
    
    company_names.append(name)
    phone_numbers.append(phone)
    websites.append(website)

# Create a DataFrame to store the data
df = pd.DataFrame({
    'Company Name': company_names,
    'Phone Number': phone_numbers,
    'Website': websites
})

# Save the DataFrame to a CSV file
df.to_csv('roofing_companies_test.csv', index=False)

print("CSV file created successfully.")


# %%
from datetime import datetime
import requests  # If using an external API for the exchange rate

def calculate_hours(start, end):
    fmt = '%H:%M'
    start = datetime.strptime(start, fmt)
    end = datetime.strptime(end, fmt)
    return (end - start).seconds / 3600

def total_hours_worked(work_days):
    total_hours = 0
    for date, intervals in work_days.items():
        for start, end in intervals:
            total_hours += calculate_hours(start, end)
    return total_hours

def get_hourly_rate():
    # Assuming a constant hourly rate in USD
    return 37.5

def get_exchange_rate(date):
    # Placeholder for exchange rate API call
    # Example of calling an external API for the exchange rate
    # response = requests.get(f'https://api.exchangerate.com/{date}')
    # return response.json()['USD_to_BRL']
    
    # For now, we return a mock exchange rate (replace with actual rate-fetching code)
    exchange_rates = {
        "18/09/2024": 5.0,
        "19/09/2024": 5.1,
        "20/09/2024": 5.05,
        "23/09/2024": 5.08,
        "24/09/2024": 5.12,
        "25/09/2024": 5.09,
        "26/09/2024": 5.11,
    }
    return exchange_rates.get(date, 5.0)  # Default exchange rate if date not found

def calculate_total_in_usd_and_brl(work_days):
    total_usd = 0
    total_brl = 0
    hourly_rate = get_hourly_rate()
    
    for date, intervals in work_days.items():
        hours = sum(calculate_hours(start, end) for start, end in intervals)
        daily_total_usd = hours * hourly_rate
        exchange_rate = get_exchange_rate(date)
        daily_total_brl = daily_total_usd * exchange_rate
        
        total_usd += daily_total_usd
        total_brl += daily_total_brl
        
    return total_usd, total_brl

# Example usage:
work_days = {
    "18/09/2024": [("8:30", "12:00"), ("13:00", "19:30")],
    "19/09/2024": [("8:30", "12:00"), ("13:00", "18:30")],
    "20/09/2024": [("9:00", "12:30"), ("14:00", "18:30")],
    "23/09/2024": [("8:30", "12:30"), ("13:30", "17:30")],
    "24/09/2024": [("8:30", "13:30"), ("14:30", "18:00")],
    "25/09/2024": [("8:30", "12:00"), ("13:00", "17:00")],
    "26/09/2024": [("8:30", "12:00"), ("13:00", "17:00")],
}

total_usd, total_brl = calculate_total_in_usd_and_brl(work_days)
print(f"Total USD: ${total_usd:.2f}")
print(f"Total BRL: R${total_brl:.2f}")


# %%
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Load company names from the CSV
df = pd.read_csv('marble_boston_data.csv')
df['Date of Organization'] = ''
df['Owner'] = ''

# Set up Selenium WebDriver
driver = webdriver.Chrome()

for index, row in df.iterrows():
    company_name = row['name'].strip()  # Strip any extra spaces from the company name

    try:
        # Step 1: Open the corporation search page
        driver.get('https://corp.sec.state.ma.us/corpweb/CorpSearch/CorpSearch.aspx')

        # Step 2: Wait for the search box to load and enter the company name
        search_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "MainContent_txtEntityName"))
        )
        search_box.clear()
        search_box.send_keys(company_name)

        # Step 3: Click the search button
        search_button = driver.find_element(By.ID, 'MainContent_btnSearch')
        search_button.click()

        # Step 4: Wait for the results table to load and locate the first company link
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "MainContent_grdSearchResultsEntity"))
        )

        # Step 5: Find the link for the company using partial match, case-insensitive
        company_link = driver.find_element(By.XPATH, f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{company_name.lower()}')]")

        # Step 6: Extract the href attribute from the link
        company_href = company_link.get_attribute("href")
        print(f"Copying link: {company_href}")

        # Step 7: Open the extracted URL by navigating directly
        driver.get(company_href)  # Opening the second page with the copied link

        # Step 8: Wait for the company summary page to load
        WebDriverWait(driver, 30).until(
            EC.url_contains("CorpSummary.aspx")
        )

        # Step 9: Scrape the required details from the company summary page
        date_of_organization = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//td[text()='Date of Organization:']/following-sibling::td"))
        ).text.strip()

        owner = driver.find_element(By.XPATH, "//td[text()='Address:']/following-sibling::td").text.strip()

        # Step 10: Populate the DataFrame with the extracted data
        df.at[index, 'Date of Organization'] = date_of_organization
        df.at[index, 'Owner'] = owner

    except Exception as e:
        print(f"Error processing {company_name}: {e}")

    time.sleep(3)  # Delay to avoid overwhelming the server

# Step 11: Close the browser
driver.quit()

# Step 12: Save the updated DataFrame back to a CSV
df.to_csv('updated_marble_boston_data.csv', index=False)


# %%
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to search Google and open the first result
def search_and_open(query):
    # Setup Selenium WebDriver
    options = Options()
    options.headless = False  # Set to True if you want to run headlessly
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Navigate to Google
        driver.get("https://www.google.com/")
        
        # Find the search box, enter the query, and submit
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(query)
        search_box.submit()

        # Wait for the results to load and click the first result
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'h3'))
        )
        first_result.click()
        
        # Wait a moment to ensure the page loads
        time.sleep(5)
        
        # Print the current URL of the opened website
        print(f"Opened website: {driver.current_url}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the driver
        driver.quit()

# Example usage
if __name__ == "__main__":
    query = input("Enter the word you want to search for: ")
    search_and_open(query)


# %%
import pandas as pd
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load CSV file
input_csv = 'marble_boston.csv'
output_csv = 'marble_boston_personal.csv'

# Read the input CSV
df = pd.read_csv(input_csv)

# Prepare a list to store scraped data
data = []

# Load existing progress if the output CSV already exists
if os.path.exists(output_csv):
    existing_data = pd.read_csv(output_csv)
    processed_links = existing_data['Website'].tolist()
else:
    processed_links = []

# Setup Selenium WebDriver
options = Options()
options.headless = False  # Set to True if you want to run headlessly
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Function to search for the official website on Google
def search_google(name, address):
    search_query = f"{name} {address} official site"
    driver.get("https://www.google.com/")
    try:
        # Find the search box, enter the query, and submit
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(search_query)
        search_box.submit()

        # Wait for the results to load and click the first result
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'h3'))
        )
        first_result.click()
        
        # Get the current URL after clicking
        official_website = driver.current_url
        print(f"Clicked on official website: {official_website}")
        return official_website
    except Exception as e:
        print(f"Error searching Google for {name}: {e}")
        return None

# Function to scrape contact info from the official website
def scrape_contact_info():
    try:
        # Wait for the page to load and get the telephone number
        telephone = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'tel:')]"))
        ).text.strip()
        return telephone
    except Exception as e:
        print(f"Error scraping contact info: {e}")
        return None

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    name = row['name']  # Use your actual column name for the name
    address = row['address']  # Use your actual column name for the address
    
    # Skip if the website has already been processed
    if name in processed_links:
        continue

    # Search for the official website
    official_website = search_google(name, address)

    if official_website:
        # Scrape contact info from the official website
        telephone = scrape_contact_info()

        # Store the data if successfully scraped
        if telephone:
            data.append({
                'Name': name,
                'Address': address,
                'Website': official_website,
                'Telephone': telephone
            })

            # Save progress after each successful scrape
            output_df = pd.DataFrame(data)
            output_df.to_csv(output_csv, index=False)

    # Longer sleep interval to avoid detection
    time.sleep(random.uniform(5, 10))

# Final save of any remaining data
if data:
    output_df = pd.DataFrame(data)
    output_df.to_csv(output_csv, index=False)

driver.quit()
print(f"Scraping completed! Data saved to {output_csv}.")


# %%
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import csv

# Selenium Wire configuration to use a proxy
proxy_username = 'username'
proxy_password = 'password'
seleniumwire_options = {
    'proxy': {
        'http': f'http://{proxy_username}:{proxy_password}@city.smartproxy.com:21250',
        'verify_ssl': False,
    },
}

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, seleniumwire_options=seleniumwire_options)

# URL of the web page
url = "https://www.google.com/maps/search/falafel+in+london/"

# Open the web page
driver.get(url)

try: 
    button = driver.find_element(By.XPATH,"//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 XWZjwc']") 
    button.click()
    print("Clicked consent to cookies.") 
except: 
    print("No consent required.")

# Set an implicit wait time to wait for JavaScript to render
driver.implicitly_wait(30)  # Wait for max 30 seconds

# Take a screenshot after the content you want is loaded
screenshot_path = '/path/to/your/destination/screenshot.png'
driver.save_screenshot(screenshot_path)
print(f"Screenshot saved to {screenshot_path}")

def scroll_panel_with_page_down(driver, panel_xpath, presses, pause_time):
    """
    Scrolls within a specific panel by simulating Page Down key presses.

    :param driver: The Selenium WebDriver instance.
    :param panel_xpath: The XPath to the panel element.
    :param presses: The number of times to press the Page Down key.
    :param pause_time: Time to pause between key presses, in seconds.
    """
    # Find the panel element
    panel_element = driver.find_element(By.XPATH, panel_xpath)
    
    # Ensure the panel is in focus by clicking on it
    # Note: Some elements may not need or allow clicking to focus. Adjust as needed.
    actions = ActionChains(driver)
    actions.move_to_element(panel_element).click().perform()

    # Send the Page Down key to the panel element
    for _ in range(presses):
        actions = ActionChains(driver)
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(pause_time)

panel_xpath = "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div"
scroll_panel_with_page_down(driver, panel_xpath, presses=5, pause_time=1)

# Get the page HTML source
page_source = driver.page_source

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(page_source, "html.parser")

# Find all elements using its class
titles = soup.find_all(class_="hfpxzc")
ratings = soup.find_all(class_='MW4etd')
reviews = soup.find_all(class_='UY7F9')
services = soup.find_all(class_='Ahnjwc')

# Print the number of places found
elements_count = len(titles)
print(f"Number of places found: {elements_count}")

# Specify the CSV file path
csv_file_path = '/path/to/your/destination/places.csv'

# Open a CSV file in write mode
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    # Create a CSV writer object
    csv_writer = csv.writer(csv_file)
    
    # Write the header row (optional, adjust according to your data)
    csv_writer.writerow(['Place', 'Rating', 'Reviews', 'Service options'])
    
    # Write the extracted data
    for i, title in enumerate(titles):
        title = title.get('aria-label')
        rating = (ratings[i].text + "/5") if i < len(ratings) else 'N/A' # Ensure we have a rating and reviews for each title, defaulting to 'N/A' if not found
        review_count = reviews[i].text if i < len(reviews) else 'N/A'
        service = services[i].text if i < len(services) else 'N/A'

        # Write a row to the CSV file
        if title:
            csv_writer.writerow([title, rating, review_count, service])

print(f"Data has been saved to '{csv_file_path}'")

# Close the WebDriver
driver.quit()

# %%
pip install blinker==1.5

# %%
import pandas as pd
import re

input_csv = 'marble_boston_personal.csv'
output_csv = 'marble_boston_data.csv'
df = pd.read_csv(input_csv)
df.columns = df.columns.str.lower()

print("Columns in DataFrame:", df.columns.tolist())  # Debugging line

def clean_and_format_phone(phone):
    if isinstance(phone, str):
        digits = re.sub(r'\D', '', phone)
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else ''
    return ''

if 'telephone' in df.columns:
    df['telephone'] = df['telephone'].apply(clean_and_format_phone)
else:
    print("Column 'telephone' not found in the DataFrame.")

df['categories'] = 'granite & marble'
df['address'] = df['address'].str.replace('Estados Unidos', 'United States')
df['website'] = df['website'].replace('https://www.google.com', '')
df.to_csv(output_csv, index=False)

# %%
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Selenium WebDriver with ChromeDriverManager
def setup_driver():
    options = Options()
    options.headless = False  # Keep headless mode off to see the browser (set to True for headless)
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Initialize WebDriver using ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

# Function to check if the URL is a valid company website (ends with .com, .org, etc.)
def is_valid_company_url(url):
    invalid_keywords = ["google.com", "facebook.com", "yelp.com", "linkedin.com", "twitter.com", "maps.google.com"]
    
    if any(keyword in url for keyword in invalid_keywords):
        return False
    if url.endswith(".com") or url.endswith(".org") or url.endswith(".net") or url.endswith(".biz"):
        return True
    return False

# Function to scrape companies using Google search for a specific niche and location
def google_search_companies(driver, niche, location):
    search_query = f"{niche} companies in {location}"
    
    # Navigate to Google
    driver.get("https://www.google.com/")
    
    # Wait for the Google search bar to load and enter the query
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "q")))
    
    search_input = driver.find_element(By.NAME, "q")
    search_input.send_keys(search_query)
    search_input.send_keys(Keys.RETURN)
    
    # Wait for the search results to load
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.g")))
    
    company_list = []
    
    try:
        result_elements = driver.find_elements(By.CSS_SELECTOR, "div.g")  # Each search result block
        
        for result in result_elements:
            try:
                url = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                
                # Check if the URL is a valid company website
                if is_valid_company_url(url):
                    company_list.append({
                        'URL': url
                    })
                    
            except Exception as e:
                print(f"Error extracting URL: {e}")
                continue
    
    except Exception as e:
        print(f"Error during scraping: {e}")
    
    return company_list

# Save the data to CSV
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Main function to run the scraper
def main():
    driver = setup_driver()
    
    niche = "technology"  # Example niche
    location = "Boston"   # Example location
    
    # Perform the Google search
    company_data = google_search_companies(driver, niche, location)
    
    if company_data:
        # Save to CSV
        save_to_csv(company_data, f"company_websites_{niche}_{location}.csv")
    else:
        print("No company websites found.")
    
    driver.quit()

# Run the script
if __name__ == "__main__":
    main()


# %%
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import re

# Chrome options for headless browsing
chrome_options = Options()
chrome_options.add_argument("--headless")  # Comment this line for debugging
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def search_google(company_name):
    driver.get("https://www.google.com")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(company_name)
    search_box.send_keys(Keys.RETURN)

    try:
        # Wait until the search results are loaded
        website_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'http')]"))
        )
        return website_link.get_attribute("href")
    except Exception as e:
        print(f"Error finding website link: {e}")
        return None

def extract_contact_info(url):
    contact_info = {'phone': None, 'email': None, 'owner': None}
    driver.get(url)

    try:
        # Wait for the page to load and content to be available
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract phone number using regex
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', soup.text)
        contact_info['phone'] = phone_match.group(0) if phone_match else None

        # Extract email using regex
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', soup.text)
        contact_info['email'] = email_match.group(0) if email_match else None

        # Extract owner/CEO name by looking for keywords
        owner = soup.find(text=re.compile(r'Owner|CEO|Founder', re.I))
        contact_info['owner'] = owner.strip() if owner else "N/A"

    except Exception as e:
        print(f"Error extracting contact info: {e}")

    return contact_info

def save_to_csv(data, filename='company_data.csv'):
    keys = data[0].keys()
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    company_name = input("Enter the company name: ")
    website_url = search_google(company_name)
    
    if website_url:
        contact_info = extract_contact_info(website_url)
        contact_info['website_url'] = website_url
        save_to_csv([contact_info])
        print("Data saved to CSV.")
    else:
        print("Failed to find the company's website.")

if __name__ == "__main__":
    main()

driver.quit()




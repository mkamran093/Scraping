import requests
import csv
import urllib.parse
from bs4 import BeautifulSoup

myUrl = 'https://aibd.org/directory/?ps&pn=2&limit=985'
token = "8247653dd3414734b941cd603bbb3cfe834eed3fa8d"
target_url = urllib.parse.quote(myUrl)
url = "http://api.scrape.do?token={}&url={}".format(token, target_url)



data_list = []

while True:
    response = requests.request("GET", url)
    if response.status_code == 403:
        print("Sleeping for 1")
    else:
        break

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    directory_container = soup.find('div', class_='pmpro_member_directory pmpro_member_directory-3col')

    member_items = directory_container.find_all('div', class_="pmpro_member_directory-item")
    
    for member in member_items:
        level = member.find('p', class_='pmpro_member_directory_level')
        level = level.get_text(strip=True).split(':')[-1].strip() if level else "-"

        first_name = member.find('p', class_='pmpro_member_directory_first_name')
        first_name = first_name.get_text(strip=True).split(':')[-1].strip() if first_name else "-"

        last_name = member.find('p', class_='pmpro_member_directory_last_name')
        last_name = last_name.get_text(strip=True).split(':')[-1].strip() if last_name else "-"

        city = member.find('p', class_='pmpro_member_directory_pmpro_scity')
        city = city.get_text(strip=True).split(':')[-1].strip() if city else "-"

        state = member.find('p', class_='pmpro_member_directory_pmpro_sstate')
        state = state.get_text(strip=True).split(':')[-1].strip() if state else "-"

        zip_code = member.find('p', class_='pmpro_member_directory_pmpro_szipcode')
        zip_code = zip_code.get_text(strip=True).split(':')[-1].strip() if zip_code else "-"

        designations = member.find('p', class_='pmpro_member_directory_professional_designations')
        designations = designations.get_text(strip=True).split(':')[-1].strip() if designations else "-"

        certification_no = member.find('p', class_='pmpro_member_directory_certificate_number')
        certification_no = certification_no.get_text(strip=True).split(':')[-1].strip() if certification_no else "-"

        certification_expires = member.find('p', class_='pmpro_member_directory_expiration_date')
        certification_expires = certification_expires.get_text(strip=True).split(':')[-1].strip() if certification_expires else "-"

        email = "-"
        profile_link = "https://aibd.org/profile/" + first_name.lower() + "-" + last_name.lower()

        try:
            target_url = urllib.parse.quote(profile_link)
            url = "http://api.scrape.do?token={}&url={}".format(token, target_url)

            profile_response = requests.request("GET", url)
            profile_soup = BeautifulSoup(profile_response.content, 'html.parser')
            
            email_tag = profile_soup.find('p', class_='pmpro_member_directory_email')
            if email_tag:
                email_link = email_tag.find('a', href=True)
                if email_link:
                    email = email_link.get_text(strip=True)
        except Exception as e:
            print(f"Failed to fetch email from {profile_link}: {e}")

        data_list.append([level, first_name, last_name, city, state, zip_code, designations, certification_no, certification_expires, email])

        csv_filename = 'members_directory2.csv'
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(['Level', 'First Name', 'Last Name', 'City', 'State', 'Zip Code', 'Designations', 'Certification No.', 'Certification Expires On', 'Email Address'])
            # Write the data rows
            writer.writerows(data_list)
    
else:
    print(f"Failed to retrieve content. Status code: {response.status_code}")

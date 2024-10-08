# from xxlimited import foo
import requests
from bs4 import BeautifulSoup
import csv

def scrape(url):

    logo = ''
    pdf = []
    # visit the site
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # remove head and script tags
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style", "head"]):
                script.extract()
            # extract all a and img tags
            img_tags = soup.find_all('img')
            a_tags = soup.find_all('a')
            
            # find logo links
            for tag in img_tags:
                if tag['src'].endswith('.png') or tag['src'].endswith('.jpg') or tag['src'].endswith('.jpeg') or tag['src'].endswith('.svg'):
                    logo = tag['src']
                    if 'http' not in logo:
                        logo = url + logo
                    break
            
            # find pdf links
            for a in a_tags:
                if a['href'].endswith('.pdf'):
                    if 'http' not in a['href']:
                        pdf.append(url + a['href'])
                    else:
                        pdf.append(a['href'])

            pdf = ', '.join(pdf)
            print('data extracted')
            return logo, pdf
        else:
            print('No data found')
            return '-', '-'
    except:
        print('An error occured')
        return '-', '-'
    

def main():

    # extract rows from excel file
    with open('Medicine Data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[4] != '-':
                continue
            url = row[3]
        
            # print(scrape(url))
            # process data
            logo, pdf = scrape(url)

            # write data to output
            row[4] = logo
            row[5] = pdf

            quoted_row = ','.join(f'"{item}"' for item in row)
            with open('Medicine Data - updated.csv', 'a') as file:
                file.write(quoted_row + '\n')
            print('row updated')
   

if __name__ == "__main__":
    main()
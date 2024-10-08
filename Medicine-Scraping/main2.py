from requests_html import HTMLSession
from bs4 import BeautifulSoup
import openai
import csv

openai.api_key = 'sk-xoXuSP9bwDs8g8EmCrRC2odmwPxNXoQ1Vo38RVKHKOT3BlbkFJJIFPRUu7ZX0C6SN1TZhyMc0d5qwwOhMNo9K-MQX60A'
def scrape(url):

    logo = ''
    pdf = []
    # visit the site
    try:
        s = HTMLSession()
        response = s.get(url)
        if response:
            # remove head and script tags
            soup = BeautifulSoup(response.text, 'html.parser')
            # extract all a and img tags
            img_tags = soup.find_all('img')
            a_tags = soup.find_all('a')

            prompt = str(img_tags) + str(a_tags)
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. You will be given html tags in string format, you will find url of the first image and all pdf links in the html tags. Give your response in this format: 'logo_url, pdf_url1, pdf_url2, ...', if url is not found, use '-' instead."},
                    {"role": "user", "content": prompt}
                ]
            )
            links = response.choices[0].message.content.strip().split(', ')
            logo = links[0]
            pdf = links[1:]

            # find logo links
            logo = img_tags[0]['src']
            if 'http' not in logo:
                logo = url + logo
            
            # find pdf links
            for link in links:
                if 'http' not in link:
                    link = url + link
                
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
    with open('Medicine Data.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        i = 0
        for row in reader:
            if i < 482:
                i += 1
                continue
            try:
                if (row[4] == '-' or row[4] == '') and (row[5] == '-' or row[5] == ''):
                    print('empty row founded')
                    url = row[3]
            
                    # process data
                    logo, pdf = scrape(url)

                    # write data to output
                    if row[4] == '-' or row[4] == '':
                        row[4] = logo
                    if row[5] == '-' or row[5] == '':
                        row[5] = pdf

                quoted_row = ','.join(f'"{item}"' for item in row)
                try:
                    with open('Medicine Data - updated.csv', 'a', encoding='utf-8') as file:
                        file.write(quoted_row + '\n')
                    print('row updated\n\n')
                except:
                    raise Exception('An error occured while writing to file')
            except:
                with open('Medicine Data - updated.csv', 'a', encoding='utf-8') as file:
                    file.write(','.join(f'"{item}"' for item in row) + '\n')
   

if __name__ == "__main__":
    main()
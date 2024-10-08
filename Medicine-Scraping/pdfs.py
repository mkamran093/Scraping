import os
import requests
import csv

def main():

    with open('Medicine Data.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        files = os.listdir('PDFs')
        for row in reader:
            if row[5] == '-':
                continue

            for index, url in enumerate(row[5].split(', ')):
                if url == '-' or 'the response is: ' in url:
                    continue
                if 'http' not in url:
                    url = row[3] + url
                
                name = row[0].replace(' ', '_') + f'_{index}.pdf'
                if name in files:
                    print(f'{name} already exists')
                    continue
                try:
                    pdf_data = requests.get(url).content
                    if not os.path.exists('PDFs'):
                        os.makedirs('PDFs')

                    full_path = os.path.join('PDFs', name)

                    with open(full_path, 'wb') as file:
                        file.write(pdf_data)
                except Exception as e:
                    print(e)
                    continue

if __name__ == '__main__':
    main()  
import os
import requests
import csv


def main():

    current_logos = os.listdir('Logos')
    with open('Medicine Data.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if 'http' not in row[4]:
                continue
            url = row[4]
            name = row[0].replace(' ', '_') + url[url.rfind('.'):]
            if name in current_logos:
                print(f'{name} already exists')
                continue

            try:
                image_data = requests.get(url).content
                if not os.path.exists('Logos'):
                    os.makedirs('Logos')

                full_path = os.path.join('Logos', name)

                with open(full_path, 'wb') as file:
                    file.write(image_data)
            except Exception as e:
                print(e)
                continue

if __name__ == '__main__':
    main()  
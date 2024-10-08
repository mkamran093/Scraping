from svg2png import svg2png
import os

directory = 'C:/Users/NeXbit/Desktop/Scraping/Medicine-Scraping/Logos copy'

for file in os.listdir(directory):
    name = file[:file.rfind('.')] + '.png'
    if file.endswith('.svg'):
        file_path = os.path.join(directory, name)
        with open(file_path, 'wb') as file:
            pass
        svg2png(file_path)
        os.remove(file)

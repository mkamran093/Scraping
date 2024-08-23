from constants import ZYTE_API_URL, ZYTE_API_KEY
from bs4 import BeautifulSoup
from base64 import b64decode
import requests
import logging
import json
import csv
import re
import os

url = 'https://www.wayfair.co.uk/furniture/pdp/yaheetech-reversible-sleeper-corner-sofa-bed-u003278242.html?piid=340601429'
api_response = requests.post(
    ZYTE_API_URL,
    auth=(ZYTE_API_KEY, ""),   
    json={
        "url": url,
        "httpResponseBody": True,
    },
)

if api_response.status_code == 200:
    http_response_body = b64decode(api_response.json()["httpResponseBody"])
    soup = BeautifulSoup(http_response_body, 'html.parser')

    img_section = soup.find('div', class_='ProductDetailImageCarousel-thumbnails ProductDetailImageCarousel-thumbnails--halfColumnWidthCarousel')
    urls = []
    for li in img_section.find_all('li'):
        urls.append(li.find('img')['src'])
    
    img_urls = []
    for url in urls:
        new_url = url.replace('resize-h56-w56%5Ecompr-r50', 'resize-h800-w800%5Ecompr-r85')
        img_urls.append(new_url)

    print(img_urls)
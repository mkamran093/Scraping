from scrape import start_scraping

categories_url = {
    "1": "https://www.wayfair.co.uk/furniture/cat/furniture-c1852173.html", 
    "2": "https://www.wayfair.co.uk/garden/cat/outdoor-c476621.html",
    "3": "https://www.wayfair.co.uk/lighting/cat/lighting-c234985.html", 
    "4": "https://www.wayfair.co.uk/home-decor/cat/home-decor-c225067.html", 
    "5": "https://www.wayfair.co.uk/textiles-bedding/cat/textiles-bedding-c1852180.html", 
    "6": "https://www.wayfair.co.uk/rugs/cat/rugs-c476861.html", 
    "7": "https://www.wayfair.co.uk/kitchenware-tableware/cat/kitchenware-tableware-c1804587.html", 
    "8": "https://www.wayfair.co.uk/storage-organisation/cat/storage-organisation-c1792693.html", 
    "9": "https://www.wayfair.co.uk/children-nursery/cat/children-nursery-c476620.html", 
    "10": "https://www.wayfair.co.uk/home-improvement/cat/home-improvement-c1834253.html", 
    "11": "https://www.wayfair.co.uk/pets/cat/pets-c477714.html", 
    "12": "https://www.wayfair.co.uk/holiday-decor/cat/holiday-decor-c1863206.html", 
    "13": "https://www.wayfair.co.uk/shop-by-room/cat/shop-by-room-c1862441.html"
}

def main():
    print("Welcome to Wayfair Scraper!\n")
    print(" 1. Furniture          2. Outdoor              3. Lighting\n"
          " 4. Decor              5. Textiles & Bedding   6. Rugs\n"
          " 7. Kitchen            8. Storage              9. Baby & Kids\n"
          "10. Home Improvement  11. Pet                 12. Holiday\n"
          "13. Shop by Room")

    category = input("\nEnter number of the corresponding category to scrape: ")

    while True:
        if category in categories_url:
            break
        else:
            category = input("Invalid input. Please enter a valid number.")
    url = categories_url[category]
    print(f"Scraping {url}...\n")
    start_scraping(url)

if __name__ == "__main__":
    main()

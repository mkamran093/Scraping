from igc_scraper import IGCScraper
from pwg_scraper import PWGScraper
from pilkington_scraper import PilkingtonScraper

def main():

    part_number = input("Enter the part number: ")
    print("Wait while we search for the part number: ", part_number)

    # IGC Scraper
    pwg_data = PWGScraper(part_number)
    igc_data = IGCScraper(part_number)
    pilkington_data = PilkingtonScraper(part_number)

    print("\nPart Data From PWG\n")
    print(pwg_data)
    print("\n")
    print("Part Data From IGC\n")
    print(igc_data)
    print("\n")
    print("Part Data From Pilkington\n")
    print(pilkington_data)
    print("\n")

if __name__ == "__main__":
    main()
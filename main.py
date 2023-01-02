from scripts.scraper import scrape
from scripts.toShopify import convert

def main(shop_url, vendor_name):
    raw_data = scrape(shop_url)
    print(raw_data)
    shopify_data = convert(raw_data, vendor)
    print(shopify_data)
    

if __name__ == '__main__':
    url = str(input('Enter Etsy Shop URL: '))
    vendor = str(input('Enter Shopify Store Name: '))
    main(url, vendor)
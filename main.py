from scripts.scraper import scrape
from scripts.toShopify import convert


def main(shop_url, vendor_name):
    """
    Scrape data from an Etsy shop and convert it to a format that is compatible with Shopify.
    
    Parameters:
    shop_url (str): The URL of the Etsy shop to scrape.
    vendor_name (str): The name of the vendor whose products are being scraped.
    
    Returns:
    None
    """
    print("Product scrapping in progress...")
    raw_data = scrape(shop_url)
    print("Converting data to Shopify format...")
    shopify_data = convert(raw_data, vendor)
    print(f"Done! Check {shopify_data} to get your csv file.")
    return None
    
if __name__ == '__main__':
    url = str(input('Enter Etsy Shop URL: '))
    vendor = str(input('Enter Shopify Store Name: '))
    print("############################################")
    main(url, vendor)
from http.client import HTTPException
from bs4 import BeautifulSoup
import requests
import time
import csv
import re


def get_title(soup):
        title = soup.select('#listing-page-cart > div.wt-mb-xs-2 > h1')  
        return title[0].text.strip()

def get_price(soup):
        price = soup.select('#listing-page-cart > div.wt-mb-xs-6.wt-mb-lg-0 > div:nth-child(1) > div.wt-mb-xs-3 > div.wt-mb-xs-3 > div > div.wt-display-flex-xs.wt-align-items-center.wt-justify-content-space-between > div.wt-display-flex-xs.wt-align-items-center.wt-flex-wrap > p')
        price = price[0].text.strip()
        price = ''.join([i for i in price if i in '.0123456789'])
        return price.strip()

def get_desc(soup):
        desc = soup.select('#wt-content-toggle-product-details-read-more > p')
        desc = '\n'.join(list([ i.text for i in desc]))
        desc = desc.replace('BYesil', 'Luxlushy')
        desc = desc.replace('www.byyesil.com', 'www.Luxlushy.com')
        # Clean from all links / URLs
        desc = re.sub(r'^https?:\/\/.*[\r\n]*', '', desc, flags=re.MULTILINE)
        return desc.strip()

def get_images(soup):
        images = soup.select('#listing-right-column > div > div.body-wrap.wt-body-max-width.wt-display-flex-md.wt-flex-direction-column-xs > div.image-col.wt-order-xs-1.wt-mb-lg-6 > div > div > div > div > div.image-carousel-container.wt-position-relative.wt-flex-xs-6.wt-order-xs-2.show-scrollable-thumbnails > ul > li > img')
        URLs = [ img.get('src') if img.get('src') else img.get('data-src') for img in images]
        return URLs

def get_soup(url):
        try:
                # driver.get(url)
                res = requests.get(url)
                soup = BeautifulSoup(res.content, 'html.parser')
        except HTTPException as e:
                print(e)
                soup = None   
        return soup # .encode("utf-8")

def get_products(soup, products):
    listingPage = soup.find_all("a", {"class": "listing-link"})
    try:
        for i, product in enumerate(listingPage):
                print(f'Scraping the {i+1}th product...')
                URL = product['href']
                soup = get_soup(URL)
                data = {
                        'title': get_title(soup),
                        'price': get_price(soup),
                        'desc': get_desc(soup),
                        'images': get_images(soup)
                }
                products.append(data)
                print(f'The {i+1}th product done successfully!!')
    except HTTPException as e:
        print(e)
        pass
    return products, len(products) 

def scrapeShop(url):
        products = list()
        print(f"############ Scrapping {url.split('/')[3]} ############")
        x = 1
        while x < 3:
                soup = get_soup(f'{url}?page={x}')
                time.sleep(3)
                if not soup:
                        pass
                else:
                        products, j = get_products(soup, products)

                        if j == 0:
                                break
                        else:
                                print(f"{x}th page done...")
                                x += 1
        return products

def main(URL):
        shop = URL.split('/')[4]
        products = scrapeShop(URL)
        keys = products[0].keys()
        a_file = open(f"raw_products{shop}.csv", "w", encoding='utf-8')
        dict_writer = csv.DictWriter(a_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(products)
        a_file.close()

if __name__ == '__main__':
        url = "https://www.etsy.com/shop/byyesil/?section_id=1"
        main(url)

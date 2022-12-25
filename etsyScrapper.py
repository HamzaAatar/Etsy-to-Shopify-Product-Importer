from http.client import HTTPException
from bs4 import BeautifulSoup
import requests
import csv


def get_title(soup) -> str:
        title = soup.select('#listing-page-cart > div.wt-mb-xs-2 > h1')  
        return title[0].text.strip()

def get_price(soup) -> str:
        price = soup.select('#listing-page-cart > div.wt-mb-xs-6.wt-mb-lg-0 > div:nth-child(1) > div.wt-mb-xs-3 > div.wt-mb-xs-3 > div > div.wt-display-flex-xs.wt-align-items-center.wt-justify-content-space-between > div.wt-display-flex-xs.wt-align-items-center.wt-flex-wrap > p')
        price = price[0].text.strip()
        price = ''.join([i for i in price if i in '.0123456789'])
        return price.strip()

def get_desc(soup) -> str:
        desc = soup.select('#wt-content-toggle-product-details-read-more > p')
        desc = '\n'.join(list([ i.text for i in desc]))

        return desc.strip()

def get_images(soup) -> list:
        images = soup.select('#listing-right-column > div > div.body-wrap.wt-body-max-width.wt-display-flex-md.wt-flex-direction-column-xs > div.image-col.wt-order-xs-1.wt-mb-lg-6 > div > div > div > div > div.image-carousel-container.wt-position-relative.wt-flex-xs-6.wt-order-xs-2.show-scrollable-thumbnails > ul > li > img')
        URLs = [ img.get('src') if img.get('src') else img.get('data-src') for img in images]
        return URLs

def get_number_of_pages(soup) -> int:
        pages = soup.select('#content > div.shop-home > div.wt-body-max-width.wt-pr-xs-2.wt-pr-md-4.wt-pl-xs-2.wt-pl-md-4 > div:nth-child(2) > span > div.wt-display-flex-lg > div.wt-pr-xs-0.wt-pl-xs-0.shop-home-wider-items.wt-pb-xs-5 > div.wt-animated > div.wt-text-center-xs > div.wt-show-md.wt-hide-lg > nav > ul > li > a > span:nth-child(2)')

        return max(map(lambda x: int(x.text.strip()), pages[1:-1]))

def get_soup(url) -> BeautifulSoup:
        try:
                res = requests.get(url)
                soup = BeautifulSoup(res.content, 'html.parser')
        except HTTPException as e:
                print(e)
                soup = None   
        return soup # .encode("utf-8")

def get_product_data(URL) -> dict:
        try:
                soup = get_soup(URL)
                data = {
                        'title': get_title(soup),
                        'price': get_price(soup),
                        'desc': get_desc(soup),
                        'images': get_images(soup)
                }
        except HTTPException as e:
                print(e)
                pass
        return data

def get_product_links(soup) -> list[str]:
        listingPage = soup.select('#content > div.shop-home > div.wt-body-max-width.wt-pr-xs-2.wt-pr-md-4.wt-pl-xs-2.wt-pl-md-4 > div:nth-child(2) > span > div.wt-display-flex-lg > div.wt-pr-xs-0.wt-pl-xs-0.shop-home-wider-items.wt-pb-xs-5 > div.wt-animated > div:nth-child(4) > div > div > div > a')
        return [product['href'] for product in listingPage]

def scrapeShop(url) -> list[dict]:
        products = []
        print(f"############ Scrapping {url.split('/')[3]} ############")
        print("############ Getting Links from 1st page ############")
        soup = get_soup(f'{url}?page=1')
        product_URLS = get_product_links(soup)
        pages = get_number_of_pages(soup)
        if pages > 1:
                for page in range(2, pages + 1):
                        print(f"############ Getting Links from {page}th page ############")
                        soup = get_soup(f'{url}?page={page}')
                        product_URLS += get_product_links(soup)
        for URL in product_URLS:
                print(f'Scraping product number: {len(products) + 1}...')
                products.append(get_product_data(URL))
                print(f'Product number: {len(products)} scrapped Successfully!!')
                                
        return products

def main(URL) -> None:
        shop = URL.split('/')[4].split('?')[0]
        URL = f"https://www.etsy.com/shop/{shop}"
        products = scrapeShop(URL)
        keys = products[0].keys()
        with open(f"./CSV/raw_products_{shop}.csv", "w", encoding='utf-8', newline='') as a_file:
                dict_writer = csv.DictWriter(a_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(products)

if __name__ == '__main__':
        url = "https://www.etsy.com/shop/PetajaFiberWorks"
        main(url)
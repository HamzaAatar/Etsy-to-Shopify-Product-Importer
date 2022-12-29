from http.client import HTTPException
from bs4 import BeautifulSoup
import requests
import csv
import asyncio
from httpx import AsyncClient
import time
from concurrent.futures import ProcessPoolExecutor
import os
from functools import reduce


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

def get_number_of_pages(html) -> int:
        soup = BeautifulSoup(html, "html.parser")
        pages = soup.select('#content > div.shop-home > div.wt-body-max-width.wt-pr-xs-2.wt-pr-md-4.wt-pl-xs-2.wt-pl-md-4 > div:nth-child(2) > span > div.wt-display-flex-lg > div.wt-pr-xs-0.wt-pl-xs-0.shop-home-wider-items.wt-pb-xs-5 > div.wt-animated > div.wt-text-center-xs > div.wt-show-md.wt-hide-lg > nav > ul > li > a > span:nth-child(2)')

        return max(map(lambda x: int(x.text.strip()), pages[1:-1]))

def get_soup(url) -> BeautifulSoup:
        try:
                res = requests.get(url)
        except HTTPException as e:
                print(e)
        return res.content # .encode("utf-8")

async def get_html_async(URL, session, throttler=None):
        if throttler:
                async with throttler:
                        try:
                                res = await session.get(URL)
                        except HTTPException as e:
                                print(e)
                                return None
        else:
                try:
                        res = await session.get(URL)
                except HTTPException as e:
                        print(e)
                        return None
        return res.content

def get_product_data(html) -> dict:
        try:
                soup = BeautifulSoup(html, 'html.parser')
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

def get_product_links(html) -> list[str]:
        soup = BeautifulSoup(html, 'html.parser')
        listingPage = soup.select('#content > div.shop-home > div.wt-body-max-width.wt-pr-xs-2.wt-pr-md-4.wt-pl-xs-2.wt-pl-md-4 > div:nth-child(2) > span > div.wt-display-flex-lg > div.wt-pr-xs-0.wt-pl-xs-0.shop-home-wider-items.wt-pb-xs-5 > div.wt-animated > div:nth-child(4) > div > div > div > a')
        return [product['href'] for product in listingPage]

async def run(url):
        _start = time.time()
        html = get_soup(url + "")
        links = get_product_links(html)
        pages = get_number_of_pages(html)
        throttler = asyncio.Semaphore(os.cpu_count() + 4)
        async with AsyncClient() as session:
                tasks, html = [], []
                for page in range(2, pages + 1):
                        tasks.append(get_html_async(f'{url}?page={page}', session=session, throttler=throttler))
                htmls = await asyncio.gather(*tasks)

                with ProcessPoolExecutor(max_workers= os.cpu_count()) as ex:
                        futures = [ex.submit(get_product_links, html) for html in htmls]
                        links.extend(reduce(lambda x, y: x + y, [future.result() for future in futures]))
                tasks, html = [], []
                for link in links:
                        tasks.append(get_html_async(link, session=session, throttler=throttler))
                htmls = await asyncio.gather(*tasks)

        with ProcessPoolExecutor(max_workers= os.cpu_count()) as ex:
                futures = [ex.submit(get_product_data, html) for html in htmls]
                products = [future.result() for future in futures]
        print(f"finished scraping in: {time.time() - _start:.1f} seconds")
        return products

async def main(URL) -> None:
        shop = URL.split('/')[4].split('?')[0]
        URL = f"https://www.etsy.com/shop/{shop}"
        products = await run(URL)
        keys = products[0].keys()
        with open(f"./CSV/raw_products_{shop}.csv", "w", encoding='utf-8', newline='') as a_file:
                dict_writer = csv.DictWriter(a_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(products)

if __name__ == '__main__':
        url = "https://www.etsy.com/shop/byyesil?ref=simple-shop-header-name&listing_id=1277737721"
        asyncio.run(main(url))

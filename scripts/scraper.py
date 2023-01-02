import asyncio
import csv
import os
import time
from concurrent.futures import ProcessPoolExecutor
from functools import reduce
from http.client import HTTPException

from httpx import AsyncClient

from .utils import get_number_of_pages, get_product_data, get_product_links


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

async def run(url):
    throttler = asyncio.Semaphore(os.cpu_count() + 4)
    async with AsyncClient() as session:
        print("Gathering Product links...")
        html = await get_html_async(url, session=session)
        links = get_product_links(html)
        pages = get_number_of_pages(html)

        tasks, html = [], []
        for page in range(2, pages + 1):
            tasks.append(get_html_async(f'{url}?page={page}', session=session, throttler=throttler))

        htmls = await asyncio.gather(*tasks)
        with ProcessPoolExecutor(max_workers= os.cpu_count()) as ex:
            futures = [ex.submit(get_product_links, html) for html in htmls]
            links.extend(reduce(lambda x, y: x + y, [future.result() for future in futures]))

        print("Scraping Product listings...")
        tasks, html = [], []
        for link in links:
            tasks.append(get_html_async(link, session=session, throttler=throttler))
        htmls = await asyncio.gather(*tasks)

    print("Parsing Product data...")
    with ProcessPoolExecutor(max_workers= os.cpu_count()) as ex:
        futures = [ex.submit(get_product_data, html) for html in htmls]
        products = [future.result() for future in futures]

    return products

async def main(URL) -> None:
    shop = URL.split('/')[4].split('?')[0]
    URL = f"https://www.etsy.com/shop/{shop}"
    products = await run(URL)
    keys = products[0].keys()
    with open(f"./data/raw/raw_products_{shop}.csv", "w", encoding='utf-8', newline='') as a_file:
        dict_writer = csv.DictWriter(a_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(products)
    
    return f"./data/raw/raw_products_{shop}.csv"

def scrape(URL):
    return asyncio.run(main(URL))

if __name__ == '__main__':
    url = str(input('Enter Etsy Shop URL: '))
    scrape(url)

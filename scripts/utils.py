from bs4 import BeautifulSoup


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

def get_product_data(html) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    data = {
        'title': get_title(soup),
        'price': get_price(soup),
        'desc': get_desc(soup),
        'images': get_images(soup)
    }
    return data

def get_product_links(html) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')
    listingPage = soup.select('#content > div.shop-home > div.wt-body-max-width.wt-pr-xs-2.wt-pr-md-4.wt-pl-xs-2.wt-pl-md-4 > div:nth-child(2) > span > div.wt-display-flex-lg > div.wt-pr-xs-0.wt-pl-xs-0.shop-home-wider-items.wt-pb-xs-5 > div.wt-animated > div:nth-child(4) > div > div > div > a')
    return [product['href'] for product in listingPage]
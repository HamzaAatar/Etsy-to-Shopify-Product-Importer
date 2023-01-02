from copy import copy
import csv


header = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Standardized Product Type', 'Custom Product Type', 'Tags', 'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description', 'Google Shopping / Google Product Category', 'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / AdWords Grouping', 'Google Shopping / AdWords Labels', 'Google Shopping / Condition', 'Google Shopping / Custom Product', 'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1', 'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3', 'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code', 'Cost per item', 'Status']
values = ['']*49
template = dict(zip(header, values))
products = list()

def main(filename, vendor):
    with open(filename, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        counter = 1
        for row in csv_reader:
            temp = copy(template)
            handle = row['title'].replace(' ', '-').strip()
            handle = handle.replace('|', '').strip()
            temp['Handle'] = handle
            temp['Title'] = row['title']
            temp['Body (HTML)'] = row['desc']
            temp['Vendor'] = vendor
            temp['Standardized Product Type'] = '' # FIXED
            temp['Custom Product Type'] = '' # FIXED
            temp['Published'] = 'TRUE'
            temp['Variant SKU'] = f'T-L{counter:06}'
            temp['Variant Inventory Tracker'] = 'shopify'
            temp['Variant Inventory Qty'] = '1'
            temp['Variant Inventory Policy'] = 'deny'
            temp['Variant Fulfillment Service'] = 'manual'
            temp['Variant Price'] = row['price']
            temp['Variant Requires Shipping'] = 'TRUE'
            temp['Variant Taxable'] = 'TRUE'
            temp['Variant Barcode'] = temp['Variant SKU']
            temp['Image Src'] = row['images'].strip("]'[").split(', ')[0][:-1]
            temp['Image Position'] = '1'
            temp['Image Alt Text'] = handle
            temp['Gift Card'] = 'FALSE'
            temp['Status'] = 'draft'

            products.append(temp)
            for i, image in enumerate(row['images'].strip('][').split(', ')):
                if i == 0:
                    pass
                else:
                    temp_2 = copy(template)
                    temp_2['Handle'] = handle
                    temp_2['Image Src'] = image[1:-1]
                    temp_2['Image Position'] = i+1
                    temp_2['Image Alt Text'] = f"{handle}-{i+1}"
                    products.append(temp_2)
            counter += 1
    
    return products

def convert(filename, vendor):
    products = main(filename, vendor)
    keys = products[0].keys()
    with open(f"./data/processed/final_shopify_{vendor}.csv", "w", encoding='utf-8') as a_file:
        dict_writer = csv.DictWriter(a_file, keys, lineterminator = '\n', quotechar='"')
        dict_writer.writeheader()
        dict_writer.writerows(products)
    
    return f"./data/processed/final_shopify_{vendor}.csv"

if __name__ == '__main__':
    filename = str(input('Enter path to raw data: '))
    vendor = str(input('Enter Shopify Store Name: '))
    convert(filename, vendor)
import csv
import logging
import re

import requests
from bs4 import BeautifulSoup as BS

logging.basicConfig(
    level=logging.INFO,
    filename='parse_akra-holding.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)


def parse():
    url = 'https://akra-holding.kz'
    #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}
    response = requests.get(url, timeout=1)
    soup = BS(response.text, 'lxml')
    url_list = []
    for i in range(21, 22):
        try:
            for j in range(4, 9):
                a = soup.select(f'div.dMenu__bl:nth-child({i}) > ul:nth-child(2) > li:nth-child({j}) > a:nth-child(1)')
                if a == []:
                    break
                url_1 = url + a[0]['href']
                r_1 = requests.get(url_1, timeout=3)
                soup_1 = BS(r_1.text, 'lxml')
                b = soup_1.select('div.s-products__item:nth-child(1) > div:nth-child(2) > div:nth-child(1) > a:nth-child(1)')
                if b == []:
                    for f in range(1, 14):
                        c = soup_1.select(f'a.s-categ__link:nth-child({f})')
                        if c == []:
                            break
                        url_list.append(url + c[0]['href'])
                else:
                    url_list.append(url_1)
        except Exception as e:
            logging.info(f'{e}')
    product, images, category, cat_2, cat_3, cat_last = [], [], [], [], [], []
    for i in url_list:
        try:
            for n in range(1, 51):
                url_2 = i + f'?page={n}'
                r_2 = requests.get(url_2, timeout=3)
                soup_2 = BS(r_2.text, 'lxml')
                if soup_2(string=re.compile('Не найдено ни одного товара.')) != []:
                    break
                cat_2 = soup_2.select('div.js-breadcrumbs-plugin__item-wrapper:nth-child(2) > a:nth-child(2) > span:nth-child(1)')
                cat_3 = soup_2.select('div.js-breadcrumbs-plugin__item-wrapper:nth-child(3) > a:nth-child(2) > span:nth-child(1)')
                cat_last = soup_2.select('span.breadcrumbs-plugin__item__label:nth-child(2)')
                for m in range(1, 31):
                    d = soup_2.select(f'div.s-products__item:nth-child({m}) > div:nth-child(2) > div:nth-child(1) > a:nth-child(1)')
                    if d == []:
                        break
                    value = d[0].text
                    e = soup_2.select(f'div.s-products__item:nth-child({m}) > div:nth-child(1) > div:nth-child(1) > a:nth-child(1) > img:nth-child(1)')
                    image = ''
                    if e != []:
                        image_lst = str(e[0]).split()
                        for y in image_lst:
                            if 'data-src' in y:
                                image = url + y[10:-1]
                    images.append(image)
                    product.append(value)
                    if cat_2 != [] and cat_3 != [] and cat_last != []:
                        category.append(f'{cat_2[0].text[9:-8]}/{cat_3[0].text[9:-8]}/{cat_last[0].text[10:-9]}')
                    elif cat_2 != [] and cat_last != [] and cat_3 == []:
                        category.append(f'{cat_2[0].text[9:-8]}/{cat_last[0].text[10:-9]}')
                    else:
                        category.append('')
        except Exception as e:
            logging.info(f'{e}')
    g = open('akra-holding.csv', 'w', newline='')
    e = csv.writer(g)
    e.writerow(['Категория', 'Наименование и характеристики', 'Фото'])
    for i, j, z in zip(category, product, images):
        e.writerow([i, j, z])
    g.close()


if __name__ == '__main__':
    parse()

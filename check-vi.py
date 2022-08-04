from unittest.mock import DEFAULT
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from queue import Queue
import sys
import getopt

NAME_FILE = "default.txt"
BASE_PAGE = "/wiki/Thể_loại:Truyền_thông_đại_chúng"
LIMIT = 1000

opts, args = getopt.getopt(sys.argv[1:], "f:b:hl:")
for opt, arg in opts:
    if opt == '-f':
        NAME_FILE = arg
    elif opt == '-b':
        BASE_PAGE = arg
    elif opt == '-l':
        LIMIT = int(arg)
    elif opt == '-h':
        print("-f <file> -b <base page>")
        sys.exit(0)

q = Queue()

BASE_URL = "https://vi.wikipedia.org"
visited_url = set()

q.put(BASE_URL + BASE_PAGE)
list_valid_url = []

flags_continue = True

while not q.empty() and flags_continue:
    url = requests.get(q.get())
    visited_url.add(url)
    soup = BeautifulSoup(url.text, 'html.parser')

    pages = soup.select('div#mw-pages', href=True)

    if len(pages) > 0:
        list_pages = pages[0].select('ul > li > a', href=True)
        pbar = tqdm(list_pages)
        for page in pbar:
            web = requests.get(BASE_URL + str(page['href']))
            new_soup = BeautifulSoup(web.text, 'html.parser')

            if len(list_valid_url) >= LIMIT:
                flags_continue = False
                break

            list_valid_url.append(BASE_URL + str(page['href']))

            pbar.set_description(
                "url: %s, visited: %s" %
                (len(list_valid_url), len(visited_url)))

    subcategorys = soup.select('div#mw-subcategories', href=True)
    if len(subcategorys) > 0:
        list_subcategorys = subcategorys[0].select('a', href=True)
        for subcategory in list_subcategorys:
            if BASE_URL + str(subcategory['href']) not in visited_url:
                q.put(BASE_URL + str(subcategory['href']))

list_valid_url = ['"' + url + '",' for url in list_valid_url]
with open(NAME_FILE, 'w') as f:
    for url in list_valid_url:
        f.write(url + '\n')

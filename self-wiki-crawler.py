#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import argparse
import re
from urllib.parse import urlparse
from tqdm import tqdm

import requests
from bs4 import BeautifulSoup

DEFAULT_OUTPUT = 'output.txt'
DEFAULT_INTERVAL = 1.0  # interval between requests (seconds)

visited_urls = set()  # all urls already visited, to not visit twice
pending_urls = []


def load_urls(session_file):
    """Resume previous session if any, load visited URLs"""

    try:
        with open(session_file) as fin:
            for line in fin:
                visited_urls.add(line.strip())
    except FileNotFoundError:
        pass


def scrap(base_url, output_file, session_file):
    """Represents one request per article"""

    full_url = base_url
    try:
        r = requests.get(full_url)
    except requests.exceptions.ConnectionError:
        print("Check your Internet connection")
        input("Press [ENTER] to continue to the next request.")
        return
    if r.status_code not in (200, 404):
        print("Failed to request page (code {})".format(r.status_code))
        input("Press [ENTER] to continue to the next request.")
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.find('div', {'id': 'mw-content-text'})

    with open(session_file, 'a') as fout:
        fout.write(full_url + '\n')  # log URL to session file

    # skip if already added text from this article, as continuing session
    if full_url in visited_urls:
        return
    visited_urls.add(full_url)

    # to remove parenthesis content
    parenthesis_regex = re.compile('\\(.+?\\)')
    citations_regex = re.compile('\\[.+?\\]')  # to remove citations, e.g. [1]

    # get plain text from each <p>
    p_list = content.find_all('p')
    with open(output_file, 'a', encoding='utf-8') as fout:
        for p in p_list:
            text = p.get_text().strip()
            text = parenthesis_regex.sub('', text)
            text = citations_regex.sub('', text)
            if text:
                fout.write(text + '\n\n')  # extra line between paragraphs


def main(interval, output_file):
    """ Main loop, single thread """

    print("\t(Press CTRL+C to pause)\n")
    session_file = "session_" + output_file
    load_urls(session_file)  # load previous session (if any)

    for url in tqdm(pending_urls):
        try:
            scrap(url, output_file, session_file)
            time.sleep(interval)
        except KeyboardInterrupt:
            input("\n> PAUSED. Press [ENTER] to continue...\n")

    print("Finished!")
    sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-in",
        "--input",
        nargs='?',
        type=str,
        help="File input")
    parser.add_argument(
        "-i",
        "--interval",
        nargs='?',
        default=DEFAULT_INTERVAL,
        type=float,
        help="Interval between requests")
    parser.add_argument(
        "-o",
        "--output",
        nargs='?',
        default=DEFAULT_OUTPUT,
        help="File output")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as fin:
        pending_urls = fin.readlines()
        pending_urls = [url[1:len(url) - 3] for url in pending_urls]

    main(args.interval, args.output)

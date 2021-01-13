import logging
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import json

from bs4 import BeautifulSoup
import requests

from django.db import connection

from .enums import TITLE_TYPES, DETAIL_BLOCKS, BASE_URL


logger = logging.getLogger('django')


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator()


def run_thread_pool():
    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            func = yield
            executor.submit(func)


pool_wrapper = run_thread_pool()
next(pool_wrapper)


class DataExtractor:
    def __init__(self, url_from_args, task_instance):
        self.task_instance = task_instance
        self.movie_list_url = url_from_args
        self.max_movies = 1000

    def _get_title_type(self, title_bar):
        for title_type in TITLE_TYPES:
            if title_type in title_bar:
                return title_type
        return 'Feature Film'

    def _extract_movie_info(self, html_page):
        soup = BeautifulSoup(html_page.text, 'html.parser')
        title_bar_div = soup.find('div', class_='title_bar_wrapper')
        title_info = {}
        if title_bar_div is not None:
            rating_span = title_bar_div.find('span', attrs={"itemprop": "ratingValue"})
            if rating_span is not None:
                rating = rating_span.text
                title_info['rating'] = rating
            else:
                logging.info('title rating not found')
            title_div = title_bar_div.find('div', class_='titleBar')
            name_h1 = title_div.find('h1')
            if name_h1 is not None:
                if name_h1.span is not None:
                    name_h1.span.decompose()
                name = name_h1.text.replace('\xa0 ', '').strip()
                title_info['name'] = name
            else:
                logging.info('title name not found')
            subtext_div = title_div.find('div', class_='subtext')
            if subtext_div is not None:
                subtext = subtext_div.text
                title_type = self._get_title_type(subtext)
                title_info['title_type'] = title_type
            else:
                logging.info('title type not found')
        else:
            logging.info('title name, title type and rating not found')
        plot_summary_div = soup.find('div', class_='plot_summary')
        if plot_summary_div is not None:
            stars_h4 = plot_summary_div.find('h4', text='Stars:')
            if stars_h4 is not None:
                stars = [star.text for star in stars_h4.parent.find_all('a')]
                del stars[-1]
                title_info['stars'] = stars
        if 'stars' not in title_info:
            logging.info('stars not found')

        title_story_line_div = soup.find('div', id='titleStoryLine')
        if title_story_line_div is not None:
            genres_h4 = title_story_line_div.find('h4', text='Genres:')
            if genres_h4 is not None:
                genres = [star.text.strip() for star in genres_h4.parent.find_all('a')]
                title_info['genres'] = genres
        if 'genres' not in title_info:
            logging.info('genres not found')

        details_div = soup.find('div', id='titleDetails')
        if details_div is not None:
            current_key = 'details'
            needed_block = True
            for child in details_div.children:
                if child.name == 'h3' or child.name == 'h2':
                    current_key = child.text.strip()
                    needed_block = current_key in DETAIL_BLOCKS
                    if needed_block:
                        title_info[current_key] = {}
                if child.name == 'div' and 'txt-block' in child['class'] and needed_block:
                    h4 = child.find('h4')
                    if h4 is not None:
                        sub_key = h4.text.replace(':', '')
                        child.h4.decompose()
                        children_text = [txt.strip() for txt in
                                         child.text.replace('See more\xa0»', '').strip().split('|')]
                        title_info[current_key][sub_key] = children_text if len(children_text) > 1 else children_text[0]
        else:
            logging.info('details not found')
        logging.info(f'title info found')
        return title_info

    def start(self):
        print('started')
        total_title_count = 0
        title_pages = []
        while total_title_count < self.max_movies:
            search_url = self.movie_list_url + f'&start={total_title_count + 1}'
            html_doc = requests.get(search_url)
            soup = BeautifulSoup(html_doc.text, 'html.parser')
            titles = {*[link.find('a', href=True).get('href') for link in soup.select('div.lister-item.mode-simple')]}
            if len(titles) == 0:
                break
            title_pages.extend([self._extract_movie_info(requests.get(BASE_URL + title)) for title in titles])
            total_title_count += len(titles)
        self.task_instance.result_json = json.dumps(title_pages, ensure_ascii=False)
        self.task_instance.save()
        connection.close()
        # with open('result.json', 'w', encoding='utf-8') as result_json:
        #     json.dump(title_pages, result_json, ensure_ascii=False)
        # result_json.close()
        return title_pages

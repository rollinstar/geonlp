import requests
from bs4 import BeautifulSoup
import hashlib
import pickle
import datetime
import time
from random import uniform
import copy

# daum breaking news list page url
def make_news_page_url(d, p):
    if d == '' or d == None or p == '' or p == None:
        return None
    base_url = 'https://news.daum.net/breakingnews/society/affair?regDate={}&page={}'
    url = base_url.format(d, p)
    return url

# daum breaking news contents page url
def make_news_contents_url(code):
    if code == '' or code == None:
        return None
    base_url = 'http://news.v.daum.net/v/{}'
    url = base_url.format(code)
    return url

# extract html tags using selector
def select_tags(html, selector):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        tags = soup.select(selector)
        return tags
    except Exception as e:
        print('select_tags err: ', e)
        return None

# reqeust and extract html document
def fetch_html(url):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            html = res.text
        return html
    except Exception as e:
        print('fetch_html err: ', e)
        return None

# create a resource_id(checksum)
def create_resource_id(ele):
    z = pickle.dumps(ele)
    rid = hashlib.md5(z).hexdigest()
    return rid

class DaumNewsCollector:
    def __init__(self, min, max):
        self.min = min
        self.max = max

    # Create a dictionary of breaking news pages by date
    def create_news_pages_links_by_date(self, day):
        page_check = True
        page = 0
        resource = []
        print('START/day: ', day)
        while page_check == True:
            page += 1
            url = make_news_page_url(day, page)
            page_list_html = fetch_html(url)
            if page_list_html == None:
                page_check = False

            tags = select_tags(page_list_html, '#mArticle > div.box_etc > ul > li')
            if len(tags) == 0:
                page_check = False
                break

            # UTC datetime
            datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            element = {
                    'resource_id': None,
                    'news_page_info': str(day) + '__' + str(page),
                    'counts': len(tags),
                    'news_ids': None,
                    'created_at': datetime,
                    'updated_at': datetime
            }
            ids = []
            for idx, tag in enumerate(tags):
                anchor = tag.select_one('a')
                newsId = anchor['href'].replace('https://v.daum.net/v/', '')
                ids.append(newsId)
            element['news_ids'] = ids
            rid = create_resource_id(element)
            element['resource_id'] = rid
            resource.append(element)

            # Interval
            n = uniform(self.min, self.max)
            time.sleep(n)
            log = 'Page No.{} ({}sec)'.format(page, n)
            print(log)
        print('END/day: ', day)
        return  resource

    def create_news_contents_data(self, code):
        url = make_news_contents_url(code)
        # UTC datetime
        datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # result code => 0(Fail), 1(Success)
        news_contents = {
                'resource_id': '',
                'news_code': code,
                'url': url,
                'title': '',
                'reg_date': '',
                'sentences': [],
                'result_code': '0',
                'created_at': datetime,
                'updated_at': datetime
        }
        if url == None:
            return news_contents
        try:
            html = fetch_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.select_one('#cSub > div > h3').text
            #reg_date = soup.select_one('#cSub > div > span > span:nth-of-type(2)').text.replace('입력', '')
            reg_date = '{}-{}-{}'.format(code[0:4], code[4:6], code[6:8])
            #t = reg_date.split(' ')
            #reg_date = t[0].replace('.', '-')[:-1] + ' ' + t[1]
            #reg_date = reg_date.strip()
            contents = soup.select('#harmonyContainer > section > p')
            sentences = []
            for p in contents:
                sentences.append(p.text)
            result = copy.deepcopy(news_contents)
            result['title'] = title
            result['reg_date'] = reg_date
            result['sentences'] = sentences
            result['result_code'] = '1'
            rid = create_resource_id(result)
            result['resource_id'] = rid
            return result
        except Exception as e:
            print('create_news_contents_data err: ', e)
            return news_contents













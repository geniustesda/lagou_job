import logging
import os

import requests
from bs4 import BeautifulSoup
import time
from config.config import TIME_SLEEP

from util.excel_helper import mkdirs_if_not_exists


JOB_DETAIL_DIR = './data/'

logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s-%(message)s\t", level=logging.DEBUG)


def crawl_job_detail(positionId, positionName):
    """get the detailed description of the job"""
    request_url = 'https://m.lagou.com/jobs/' + str(positionId) + '.html'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Host': 'm.lagou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'
    }

    response = requests.get(request_url, headers=headers, timeout=10)
    if  response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html5lib')
        text = soup.find_all('div', class_='content')[0].get_text()

        write_job_details(positionId, text, positionName)
        time.sleep(TIME_SLEEP)
    elif response.status_code == 403:
        logging.error('request is forbidden by the server...')
    else:
        logging.error(response.status_code)


def write_job_details(positionId, text, parent_dir_name):
    """write the job details text into text file"""
    details_dir = JOB_DETAIL_DIR + parent_dir_name + os.path.sep
    mkdirs_if_not_exists(details_dir)
    try:
        f = open(details_dir + str(positionId) + '.txt', mode='w', encoding='UTF-8')
    except:
        import io
        f = io.open(details_dir + str(positionId) + '.txt', mode='w', encoding='UTF-8')
    finally:
        f.write(text)
        f.flush()
        f.close()
        logging.info('%s has been written successfully...' % positionId)


if __name__ == '__main__':
    crawl_job_detail('3040728','')
    print(joblist)

# -*- coding: utf-8 -*-
# !/usr/bin/env python

import os
import sys
import time
import json
import requests


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from spider.jobdetail_spider import crawl_job_detail
import pandas as pd
from util import log
from config.config import TIME_SLEEP
from util.excel_helper import write_excel
# from entity import job
from imp import reload

try:

    from urllib import parse as parse
except:
    import urllib as parse

    reload(sys)
    sys.setdefaultencoding('utf-8')




def crawl_jobs(positionName):
    """crawl the job info from lagou H5 web pages"""
    JOB_DATA = list()
    max_page_number = get_max_pageNo(positionName)
    log.info("%s, 共有 %s 页记录, 共约 %s 记录", positionName, max_page_number, max_page_number * 15)
    cookies = get_cookies()

    for i in range(1, max_page_number + 1):
#       https://m.lagou.com/search.json?city=%E5%85%A8%E5%9B%BD&positionName=
        request_url = 'https://m.lagou.com/search.json?city=上海&positionName=' + parse.quote(
            positionName) + '&pageNo=' + str(i) + '&pageSize=15'
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Host': 'm.lagou.com',
            'Referer': 'https://m.lagou.com/search.html',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, '
                          'like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive'
        }
        response = requests.get(request_url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            for each_item in response.json()['content']['data']['page']['result']:
                JOB_DATA.append([each_item['positionId'], each_item['positionName'], each_item['city'],
                                 each_item['createTime'], each_item['salary'],
                                 each_item['companyId'], each_item['companyName'], each_item['companyFullName']])
                crawl_job_detail(each_item['positionId'], positionName)
            print('crawling page %d done...' % i)
            time.sleep(TIME_SLEEP)
        elif response.status_code == 403:
            log.error('request is forbidden by the server...')
        else:
            log.error(response.status_code)

    return JOB_DATA


def get_cookies():
    """return the cookies after your first visit"""
    headers = {
        'Host': 'm.lagou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'
    }
    url = 'https://m.lagou.com/'
    response = requests.get(url, headers=headers, timeout=10)

    return response.cookies


def get_max_pageNo(positionName):
    """return the max page number of a specific job"""
    cookies = get_cookies()
    
#    https://m.lagou.com/search.json?city=%E5%85%A8%E5%9B%BD&positionName=
    request_url = 'https://m.lagou.com/search.json?city=上海&positionName=' + parse.quote(
        positionName) + '&pageNo=1&pageSize=15'
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Host': 'm.lagou.com',
        'Referer': 'https://m.lagou.com/search.html',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) '
                      'Version/8.0 Mobile/12A4345d Safari/600.1.4',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Cookie':'user_trace_token=20170428184410-5edfada14cff439e900c65a362047997; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1494504046,1494520724,1494520726,1494605025; _ga=GA1.2.1672649481.1493376208; LGUID=20170428184410-9cbe33a6-2bff-11e7-b419-5254005c3644; index_location_city=%E4%B8%8A%E6%B5%B7; _gid=GA1.2.1306666080.1494607685; _ga=GA1.3.1672649481.1493376208; JSESSIONID=ABAAABAAAGCABCC050B020B0B154F3A2AB049B42A389C67; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1494607685; LGSID=20170513000506-c3e48d3a-372c-11e7-9ad9-525400f775ce; LGRID=20170513004926-f55d0b25-3732-11e7-bd6e-5254005c3644; _putrc=""; login=false; unick=""; _gat=1'
    }
    response = requests.get(request_url, headers=headers, cookies=cookies, timeout=10)
    print("获取 %s 信息路由:" % positionName + request_url)
    if response.status_code == 200:
        max_page_no = int(int(response.json()['content']['data']['page']['totalCount']) / 15 + 1)
        
        return max_page_no
    elif response.status_code == 403:
        log.error('request is forbidden by the server...')

        return 0
    else:
        log.error(response.status_code)

        return 0


if __name__ == '__main__':
    jobname = 'python'
    craw_job_list = ["python","机器学习","数据挖掘","后端","前端", "Android","人工智能" ]
    for _ in craw_job_list:
        joblist = crawl_jobs(_)
        col = [
            u'职位编码',
            u'职位名称',
            u'所在城市',
            u'发布日期',
            u'薪资待遇',
            u'公司编码',
            u'公司名称',
            u'公司全称']
        jl = [json.dumps(_) for _ in joblist]
        df = pd.DataFrame(joblist, columns=col)
        path = "./data/"
        df.to_csv(path + _ + ".csv")
        write_excel(joblist, jobname)

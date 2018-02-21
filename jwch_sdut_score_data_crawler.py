# -*- coding: utf-8 -*-
import time
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from multiprocessing import Pool

client = MongoClient() #init mongodb server
score_data_coll = client.jwch.sdut_score_data #jwch sdut_score_data collection

url = '成绩抓取链接'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}

#爬取网页函数
def get_page(payload):
    html = requests.post(url, headers=headers, data=payload)
    soup = BeautifulSoup(html.content, 'lxml')
    table = soup.select('table > tr > td > table')
    trs = table[2].select('tr')
    if table[0].select('tr td')[0].get_text().strip() == payload['post_xuehao']:
        get_info(table, trs, payload)
    else:
        print('--------------------')
        print('学号',payload['post_xuehao'],'获取失败')
        print('--------------------')

#获取数据函数
def get_info(table, trs, payload):
    for x in range(1, len(trs)):
        score_data = {
            'xuehao': table[0].select('tr td')[0].get_text().strip(),
            'xuenian': trs[x].select('td')[1].get_text().strip(),
            'xueqi': trs[x].select('td')[2].get_text().strip(),
            'leibie': trs[x].select('td')[3].get_text().strip(),
            'kecheng': trs[x].select('td')[5].get_text().strip(),
            'xuefen': trs[x].select('td')[7].get_text().strip(),
            'chengji': trs[x].select('td')[9].get_text().strip(),
            'bukao': trs[x].select('td')[10].get_text().strip()
        }
        # print(score_data)
        score_data_coll.update(score_data, score_data, True)

#主函数启动入口
if __name__ == '__main__':
    payloads = [{'post_xuehao':'15110302{}'.format(str(i))} for i in range(120,130)]

    print('开始爬取数据')
    start_at = time.time()
    for payload in payloads:
        get_page(payload)
        time.sleep(1)
    end_at = time.time()
    print('串行型爬虫总耗时:', end_at-start_at)
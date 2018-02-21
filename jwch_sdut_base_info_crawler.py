# -*- coding: utf-8 -*-
import time
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from multiprocessing import Pool

client = MongoClient() #init mongodb server
base_info_coll = client.jwch.sdut_base_info #jwch sdut_base_info collection

url = '学号抓取链接'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}

#爬取网页函数
def get_page(payload):
    html = requests.post(url, headers=headers, data=payload)
    soup = BeautifulSoup(html.content, 'lxml')
    table = soup.select('table > tr > td > table')
    trs = table[0].select('tr')
    if len(table[0].select('tr td'))>1:
        get_info(trs, payload)
    else:
        print('--------------------')
        print('学号',payload['post_xuehao'],'信息获取失败')
        print('--------------------')

#获取数据函数
def get_info(trs, payload):
    for x in range(1, len(trs)):
        base_info = {
            'xuehao': trs[x].select('td')[1].get_text().strip(),
            'xingming': trs[x].select('td')[2].get_text().strip(),
            'xingbie': trs[x].select('td')[3].get_text().strip(),
            'nianji': trs[x].select('td')[4].get_text().strip(),
            'yuanxi': trs[x].select('td')[5].get_text().strip(),
            'zhuanye': trs[x].select('td')[6].get_text().strip(),
            'banji': trs[x].select('td')[7].get_text().strip(),
            'cengci': trs[x].select('td')[9].get_text().strip(),
            'xuezhi': trs[x].select('td')[10].get_text().strip(),
        }
        if base_info['xuehao'].startswith(payload['post_xuehao']):
            base_info_coll.update(base_info, base_info, True) #有则更新无则新建

#主函数启动入口
if __name__ == '__main__':
    payloads = [{'post_xuehao':'{}1'.format(str(i))} for i in range(14,18)] #14级到17级模糊查询

    print('开始爬取数据')
    start_at = time.time()
    for payload in payloads:
        get_page(payload)
        time.sleep(2)
    end_at = time.time()
    print('串行型爬虫总耗时:', end_at-start_at)

    # print('开始爬取数据')
    # start_at = time.time()
    # pool = Pool(4) #同时跑4个进程,不知道会不会卡死~
    # pool.map(get_page, payloads)
    # pool.close()
    # pool.join()
    # end_at = time.time()
    # print('多进程爬虫总耗时:', end_at-start_at)

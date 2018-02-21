# -*- coding: utf-8 -*-
import time
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from multiprocessing import Pool

client = MongoClient() #init mongodb server
base_info_coll = client.jwch.sdut_base_info #jwch sdut_base_info collection
score_data_coll = client.jwch.sdut_score_data #jwch sdut_score_data collection

url = '成绩抓取链接'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}

#根据学号获取网页信息
def get_page(payload):
    html = requests.post(url, headers=headers, data=payload)
    soup = BeautifulSoup(html.content, 'lxml')
    table = soup.select('table > tr > td > table')
    # 验证学号是否正确
    if table[0].select('tr td')[0].get_text().strip() == payload['post_xuehao']:
        for x in range(1, len(table[2].select('tr'))):
            score_data = {
                'xuehao': table[0].select('tr td')[0].get_text().strip(),
                'xuenian': table[2].select('tr')[x].select('td')[1].get_text().strip(),
                'xueqi': table[2].select('tr')[x].select('td')[2].get_text().strip(),
                'leibie': table[2].select('tr')[x].select('td')[3].get_text().strip(),
                'kecheng': table[2].select('tr')[x].select('td')[5].get_text().strip(),
                'xuefen': table[2].select('tr')[x].select('td')[7].get_text().strip(),
                'chengji': table[2].select('tr')[x].select('td')[9].get_text().strip(),
                'bukao': table[2].select('tr')[x].select('td')[10].get_text().strip()
            }
            score_data_coll.update(score_data, score_data, True)
            # score_data_coll.insert(score_data)
    else:
        print('--------------------')
        print('学号',payload['post_xuehao'],'获取失败')
        print('--------------------')

#重数据库查出学号
def get_from_db(limit, skip):
    return base_info_coll.find({}, {'xuehao':1, '_id':0}).limit(limit).skip(skip)

#主函数启动入口
if __name__ == '__main__':
    perp = 20
    print('开始爬取数据')
    start_at = time.time()
    # get_page()
    for i in range(238,250):
        res = get_from_db(perp, i*perp)
        payloads = [{'post_xuehao':r['xuehao']} for r in res]
        print('已查询',perp*(i+1),'条数据')
        pool = Pool(8)
        pool.map(get_page, payloads)
        pool.close()
        pool.join()
        time.sleep(2)
    end_at = time.time()
    print('多进程爬虫总耗时:', end_at-start_at)
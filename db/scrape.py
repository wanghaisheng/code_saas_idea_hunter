#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: RogerRordo

from ast import keyword
import logging
import optparse
import asyncio
import base64
import signal
from datetime import datetime
from datetime import timedelta
from unittest import result
from colorlog import ColoredFormatter
from urllib.parse import quote_plus
import requests
import math
import os
import random
import time
import platform
import json
from pyairtable.formulas import match
from pyairtable import *
from playwright.async_api import async_playwright
import sys
import logging
from tenacity import *
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}
LOG_LEVEL = logging.INFO
log = logging.getLogger('pythonConfig')

signalTag = False

proxylist=[]


USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")


@retry(stop=stop_after_attempt(3), before=before_log(logger, logging.DEBUG))
def supabaseop(tablename,users):
    try:
        data = supabase_db.table(tablename).insert(users).execute()    
    except:
        raise Exception


def signalHandler(signal, frame):
    log.warning('Signal catched...')
    global signalTag
    signalTag = True
# from .util import *
async def get_playright(proxy:bool=False,headless:bool=True):
    print('proxy',proxy,'headless',headless)
    browser=''
    if 'linux' in platform.system():
        headless=True
    playwright =await  async_playwright().start()
    PROXY_SOCKS5 = "socks5://127.0.0.1:1080"
    # browser=''
    if proxy==False:
        try:
            print("start pl without proxy")
            browser = await  playwright.firefox.launch(headless=headless)
            print('start is ok')
            return browser

        except:
            print('pl no proxy start failed')
            browserLaunchOptionDict = {
            "headless": headless,
            "proxy": {
                    "server": PROXY_SOCKS5,
            }
            } 
            browser = await playwright.firefox.launch(**browserLaunchOptionDict)
            # Open new page    
            return browser
    else: 
        print('proxy===',headless)
        browserLaunchOptionDict = {
        "headless": headless,
        "proxy": {
                "server": PROXY_SOCKS5,
        }
        } 
        browser = await playwright.firefox.launch(**browserLaunchOptionDict)
        # Open new page    

        return browser

def write_file(new_contents,topic):
    if not os.path.exists("web/README-{}.md".format(topic)):
        open("web/README-{}.md".format(topic),'w',encoding='utf-8').write('')

    with open("web/README-{}.md".format(topic), "w",encoding='utf-8') as fw:
        fw.write(new_contents)
def url_ok(url):
    try:
        response = requests.head(url)
    except Exception as e:
        # print(f"NOT OK: {str(e)}")
        return False
    else:
        if response.status_code == 400 or response.status_code==404:
            # print("OK")
            print(f"NOT OK: HTTP response code {response.status_code}")

            return False
        else:

            return True   

def update_daily_json(filename,data_all):
    if not os.path.exists(filename):
        print('create a  new file',filename)
        open(filename,'w',encoding='utf-8').write('')
    with open(filename,"r") as f:
        content = f.read()
        if not content:
            m = []
        else:
            m = json.loads(content)
    
    #将datas更新到m中
    for data in data_all:
        # print('item---',data)

        
        m.append(data)
    # print('mmm',m)
    # save data to daily.json
    m= list({elem["name"]:elem for elem in m}.values())
    print('/',type(m),m)
    with open(filename,"w",encoding='utf-8') as fp:
        json.dump(m,fp)
    return m
async def coldstart(topic,table):
    item_list = []
    datall=[]

    start = time.time()
    url = "https://github.com/search?o=desc&q={}&s=updated&type=Repositories".format(topic)
    try:
        browser = await get_playright(False,False)
        context = await browser.new_context()
        page = await browser.new_page()
        print('this url',url)
        res=await page.goto(url)
        print('user home url',url)
        # time.sleep(60)
        count =  page.locator('div.flex-column:nth-child(1) > h3:nth-child(1)')
        count = await count.text_content()
        print(count.strip())
        count=count.strip().split(' ')[0].replace(',','')
        print(count)
        total_count = int(count)
        if total_count<10:
            pages=1
        else:
            pages = math.ceil(total_count / 10) + 1

        print('total count',total_count)
        if total_count < 1000:
            print('total <1000, pagination is',pages)
            for i in range(pages):
                href = "https://github.com/search?o=desc&q={}&s=updated&type=Repositories".format(topic)

                url=href+'&s=updated&p='+str(i)
                print('===============',url)
                try:
                    time.sleep(random.randint(10, 30))    

                    res=await page.goto(url)
                    items = page.locator('li.repo-list-item')
                    for i in range(await items.count()):
                        full_name =await items.nth(i).locator('a.v-align-middle').text_content()
                        print('fullname',full_name)
                        des =items.nth(i).locator('p.mb-1')
                        if await des.count()>0:
                            des=await des.text_content()
                        else:
                            des=''
                        url ="https:github.com"+await items.nth(i).locator('a.v-align-middle').get_attribute("href")
                        print('repo url',url)
                        ife=items.nth(i).locator("div > div > div >a.topic-tag")
                        topics =topic

                        if await ife.count()>0:
                            for i in range(await ife.count()):
                                tmp =await ife.nth(i).get_attribute("title")
                                topics=topics+','+tmp.split(":")[1]
                        language=''
                        if await items.nth(i).locator('//div[2]/div[2]/div/div[2]/span/span[2]').count()>0:
                            language=await items.nth(i).locator('//div[2]/div[2]/div/div[2]/span/span[2]').text_content()
                            print('language exist',language)
                        
                        FORMAT='%Y-%m-%dT%H:%M:%S%z'

                        row ={
                            "name": full_name,
                            "description": des.strip(),
                            "url": url,
                            "topic":topics,
                            "language":language,
                            "created_at": datetime.now().strftime(FORMAT)
                        }
                        print(row,'============')
                        datall.append(row)
                        # updaterow(table,[row])

                
                except Exception as e:
                    print("网络发生错误", e)
                    continue

        else:
            filters=page.locator("a.filter-item")
            
            filterscount=await filters.count()
            print(filterscount,type(filterscount))
            if filterscount>0:
                for i in range(filterscount):
                    element =filters.nth(i)
                    href="https:github.com"+await element.get_attribute("href")
                    keyword=href.split('=')[1]
                    count = await element.locator('span').text_content()
                    print(keyword,count)
                    total_count=int(count)
                    pages=int(total_count/10)+1
                    urls=[]
                    for i in range(pages):
                        url=href+'&s=updated&p='+str(i)
                        print('keyword',keyword,'page-',url)
                        try:
                            time.sleep(random.randint(30, 60))    

                            res=await page.goto(url)
                            items = page.locator('li.repo-list-item')
                            for i in range(await items.count()):
                                full_name =await items.nth(i).locator('a.v-align-middle').text_content()
                                print('fullname',full_name)
                                des =items.nth(i).locator('p.mb-1')
                                if await des.count()>0:
                                    des=await des.text_content()
                                else:
                                    des=''
                                url ="https:github.com"+await items.nth(i).locator('a.v-align-middle').get_attribute("href")
                                ife=items.nth(i).locator("div > div > div >a.topic-tag")
                                topics =topic

                                if await ife.count()>0:
                                    for i in range(await ife.count()):
                                        tmp =await ife.nth(i).get_attribute("title")
                                        topics=topics+','+tmp.split(":")[1]
                                language=keyword.split('&')[0]
                                FORMAT='%Y-%m-%dT%H:%M:%S%z'

                                row ={
                                    "name": full_name,
                                    "description": des.strip(),
                                    "url": url,
                                    "topic":topics,
                                    "language":language,
                                    "created_at": datetime.now().strftime(FORMAT)
                                }
                                print(row,'============')
                                datall.append(row)
                                # updaterow(table,[row])

                        
                        except Exception as e:
                            print("网络发生错误", e)
                            continue

        
    except:
        print("请求数量的时候发生错误")
    if len(datall)>0:
        print('datall',datall)
        m = update_daily_json("data/{}.json".format(topic),datall)
        json2md(m,topic)  

    return item_list



async def worker(id: int, st: datetime, ed: datetime, proxylist: list, delay: float, timeout: float,topic:str,keyword:str,index:int,language:str,table:Table) -> dict:
    workerRes = {}  # e.g. {'22.3.4.5': '2021-04-26 03:53:41'}
    # proxy = await popProxy(id, proxypool, timeout)
    # get latest 1000 results

    item_list = []
    j=index
    global signalTag
    # while not signalTag:
    result=False
    while not result:
        try:
            proxy =random.choice(proxylist)

            url = "https://api.github.com/search/repositories?q={}&sort=updated&per_page=100&page={}".format(keyword+'+'+language,j)
                # client.get() may get stuck due to unknown reasons
                # resp = await client.get(url=url, headers=HEADERS, timeout=timeout)
            resp = requests.get(url,proxies={'http': proxy}, auth=(USERNAME, TOKEN))
            req = resp.json()
            items=[]
            if 'items' in req:
                items = req["items"]
            print("第{}轮，爬取{}条".format( j, len(items)))
            if(len(items))>0:
                save(table,keyword,topic,items)
                result=True
                print('type',type(item_list),type(items))
                item_list.extend(items)
                proxylist.append(proxy)
                result=True
            else:
                proxypool='https://proxypool.scrape.center/random',

                newProxy = requests.get(proxypool).text
                log.warning('[{}] Proxy EXP: proxy={} newProxy={} st={} ed={}'.format(id, proxy, newProxy, time2str(st),
                                                                                        time2str(ed)))
                log.debug('[{}] Proxy EXP: {}'.format(id, e))
                proxy = newProxy                
                result=False
        except Exception as e:
            print(index,"网络发生错误", e,proxy)
            proxylist.remove(proxy)
            newproxy =random.choice(proxylist)
            proxy=newproxy
            result=False
            print('another try',index)
    return item_list

def str2time(x: str) -> datetime:
    return datetime.strptime(x, "%Y-%m-%d %H:%M:%S")


def time2str(x: datetime) -> str:
    return x.strftime("%Y-%m-%d %H:%M:%S")



async def main(opts):
    # Catch signal to exit gracefully

    keywords=[]
    print('keywords list ',opts.keywords)
    
    if ',' in opts.keywords:
        keywords=opts.keywords.split(',')
    else:
        keywords.append(opts.keywords)
    topic=opts.topic
    print('keywords list ',keywords)
    apikey=os.environ.get('AIRTABLE_API_KEY')
    baseid=os.environ.get(topic.upper()+'_AIRTABLE_BASE_KEY')
    tableid=os.environ.get(topic.upper()+'_AIRTABLE_TABLE_KEY')
    if  os.path.exists('data/'+topic+'.json'):
        with open('data/'+topic+'.json',encoding='utf8') as f1:
            # print(f.read())
            data=f1.read()
            if len(json.loads(data))<1000:
                print('there is empty json,cold start ')
                for k in keywords:

                    await coldstart(k)
    else:
        print('there is no json,cold start ')
        for k in keywords:

            await coldstart(k,table)

async def latest(opts):
    signal.signal(signal.SIGINT, signalHandler)

    keywords=[]
    print('keywords list ',opts.keywords)
    timeSt = '2021-05-01 00:00:00'
    timeEd = '2021-05-01 01:00:00'    
    if ',' in opts.keywords:
        keywords=opts.keywords.split(',')
    else:
        keywords.append(opts.keywords)
    topic=opts.topic    
    if not os.path.exists('data/'+topic+'.json'):
        print('create a  new file','data/'+topic+'.json')
        open('data/'+topic+'.json','w',encoding='utf-8').write('')
    for k in keywords:
        # Assign tasks
        timeSt = str2time(timeSt)
        timeEd = str2time(timeEd)
        dt = (timeEd - timeSt) / opts.threads
        for_count=10
        try:
            url = "https://api.github.com/search/repositories?q={}&sort=updated".format(topic)

            reqtem = requests.get(url, auth=(USERNAME, TOKEN)).json()
            # print('raw json',reqtem)
            total_count = reqtem["total_count"]
            print('total result',total_count)
            # github api limit 1000
            if total_count<100:
                for_count=0
            else:
                for_count = math.ceil(1000 / 100) 

            # https://docs.github.com/en/rest/reference/search
            # The Search API helps you search for the specific item you want to find. For example, you can find a user or a specific file in a repository. Think of it the way you think of performing a search on Google. It's designed to help you find the one result you're looking for (or maybe the few results you're looking for). Just like searching on Google, you sometimes want to see a few pages of search results so that you can find the item that best meets your needs. To satisfy that need, the GitHub Search API provides up to 1,000 results for each search.
            print(total_count)
        except:
            print('here=========')
        proxypool=opts.proxypool
        if total_count<1000:
            pass
        else:
            proxylist=[]

            while len(proxylist)<20:    
                proxy = requests.get(proxypool).text
                if requests.get('https://api.github.com',proxies={'http': proxy}, auth=(USERNAME, TOKEN)).status_code==200:
                    proxylist.append(proxy)
                    print('add one',proxy)

            language_query_params=[
                "language:python",
                "language:javascript",
                "language:html",
                "language:c#",
                "language:typescript",
                "language:java",
                "language:c++",
                "language:css",
                "language:php",
                "language:Jupyter Notebook"                            
            ]

            i=0
            for item in language_query_params:
                coroutines = []
                proxy=random.choice(proxylist)
                coroutines.append(
                    worker(id=i,
                        st=timeSt + dt * i,
                        ed=timeSt + dt * (i + 1),
                        proxylist=proxylist,
                        delay=opts.delay,
                        timeout=opts.timeout,
                        topic=topic,
                        keyword=k,
                        index=i,
                        language=item,
                        table=''))
                i=i+1
                # Run tasks
                print('run task',item)
                workerRes = await asyncio.gather(*coroutines)
                proxylist=[]
                print(item,'task result',len(workerRes))

                time.sleep(60)
            # js(table,topic)

def url_ok(url):
    try:
        response = requests.head(url)
    except Exception as e:
        # print(f"NOT OK: {str(e)}")
        return False
    else:
        if response.status_code == 400 or response.status_code==404:
            # print("OK")
            print(f"NOT OK: HTTP response code {response.status_code}")

            return False
        else:

            return True   

def get_info(topic):
    # 监控用的
    try:

        api = "https://api.github.com/search/repositories?q={}".format(topic)
        # 请求API
        req = requests.get(api).json()
        items = req["items"]
        total_count = req["total_count"]
        for_count = math.ceil(total_count / 100) + 1
        # print(total_count)
        return total_count
    except Exception as e:
        print("网络请求发生错误", e)
        return None
     
def formatapiresult(items):
    result=[]
    for item in items:
        if item['id'] == "" or item['id']  == None:
            pass
        else:
            # print('valid  to save',item)

            full_name = item["full_name"]
            description = item["description"]
            if description == "" or description == None:
                description = 'no description'
            else:
                description = description.strip()
            url = item["html_url"]
            created_at = item["created_at"]
            topics=''
            if item["topics"] == "" or item["topics"] == None:
                topics=keyword
            else:
                topics=','.join(item["topics"])
            language=item['language']
            if language == "" or language == None:
                language='unknown'
            row ={
                "name": full_name,
                "description": description,
                "url": url,
                "topic":topics,
                "language":language,
                "created_at": created_at
            }  
            result.append(row)
    return result


def save(table,keyword,topic,items):
    # 下面是监控用的
    year = datetime.now().year
    sorted_list = []
    total_count = get_info(keyword)
    print("获取原始数据:{}条".format(total_count))
    # items=craw_all(keyword)
    print("获取dao原始数据:{}条".format(len(items)))

    items=formatapiresult(items)
    print('items',items)
    oldcontent=[]
    with open('data/'+topic+'.json',encoding="utf8") as f:
        if f.read() =='' or f.read() is None:
            pass
        else:
            oldcontent.extend(json.loads(f.read()))
    print('old content',oldcontent)
    for item in items:
        url=item['url']
        if not url in oldcontent:
            oldcontent.extend(item)
    print(oldcontent)
    update_daily_json("data/{}.json".format(topic),items)

    # sorted = db_match_a/irtable(table,items,keyword)
    print("record in db:{}条".format(len(sorted)))

def json2md(items,topic):
    result=[]
    # for idx,item in enumerate(table.all()):
    #     print(idx,item['fields'])
    #     result.append(item['fields'])    
    print('start convert json 2 md')
    DateToday = datetime.today()
    day = str(DateToday)    
    print('wwhty',items)
    newline = ""
    urls=[]
    for idx,s in enumerate(items):
        print(s,'-')
        if not s['url'] in urls:
            if s["description"] is None or s["description"]=='':
                des='-'
            if s["topic"] is None or s["topic"]=='':
                topic='-'                
            if s["language"] is None or s["language"]=='':
                language='-'                
            line = "|{}|{}|{}|{}|{}|{}|{}|\n".format(str(idx+1),
            s["name"], des, s["created_at"],s["url"],s["topic"],language)    

            newline = newline+line
            urls.append(s['url'])
    print(newline)
    if newline != "":
        old=f"## {day}\n"
        old=old+"|id|name|description|update_at|url|topic|language|\n" + "|---|---|---|---|---|---|---|\n"                   
        newline = "# Automatic monitor trending code under topic **{}** using Github Actions \n\n > update time: {}  total: {} \n\n \n ![star me](https://img.shields.io/badge/star%20me-click%20--%3E-orange) [code saas idea monitor](https://github.com/wanghaisheng/code_saas_idea_hunter)  [Browsing through the web](https://wanghaisheng.github.io/code_saas_idea_hunter/)  ![visitors](https://visitor-badge.glitch.me/badge?page_id=code_saas_idea_hunter) \n\n{}".format(
            topic,
            datetime.now(),
            len(items)
            ,old) + newline

        write_file(newline,topic)


def getOpts():
    parser = optparse.OptionParser()
    parser.add_option('-m', '--module', dest='module', default='ruijie_eg', type=str, help='Module name')
    parser.add_option('-k', '--keywords', dest='keywords', default='genshin', type=str, help='keyword list')
    parser.add_option('-n', '--topic', dest='topic', default='genshin', type=str, help='topic name')
    parser.add_option('-p',
                      '--proxypool',
                      dest='proxypool',
                      default='https://proxypool.scrape.center/random',
                      type=str,
                      help='Host and port of ProxyPool (default = 127.0.0.1:5010)')
    parser.add_option('-d',
                      '--delay',
                      default=5,
                      type=float,
                      dest='delay',
                      help='Seconds to delay between requests for each proxy (default = 5)')
    parser.add_option('-T', '--threads', default=15, type=int, dest='threads', help='Number of threads (default = 15)')
    parser.add_option('-t', '--timeout', default=6, type=float, dest='timeout', help='Seconds of Timeout (default = 6)')

    (opts, args) = parser.parse_args()
    return opts, args


def initLog():
    LOGFORMAT = "  %(log_color)s%(asctime)s  %(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"

    logging.root.setLevel(LOG_LEVEL)
    formatter = ColoredFormatter(LOGFORMAT)

    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    stream.setFormatter(formatter)

    log.setLevel(LOG_LEVEL)
    log.addHandler(stream)

if __name__ == '__main__':
    initLog()
    opts, args = getOpts()
    if opts.module == '':
        log.error('Module name required')
    else:
        asyncio.run(latest(opts))

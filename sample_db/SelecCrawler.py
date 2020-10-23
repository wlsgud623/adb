#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
from bs4.element import NavigableString
import requests
import lxml

def crawl_naver_one(url):
    try:
        Access_header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36 Edg/86.0.622.48'}
        respond = requests.get(url,headers = Access_header)
        soup = BeautifulSoup(respond.text,'lxml')
        
        Title = soup.select_one('#articleTitle').get_text()
        Date = soup.select_one('.t11').get_text()
        Paper = soup.find("meta", property ="me2:category1").get('content')
        URL = soup.select('#main_content > div.article_header > div.article_info > div > a')[0].get('href')
        
        source = soup.select('#articleBodyContents')[0]
        contents = ""
        for src in source:
            if(type(src) == NavigableString and src):
                contents = contents + src
        contents = contents.replace("\n", '')
        contents = contents.replace("\u200b", '')
        
        Category = []
        for cate in soup.find_all('em','guide_categorization_item'):
            Category.append(cate.get_text())
        
        if len(Category) == 1:
            Category.append("")
        
        return Title,Date,contents,Category[0],Category[1],Paper,URL
    
    except ConnectionError:
        print(repond.statue_code)
        return

def crawl_naver_mod(url):
    try:
        Access_header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36 Edg/86.0.622.48'}
        respond = requests.get(url,headers = Access_header)
        soup = BeautifulSoup(respond.text,'lxml')
        
        Title = soup.select_one('#articleTitle').get_text()
        Date = soup.select_one('.t11').get_text()
        Paper = soup.find("meta", property ="me2:category1").get('content')
        URL = soup.select('#main_content > div.article_header > div.article_info > div > a')[0].get('href')
        
        source = soup.select('#articleBodyContents')[0]
        contents = ""
        for src in source:
            if(type(src) == NavigableString and src):
                contents = contents + src
        contents = contents.replace("\n", '')
        contents = contents.replace("\u200b", '')
        
        Category = []
        for cate in soup.find_all('em','guide_categorization_item'):
            Category.append(cate.get_text())
        
        if len(Category) == 1:
            Category.append("")
        
        #홑괄호 제어 구문
        Title = Title.replace("'","''")
        contents = contents.replace("'","''")
        
        return Title,Date,contents,Category[0],Category[1],Paper,URL
    
    except ConnectionError:
        print(repond.statue_code)
        return
    
def crawl_URL_each(Sid1,Sid2,Date,Page_number):
    try:
        url = 'https://news.naver.com/main/list.nhn?mode=LS2D&listType=title&sid1={sid1}&sid2={sid2}&date={date}&page={number}'.format(sid1=Sid1,sid2=Sid2,date=Date,number=Page_number)
        Access_header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36 Edg/86.0.622.48'}
        respond = requests.get(url,headers = Access_header)
        soup = BeautifulSoup(respond.text,'lxml')
        Url_List = []
        
        if soup.select_one('#main_content > div.paging > strong').get_text() != str(Page_number): # 페이지 목록의 끝에 도달 시
            return False
        
        for art in soup.select('#main_content > div.list_body.newsflash_body > ul > li > a'):
            Url_List.append(art.get('href'))
            
        return Url_List
    
    except ConnectionError:
        print(respond.status_code)
        return
            
        


# In[2]:


import datetime

def get_today():
    today = datetime.date.today()
    today = str(today).replace('-','')
    return today

def get_yesterday(today):
    if len(today)!=8:
        print("Date input Error")
        return
    d = datetime.date(int(today[0:4]),int(today[4:6]),int(today[6:8]))
    y = d - datetime.timedelta(1)
    y = str(y).replace('-','')
    
    return y


# In[3]:


import sqlite3

def Create_Table(Table_name):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    sql = "CREATE TABLE {table}(Title Text, Date VARCHAR(20), Contents Text, Category1 VARCHAR(8), Category2 VARCHAR(8), Paper VARCHAR(10), URL Text)".format(table=Table_name)
    try:
        cursor.execute(sql)
        
    except:
        return
    
    else:
        conn.commit()
        conn.close()
        return

def Input_Article(article, Table):
    if len(article) != 7:
        print("input Error")
        return
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    sql = "INSERT INTO {table} VALUES('{title}','{date}','{contents}','{cat1}','{cat2}','{paper}','{url}')".format(table=Table,title=article[0],date=article[1],contents=article[2],cat1=article[3],cat2=article[4],paper=article[5],url=article[6])
    print(sql)
    try:
        cursor.execute(sql)
        conn.commit()
        print("입력 성공")
        
    except:
        print("입력 실패")
        raise Error


# In[4]:


import time

def crawl_all_night(Sid1, Sid2, Max_Date, Table_name):
    
# sid1 = 100 : 정치
#  sid2 = 264: 청와대, 265: 국회, 정당, 266: 행정, 267: 국방/외교, 268: 북한, 269: 정치 일반
# sid1 = 101 : 경제
#  sid2 = 260: 부동산, 259: 금융, 258: 증권, 261: 산업/재계, 262: 글로벌경제, 263: 경제 일반, 771: 중소기업/벤처 
# sid1 = 102 : 사회
#  sid2 = 249: 사건사고, 250: 교육, 251: 노동, 252: 환경, 254: 언론, 59b: 인권/복지, 256: 지역, 276: 인물, 257: 사회 일반
# sid1 = 103 : 생활/문화
#  sid2 = 237: 여행/레저, 239: 자동차/시승기, 240: 도로/교통, 241: 건강정보, 242: 공연/전시, 243: 책, 244: 종교, 245: 생활/문화 일반 
# sid1 = 104 : 세계
#  sid2 = 231: 아시아/호주, 232: 미국/중남미, 233: 유럽, 234: 중동/아프리카, 64f: 영문, 71a: 일문
# sid1 = 105 : IT/과학
#  sid2 = 226: 인터넷, 228: 과학 일반. 229: 게임/리뷰, 283: 컴퓨터, 230: IT 일반
    Date = get_today()
    Create_Table(Table_name)
    start_time = time.time()
    
    while Max_Date > 0:
        Page_number = 1
        while True:
            List = crawl_URL_each(Sid1,Sid2,Date,Page_number)
            
            if List == False:
                break
                
            else:
                for url in List:
                    try:
                        art = crawl_naver_mod(url)
                        Input_Article(art,Table_name)
                        
                    except:
                        try:
                            time.sleep(0.01)
                            art = crawl_naver_mod(url)
                            Input_Article(art,Table_name)
                        except:
                            pass
                Page_number = Page_number+1
        Date = get_yesterday(Date)
        Max_Date = Max_Date - 1
        
    print("실행 시간 : ",time.time()-start_time)
    print("End!")
    
    
    


# In[5]:


crawl_all_night(105,226,2,'인터넷')


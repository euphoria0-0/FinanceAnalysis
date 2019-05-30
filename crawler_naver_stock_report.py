### import packages
import pandas as pd 
import numpy as np
import datetime
import sys
import urllib
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from pandas import Series, DataFrame
from openpyxl import Workbook
import os
import time
from urllib import request

import webbrowser
import requests
import re
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from konlpy.tag import Twitter
tagger = Twitter() # Twitter 태깅 함수


#### naver finance price

# 프로그레스 바
def progressBar(value, endvalue, bar_length=20):
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()

# 한국거래소(krx)에서 종목코드 가져오기
code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
code_df = code_df[['회사명', '종목코드']] .rename(columns={'회사명': 'name', '종목코드': 'code'})

# get item code
def get_code(item_name): 
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False) 
    return code[1:]

## crawler
def crawler_naverfinance_stock(crp_name, start_date, end_date, filepath=None):
    stockItem = get_code(crp_name)
    df = pd.DataFrame(columns = ['date','close_val','change_val','open_val','high_val','low_val','acc_quant'])
    
    url = 'http://finance.naver.com/item/sise_day.nhn?code='+ stockItem
    html = urlopen(url) 
    source = BeautifulSoup(html.read(), "html.parser")
     
    for page in range(1, 234):
        if page % 10 == 0:
            print(str(page)+' / 234')
        url = 'http://finance.naver.com/item/sise_day.nhn?code=' + stockItem +'&page='+ str(page)
        html = urlopen(url)
        source = BeautifulSoup(html.read(), "html.parser")
        srlists=source.find_all("tr")
        isCheckNone = None
           
        #if((page % 1) == 0):
        #    time.sleep(1.50)
         
        for i in range(1,len(srlists)-1):
            if(srlists[i].span != isCheckNone):
                srlists[i].td.text
                
                date = srlists[i].find_all("td",align="center")[0].text.replace('.','')
                
                if date > end_date:
                    pass
                
                if date < start_date:
                    break
                
                close_val = srlists[i].find_all("td",class_="num")[0].text.replace(',','')
                change_val = srlists[i].find_all("td",class_="num")[1].text.replace(',','')
                open_val = srlists[i].find_all("td",class_="num")[2].text.replace(',','')
                high_val = srlists[i].find_all("td",class_="num")[3].text.replace(',','')
                low_val = srlists[i].find_all("td",class_="num")[4].text.replace(',','')
                acc_quant = srlists[i].find_all("td",class_="num")[5].text.replace(',','')
                
                price = pd.Series([date, close_val, change_val, open_val, high_val, low_val, acc_quant],
                                    index = ['date','close_val','change_val','open_val','high_val','low_val','acc_quant'])
                
                df = df.append(price, ignore_index = True)
    
    writer = pd.ExcelWriter(filepath+crp_name+'_stock_'+format(time.time(),'.0f')+'.xlsx')
    df.to_excel(writer, 'Sheet1', index = False)
    writer.save()    
        #progressBar(page, 110)
    return df


#### naver finance report

# - driver_path : chromedriver.exe가 설치되어 있는 경로
# - path : 엑셀파일이 저장될 위치(None : 현재위치)
# - start_date, end_date : 검색기간 설정(None : 전체기간)
# - pageNum : 가져올 페이지 수 (None : 검색된 전체 페이지)

def naver_finace_crawling(crp_name,path,start_date,end_date,pageNum=None):
    
    #chromedriver = 'dart/naver_finance_report/chromedriver.exe' #input("Chromedriver 위치 : ")
    driver_path = 'dart/naver_finance_report/chromedriver.exe'
    stockItem = get_code(crp_name)
    
    try:
        driver = webdriver.Chrome(driver_path)
    except:
        print("chrome driver 경로를 확인해주세요")
        return False,False

    if path is None:
        file_path = "./"
    else:
        file_path = path
    try:
        os.mkdir(file_path)
        print("%s폴더 생성"%path)
    except:
        print("path 있음")


    driver.implicitly_wait(3)

    page = 1
    stock_list = [] # 데이터 저장
    url = 'https://finance.naver.com/research/company_list.nhn?searchType=itemCode&itemCode='+stockItem
    
    while True:
    
        c_url = url +'&page=' + str(page)
        print(c_url)
        driver.get(c_url) # 해당 url로 이동

        html = driver.page_source

        # 테이블 정보 get
        table = driver.find_elements_by_xpath('//*[@id="contentarea_left"]/div[3]/table[1]/tbody/tr')

        for i,t in enumerate(table):
            
            endflage = False
            # 테이블의 행을 읽는다. 이때 줄바꿈 행도 읽기 때문에 rows의 길이 확인
            rows = t.find_elements_by_tag_name('td')
            if len(rows) == 6:
                temp = ['0' for _ in range(6)] # 저장할 공간을 미리 할당

                for k,row in enumerate(rows):
                    temp[k] = row.text
                    
                    # pdf경로는 tag가 다름
                    if row.get_attribute("class") == "file":
                        try:
                            temp[k] = row.find_element_by_tag_name("a").get_attribute('href')
                        except:
                    #        endflag = True
                            break

                temp[4] = '20'+temp[4].replace('.','')
                
                if temp[4] <= start_date:
                    break
                
                stock_list.append(temp)

        # 마지막 페이지인 경우 stop
        pagination = driver.find_element_by_xpath('//*[@id="contentarea_left"]/div[3]/table[2]/tbody/tr/td[@class="on"]')
        if pagination.text != str(page):
            break
        page += 1

    driver.quit()
    # DataFrame으로 변환 -> excel저장 용이
    try :
        stocks = DataFrame(stock_list)
    except:
        print(stock_list)
        print("저장할 데이터가 없거나 형식이 잘못되었습니다")
        return False, stock_list

    stocks.columns = ["종목명","제목","증권사","pdf","작성일","조회수"]
    #엑셀로 저장
    # 시간정보를 파일명에 더해서 덮여쓰여지는 것을 방지(존재하는 파일명을 사용하면 덮어쓰기된다)
    file_path = os.path.join(file_path,crp_name+'_report_'+format(time.time(),'.0f')+ ".xlsx")
    print(file_path)

    try:
        writer = pd.ExcelWriter(file_path)
        stocks.to_excel(writer,'Sheet1', index = False)
        writer.save()
        print("%s에 저장했습니다" % file_path)

    except:
        print("\n저장하지 못했습니다")

    return file_path, stocks


################################################################
    
if __name__ == "__main__":
    
    ######## input
    crp_name = 'crp_name'
    start_date = '20130901'
    end_date = '20190501'
    excel_path = 'path/'

    ### naver finance stock price
    df_stock = crawler_naverfinance_stock(crp_name, start_date, end_date, excel_path)

    ### naver finance report
    filename, data = naver_finace_crawling(crp_name, excel_path, start_date, end_date)


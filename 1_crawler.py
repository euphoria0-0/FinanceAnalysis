### install library
import pandas as pd
import requests
import sys
import os
import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen
import io
import re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
#import multiprocessing

### functions
# progress bar
def progressBar(value, endvalue, bar_length=20):
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()

### get 종목분석리포트 from finance.naver.com
# get pdf url and info
def naver_crawler(crpname, start_date='20090101', end_date='20190630'):
    print('\n.....crawling.....')
    start = datetime.datetime.now()
    # get crp code
    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
    itemCode = code_df.query("회사명=='{}'".format(crpname))['종목코드'].to_string(index=False)[1:]
    
    url = 'https://finance.naver.com/research/company_list.nhn?searchType=itemCode&itemCode='+itemCode+'&page='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    }
    idx_list = [2,3,4,5,6,10,11,12,13,14,18,19,20,21,22,26,27,28,29,30,34,35,36,37,38,42,43,44,45,46]
    df = pd.DataFrame(columns = ['date','kapital','title','comment','price','pdf'])
    
    end_page=25
    for page in range(1, end_page+1):
        progressBar(page, end_page)
        end_flag = False
        pg_url = url+str(page)
        # get url source
        r = requests.get(pg_url, stream=True, headers=headers)
        r.encoding = 'euc-kr'
        html = r.text
        source = BeautifulSoup(html, 'html.parser')
        srlists = source.find_all('tr')
        
        for i in range(30):
            #tr = srlists[idx_list[i]]
            try:
                tr = srlists[idx_list[i]]
                # get data
                date = '20'+tr.find_all('td')[4].text.replace('.','')
                if date < start_date or idx_list[i] == len(srlists)-1:
                    end_flag = True
                    break
                kap = tr.find_all('td')[2].text
                pdf = tr.find_all('td')[3].find('a')['href'][-17:-4]
                href = 'https://finance.naver.com/research/'+tr.find_all('td')[1].find('a')['href']
                # get data from second url
                html2 = urlopen(href)
                sour2 = BeautifulSoup(html2.read(), "html.parser")
                comment = sour2.find_all("em")[2].text
                comment = comment.replace('매수','Buy')
                price = sour2.find_all("em")[1].text.replace('원','')
                
                title = sour2.find_all("th")[0]
                a1 = str(title).find('span')
                a2 = len(str(title.find('span')))
                b1 = str(title).find(str(title.find('p')))
                title = str(title)[a1+a2:b1].replace('\n','')
                title = title.replace('\t','')
            except:
                pass
            
            record  = pd.Series([date, kap, title, comment, price, pdf],
                                 index = ['date','kapital','title','comment','price','pdf'])
            df = df.append(record, ignore_index = True)
            
        if end_flag:
            break
            
    end = datetime.datetime.now()
    print('\n---- crawling TIME: '+str(end-start))
    
    return df

### pdf parser
def pdfparser(data):
    fp = open(data, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    filename = data
    for i,page in enumerate(PDFPage.get_pages(fp)):
        try:
            interpreter.process_page(page)
            data =  retstr.getvalue()
        except error as e:
            print(e)
            print(filename,"failed to read %dth file"%i+1)
            return e
    return data

### pdf download from pdf url
def pdf_download(df_pdf, pdfpath, ind=False):
    print('\n.....downloading <%d> pdf files.....' % len(df_pdf))
    start = datetime.datetime.now()
    url = 'https://ssl.pstatic.net/imgstock/upload/research/company/'
    if ind:
        url = 'https://ssl.pstatic.net/imgstock/upload/research/industry/'
    
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    }
    idx = 0
    for pdf in df_pdf:
        idx += 1
        fname = pdfpath+'/'+str(pdf)+'.pdf'
        if not os.path.exists(fname):
            try:
                res = requests.get(url+str(pdf)+'.pdf', stream = True, headers=headers)
                with open(fname, 'wb') as f:
                    f.write(res.content)
            except:
                pass
        progressBar(idx, len(df_pdf))
    
    end = datetime.datetime.now()
    print("\n.....download TIME : ", end-start)

### extract(read) text from pdf ### time consuming
def pdfread(path):
    print('\n.....reading text in pdf.....')
    start = datetime.datetime.now()
    
    dirname = path+'pdf'
    down_path = path+'text'
    # get file names from directory
    file_list = os.listdir(dirname)
    path_filenames = [dirname+'/'+i for i in file_list]

    # extract file names without .pdf
    text_list = os.listdir(down_path)
    text_list = [os.path.splitext(i)[0] for i in text_list]

    pdf_list = []

    print("Total <%d> Files"%len(file_list))

    for i,file in enumerate(file_list):
        if file in text_list:
            continue
        # read only pdf files
        if '.pdf' == os.path.splitext(file)[-1]:
            #sys.stdout.write("\r reading {}th".format(i+1))
            progressBar(i, len(file_list))
            
            fname = down_path+'/'+file[:-4]+".txt"
            if not os.path.exists(fname):
                try:
                    pdf2txt = pdfparser(path_filenames[i])
                except:
                    #print("\n %s failed to read"%file)
                    pdf_list.append(file)
                    continue
                else:
                    # save txt files
                    with io.open(fname,'w',encoding='utf8') as f:
                        f.write(pdf2txt)
#                    f.close()
#                except:
#                    pdf_list.append(file)
#                    print('%s failed to save'%file)
    
    end = datetime.datetime.now()
    print("\n.....download TIME : ", end-start)
    
    return pdf_list

### text preprocessing
def extract_txt(dirname):
    start = datetime.datetime.now()
    
    file_list = os.listdir(dirname)
    df = pd.DataFrame(columns = ['pdf','text'])
    
    for i, file in enumerate(file_list):
        sys.stdout.write("\r reading {}th".format(i+1))
        
        if '.txt' in file:
            with open(dirname+'/'+file,'r', encoding='utf-8') as f:
                txt = f.read()
        
            txt_ko = re.sub("[^가-힣]",' ',txt)
            txt_ko = re.sub("   +",' ',txt_ko)
            record = pd.Series([file[:-4],txt_ko], index=['pdf','text'])
            df = df.append(record, ignore_index = True)
        
    end = datetime.datetime.now()
    print("\n.....processing TIME : ", end-start)
    
    return df

### get 산업분석리포트 from finance.naver.com
def naver_crawler_ind(ind, start_date='2009-01-01', end_date='2019-06-30'):
    print('\n.....crawling.....')
    start = datetime.datetime.now()
    
    url = 'https://finance.naver.com/research/industry_list.nhn?searchType=writeDate&writeFromDate='+start_date+'&writeToDate='+end_date+'&page='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    }
    idx_list = [2,3,4,5,6,10,11,12,13,14,18,19,20,21,22,26,27,28,29,30,34,35,36,37,38,42,43,44,45,46]
    df = pd.DataFrame(columns = ['industry','date','kapital','title','pdf'])
    
    end_page=728
    for page in range(1, end_page+1):
        progressBar(page, end_page)
        end_flag = False
        pg_url = url+str(page)
        # get url source
        r = requests.get(pg_url, stream=True, headers=headers)
        r.encoding = 'euc-kr'
        html = r.text
        source = BeautifulSoup(html, 'html.parser')
        srlists = source.find_all('tr')
        
        for i in range(30):
            #tr = srlists[idx_list[i]]
            try:
                tr = srlists[idx_list[i]]
                # get data
                if tr.find_all('td')[0].text == ind:
                    date = '20'+tr.find_all('td')[4].text.replace('.','')
                    if idx_list[i] == len(srlists)-1:
                        end_flag = True
                        break
                    kap = tr.find_all('td')[2].text
                    pdf = tr.find_all('td')[3].find('a')['href'][-17:-4]
                    href = 'https://finance.naver.com/research/'+tr.find_all('td')[1].find('a')['href']
                    # get data from second url
                    html2 = urlopen(href)
                    sour2 = BeautifulSoup(html2.read(), "html.parser")

                    title = sour2.find_all("th")[0]
                    a1 = str(title).find('span')
                    a2 = len(str(title.find('span')))
                    b1 = str(title).find(str(title.find('p')))
                    title = str(title)[a1+a2:b1].replace('\n','')
                    title = title.replace('\t','')
                    
                    record  = pd.Series([ind, date, kap, title, pdf],
                                     index = ['industry','date','kapital','title','pdf'])
                    df = df.append(record, ignore_index = True)
            except:
                pass

                
            
        if end_flag:
            break
            
    end = datetime.datetime.now()
    print('\n---- crawling TIME: '+str(end-start))
    
    return df

## crawler stock price by item (just for getting data in 2008)
def crawler_naverfinance_stock(itemcode, start_date, end_date):
    df = pd.DataFrame(columns = ['date','close_val'])
    if itemcode=='kospi':
        url = 'https://finance.naver.com/sise/sise_index_day.nhn?code=kospi&page='
        a,b = 436, 480
    else:
        url = 'http://finance.naver.com/item/sise_day.nhn?code='+ itemcode +'&page='
        a,b = 261, 291
    
    for page in range(a, b):
        #sys.stdout.write(str(page))
        #sys.stdout.flush()

        urlp = url + str(page)
        html = urlopen(urlp)
        source = BeautifulSoup(html.read(), "html.parser")
        srlists = source.find_all("tr")
        isCheckNone = None
         
        for i in range(1,len(srlists)-1):
            if(srlists[i].span != isCheckNone):
                if itemcode == 'kospi':
                    if len(srlists[i].find_all('td')) >= 2:
                        date = srlists[i].find_all("td")[0].text.replace('.','')
                        close_val = float(srlists[i].find_all("td")[1].text.replace(',',''))
                else:
                    srlists[i].td.text
                    date = srlists[i].find_all("td",align="center")[0].text.replace('.','') 
                    close_val = float(srlists[i].find_all("td",class_="num")[0].text.replace(',',''))
                if date > end_date:
                    continue               
                if date < start_date:
                    break  
                price = pd.Series([date, close_val], index = ['date','close_val'])
                df = df.append(price, ignore_index = True)
    
    df.date = pd.to_datetime(df.date, format='%Y%m%d')
    return df

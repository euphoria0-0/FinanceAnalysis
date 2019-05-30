#### 
import pandas as pd
import numpy as np
import re
import json
import sys
import datetime
import nltk
from konlpy.tag import Twitter 
tagger = Twitter()

### 프로그레스 바
def progressBar(value, endvalue, bar_length=20):
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()

####### 단어수세기 
### 길이 구하기
df_text = pd.read_excel('NAVER_report_text.xlsx')
x = []
for i in range(len(df_text)):
    txt = df_text.iloc[i]
    try:
        # 한글 + 영어
        x.append(len(txt['text'])+len(txt['text_en']))
    except:
        # 길이가 안 구해지면(None) 0
        x.append(0)

df_text['length'] = x.copy()

### 긍부정 단어 수 세기
df_dic = pd.read_csv('lexicon/polarity.csv')
df_dic = df_dic[['ngram', 'max.value']]

# 사전 전처리
dic = dict()
for idx in range(len(df_dic)):
    d = df_dic.iloc[idx]
    if ';' in d['ngram']:
        continue
    txt = re.sub("[^가-힣]",' ',d['ngram'])
    txt = re.sub(" ", '', txt)
    if len(txt) >= 2:
        dic[txt] = d['max.value']

# json 파일로 만들기
#pos_neg_dict = json.dumps(dic)
with open('DSC_FINAL/dict.json','w') as make_file:
    json.dump(dic, make_file, ensure_ascii=False, indent="\t")


### 긍부정 단어 세기
def count_pos_neg(textdata,pn_dict=None):
    start = datetime.datetime.now()
    
    json1_file = open('dict.json')
    json1_str = json1_file.read()
    pos_neg_dict = json.loads(json1_str)
    
    pos_cnt,neg_cnt,neut_cnt = [],[],[]
    # text데이터에서 명사 추출(오래걸림)
    for text in textdata:
        # 문서 토큰화
        text_token = tagger.morphs(text)
        text_token = [x for x in text_token if len(x)>=2]
        
        # 긍정/부정/중립 단어 수 세기
        pos,neg,neut = 0,0,0
        for word in text_token:
            if word in pos_neg_dict:
                np = pos_neg_dict.get(word)
                if np == "POS":
                    pos += 1
                elif np == "NEG":
                    neg += 1
                elif np == "NEUT":
                    neut += 1
                    
        pos_cnt.append(pos)
        neg_cnt.append(neg)
        neut_cnt.append(neut)
    
        progressBar(len(pos_cnt), len(textdata))
    
    end = datetime.datetime.now()
    print("\n걸린시간 : ",end-start)

    return pos_cnt, neg_cnt, neut_cnt


pos,neg,neut = count_pos_neg(df_text['text'])
df_text['pos'] = pos
df_text['neg'] = neg
df_text['neut'] = neut

### 영문 긍정/부정/중립 단어 수 세기
'''
def data_text_cleaning(data):
 
    # 소문자 변환
    no_capitals = only_english.lower().split()
 
    # 불용어 제거
    stops = set(stopwords.words('english'))
    no_stops = [word for word in no_capitals if not word in stops]
 
    # 어간 추출
    stemmer = nltk.stem.SnowballStemmer('english')
    stemmer_words = [stemmer.stem(word) for word in no_stops]
 
    # 공백으로 구분된 문자열로 결합하여 결과 반환
    return ' '.join(stemmer_words)

nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()
sid.polarity_scores("df_text['text_en'][2]")
'''

### 강조 단어 수 세기
# 강조 사전 다운
df_dic_it = pd.read_csv('lexicon/intensity.csv')
df_dic_it = df_dic[['ngram', 'max.value']]

# 강조 사전 전처리
dic_it = dict()
for idx in range(len(df_dic_it)):
    d = df_dic_it.iloc[idx]
    if ';' in d['ngram']:
        continue
    txt = re.sub("[^가-힣]",' ',d['ngram'])
    txt = re.sub(" ", '', txt)
    if len(txt) >= 2:
        dic_it[txt] = d['max.value']

# 강조 사전 json 파일로 만들기
with open('dict_intensity.json','w') as make_file:
    json.dump(dic_it, make_file, ensure_ascii=False, indent="\t")

# 강조 단어 세기
stopwords = ['일본','국가','캐릭터','지하철']

def count_intensity(textdata,pn_dict=None):
   
    json1_file = open('dict_intensity.json')
    json1_str = json1_file.read()
    intensity_dict = json.loads(json1_str)
    for word in stopwords:
        del intensity_dict[word]
    
    int_cnt = []
    # text데이터에서 형태소 추출
    for text in textdata:
        # 문서 토큰화
        text_token = tagger.morphs(text)
        text_token = [x for x in text_token if len(x)>=2]
        
        # 긍정/부정/중립 단어 수 세기
        intt = 0
        for word in text_token:
            if word in intensity_dict:
                np = intensity_dict.get(word)
                if np == "High":
                    intt += 1
                    
        int_cnt.append(intt)

    return int_cnt

intensity = count_intensity(df_text['text'])

df_text['intensity'] = intensity.copy()


writer = pd.ExcelWriter('report_text.xlsx')
df_text.to_excel(writer,'Sheet1', index = False)
writer.save()



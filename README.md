# 네이버 금융에서 주식과 리포트 분석하기

## 1. crawler_finance_stock_report.py
### 네이버 금융 크롤링
참고: https://finance.naver.com/
#### 1. 네이버 금융 주식 크롤링
참고: https://finance.naver.com/item/sise_day.nhn?code=005930
이 곳을 크롤링
#### 2. 네이버 금융 리포트 크롤링
1. 크롬 드라이버를 이용한 동적 크롤링으로 pdf 다운 링크 받기

~~친구에게 저작권이...~~
## 2. pdf_downloader.py
### pdf 다운로드
2. pdf 다운 링크로 pdf를 로컬에 다운로드
3. pdf의 텍스트 읽기
4. 텍스트 간단한 전처리(한글/영문)

~~친구에게 저작권이...~~
## 3. text_analyzer.py
긍정/부정/중립 단어 수 세기
1. 한글은 서울대학교 형태소 사전을 이용

참고: http://word.snu.ac.kr/kosac/index.php

한글은 강조하는 단어 수도 셌다.
2. 영문은 VADER 형태소 사전을 이용

참고: https://pypi.org/project/vaderSentiment/

## 4. text_visualization.py
참고: http://bokeh.pydata.org/en/latest/

bokeh의 다양한 시각화 라이브러리?를 이용하여
증권사 별 리포트의 긍부정 단어 비율을 보았음.

## 5. data_modeling.py
작성중zzz

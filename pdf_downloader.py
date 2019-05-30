import requests
import shutil
import pandas as pd

import sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
import io
import os

def pdfparser(data):
    #
    
    return data

def pdfread(dirname,savefolder=None):

    #

    return pdf_list

if __name__ == "__main__":
    pdfpath = 'report_pdf'
    downpath = 'report_pdf_text'
    
    df_excel = pd.read_excel('report.xlsx')
    df_pdf = df_excel['pdf']
    idx = 0

    #
    
    print('==========pdf read==========')
    
    # ex) ./temp, ./temp_text

    #   
    
    file_path = 'report_pdf_text'
    file_list = os.listdir(file_path)
    pdf_list = pd.DataFrame(columns = ['pdf','text'])
    le = len(file_list)
    
    for i, file in enumerate(file_list):
        if i % 10 == 0:
            print(str(len(pdf_list))+' / '+str(le))
        
        with open(file_path+'/'+file,'r', encoding='utf-8') as f:
            txt = f.read()
        
        txt_ko = re.sub("[^가-힣]",' ',txt)
        txt_ko = re.sub("  +",' ',txt_ko)
        x = pd.DataFrame({'pdf':[file[:17]], 'text':[txt_ko]})
        pdf_list = pd.concat([pdf_list, x], axis = 0)
        
    writer = pd.ExcelWriter('report_text_'+format(time.time(),'.0f')+'.xlsx')
    pdf_list.to_excel(writer, 'Sheet1', index = False)
    writer.save() 

        
        



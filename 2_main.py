if __name__ == "__main__":
    
    crp_list = ['삼성전자','SK하이닉스','삼성전자우','현대차','셀트리온','LG화학','현대모비스',
                'POSCO','신한지주','SK텔레콤','삼성바이오로직스','LG생활건강','NAVER','KB금융',
                '기아차','삼성물산','삼성에스디에스','한국전력','삼성생명','SK','삼성SDI',
                'SK이노베이션','KT&G','LG','삼성화재','LG전자','카카오','하나금융지주','엔씨소프트','S-Oil']
    
    for crpname in crp_list:
        
        start_date = '2009-01-01'
        end_date = '2019-06-30'
        filepath = crpname+'/'
        pdfpath = filepath+'pdf'
        txtpath = filepath+'text'
        if not os.path.exists(filepath):
            os.mkdir(filepath);os.mkdir(pdfpath);os.mkdir(txtpath)
        
        ### crawling
        df_excel = crawler(crpname, start_date, end_date)
        
        ### download pdf
        pdf_download(df_excel['pdf'], pdfpath)
        
        ### read text in pdf
        # multi processing
        pool = multiprocessing.Pool(processes=2)
        pool.map(pdfread, (filepath,))
        pool.close()
        pool.join()
        
        
        ### text preprocessing: extract text
        pdf_list = extract_txt(txtpath)
        
        print("Total <%d> Files"%len(os.listdir('data/'+crpname+'/text')))
        
        ### save text
        df_excel = pd.merge(df_excel, pdf_list, how = 'outer' )
        
        writer = pd.ExcelWriter(filepath+crpname+'_report_text.xlsx')
        df_excel.to_excel(writer, 'Sheet1', index = False)
        writer.save() 
    
        
    
    
#!/usr/bin/env python

import os
import sys
import re
import xlrd
import splinter
import tca as TCA #URT
import google_translater as G_TRANS
import time
import pandas as pd
import pygsheets
import numpy as np
import shutil 
from selenium import webdriver
from googletrans import Translator
from datetime import datetime, date, timedelta
from print_log import log_print,Emptyprintf

#PROJECT_IDS = [1429]
# PROJECT_IDS = [712, 746, 750]

ALL_PROBLEMS = "/media/sf_linux-share/all.txt"
PROBLEM = "~/Downloads/TCA.xlsx"
log = Emptyprintf

def isNaN(num):
    return num != num


def DF2List(df_in):
    train_data = np.array(df_in)#np.ndarray()
    df_2_list=train_data.tolist()#list
    return df_2_list



def TCA_upload_to_google(file, sheet, TCA_df):
    try:
        gc = pygsheets.authorize(service_file='PythonUpload-cfde37284cdc.json')
    except:
        return filename
    
    sh = gc.open(file)

    try:
        wks = sh.worksheet_by_title(sheet)
    except:
        wks = sh.add_worksheet(sheet,rows=1,cols=30,index=0)    
     
    wks.set_dataframe(TCA_df, (1, 1))
    '''
    sh = gc.open('Translation_Symptom')

    try:
        wks = sh.worksheet_by_title('data in')
    except:
        wks = sh.add_worksheet(gh_name,rows=510,cols=80,index=0)    
     
    wks.set_dataframe(En_df, (1, 1))
    '''
    return wks    

def TCA_download_from_google(file, sheet):

    try:
        gc = pygsheets.authorize(service_file='PythonUpload-cfde37284cdc.json')
    except:
        log("can not find json file")
    
    sh = gc.open(file)

    try:
        wks = sh.worksheet_by_title(sheet)
    except:
        wks = sh.add_worksheet(sheet,rows=1,cols=30,index=0)    
     
    df = wks.get_as_df()   
    
    return df    
    '''
    new_df = pd.DataFrame(columns=['Unique Reference Number','Claim RD Review Date','Workshop Name','Model No','Product No','Repair Result','Regular SW number IN','Regular SW number OUT','Total Spare Part Cost (1-4 + Small) (Local Currency)','Symptom Code 1','Workshop Comment','Fault Description Text'])
    df_column=new_df.columns.values.tolist()
    for i in df_column:
        new_df[i]=df[i]  
    
    #sh.del_worksheet(wks) # delete this wroksheet

    return new_df 
    '''

def download_from_google(file, sheet):
    try:
        gc = pygsheets.authorize(service_file='PythonUpload-cfde37284cdc.json')
    except:
        log("can not find json file")
    
    sh = gc.open(file)

    try:
        wks = sh.worksheet_by_title(sheet)
    except:
        wks = sh.add_worksheet(sheet,rows=1,cols=30,index=0)    
     
    df = wks.get_as_df()

    return df 


def filter_fault_description(df_in):
    df_in = df_in.str.replace("\n"," ")
    df_in = df_in.str.replace("\r"," ")
    df_in = df_in.str.replace("<br/>"," ")
    df_in = df_in.str.replace("&"," ")
    df_in = df_in.str.replace("#"," ")
    
    find_index = df_in.str.find("[symptom description]")
    print(find_index)
    
    n=0 
    for i in df_in:   
        print(n)    
        if (find_index[n]>0):

            df_in[n]=df_in[n][int(find_index[n])+22:]
        n=n+1
            
    find_index2 = df_in.str.find("[")
    n=0 
    for i in df_in:       
        if (find_index[n]>=0):
            df_in[n]=df_in[n][:int(find_index2[n])]
            print('new_str=',df_in[n])
        n=n+1
    
    return df_in           

    
def TCA_check_symptom(df_in):

    symptom_keyword_df=download_from_google('TCA2','symptom keyword')    

    symptom_keyword_df2 = symptom_keyword_df["symptom keyword"]
    symptom_df = symptom_keyword_df["symptom"]
    symptom_out_df = df_in.copy() #複製dataframe

    #find_index = df_in.str.find("audio")
    
    n=0 
    for i in symptom_out_df:         
        symptom_out_df[n] = ""
        n=n+1  
    
    for i in range(0, len(df_in)):  
        for j in range(0, len(symptom_keyword_df)):
            srt = symptom_keyword_df2[j]
            srt=str(srt)
            #print("srt=",srt)
            #print("m,n=",j,i)
            try:
                if (df_in[i].find(srt)>=0):
                    #print("symptom_df=",symptom_df[j])
                    symptom_out_df[i]=symptom_df[j]
                    #sel = input("pause")
                    break
            except:
                i=i            

    return symptom_out_df 
   

def main (args):
    global log
    config = 'config'
    print('args = ',args)
    projdata = []
    
    filename ='translation.xlsx'
    
    try:
        if (args[1]=="debug"):
           log = log_print
    except:
        log = Emptyprintf
 
    In_df=TCA_download_from_google('Translation','data in')  
    In_df['ErrorDescription'] = In_df['ErrorDescription'].str.lower() #全部字串都先轉成小寫
    log("main current_df=",In_df)    
    In_df2=In_df['ErrorDescription']
    In_df2 = filter_fault_description(In_df2)    
    #translated_df = Google_Translator("auto","en",In_df2)  
    translated_df = G_TRANS.Google_Translator("auto","en",In_df2)   
    In_df['ErrorDescription'] = translated_df
    
    out_df=TCA_check_symptom(In_df['ErrorDescription'])
    In_df.insert(In_df.shape[1],'symptom',out_df)      
    
    CURRENT_PACKAGE_DIRECTORY = os.path.abspath('.')    
    filename=os.path.join(CURRENT_PACKAGE_DIRECTORY,filename)
    In_df.to_excel(filename,index=False)          
    
    In_df=In_df.fillna("")   
    TCA_upload_to_google('Translation','data out',In_df) # upload to google sheet
    
    print("==============Done==============")
   
        
if __name__ == '__main__':
    main (sys.argv)

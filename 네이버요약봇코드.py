#모듈
import requests
import json
import numpy as np
import pandas as pd
import itertools #이중 리스트 풀기

#데이터 호출
with open (r'.\Comment_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_comm = pd.DataFrame(df_dict)
#한글, 공백 제외 모두 제거
df_comm['댓글'] = df_comm['댓글'].str.replace("[^ㄱ-ㅎ ㅏ-ㅣ 가-힣 ]", "").replace('',np.nan)
df_comm.dropna(how = 'any',inplace = True)

#분석에 사용할 df생성
df = df_comm[['댓글', '별점']]
temp = df[df['별점']<=3].index
df_p = df.drop(temp).reset_index(drop=True)
df_p = df_p[['댓글']]
temp = df[df['별점']>3].index
df_n = df.drop(temp).reset_index(drop=True)
df_n = df_n[['댓글']]

#댓글을 합칠 때, 2000자를 넘어가는 경우를 제어
def separate_2000(df):
    k = 0
    temp_list = []
    while k < len(df):
        sen_old = df['댓글'][k]
        for i in range(1,len(df)):
            if k+i == len(df):
                break
            print(k+i)
            sen_new = sen_old + ' ' + df['댓글'][k+i]
            if len(sen_new) >= 2000:
                break
            sen_old = sen_new
        temp_list.append(sen_old)
        k += i
    return temp_list

temp_list_p = separate_2000(df_p)
temp_list_n = separate_2000(df_n)

#%%
#결과 제출 시 API키 해지 예정 #유료 서비스
#API key
client_id = '90h0uvxm43'
client_secret = 'Var1ydjdxzqVkiPOpnOwcMbRuEvJd9RM4NtVr6zu'
url = 'https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize'
#네이버 요약기를 위한 헤더 선언
headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-NCP-APIGW-API-KEY-ID': client_id,
            'X-NCP-APIGW-API-KEY': client_secret
        }

#네이버 요약기 사용
def Summary(temp_list): #한번 사용할때마다 돈 나감
    summary_list = []
    for i in range(len(temp_list)):
        data = {
          "document": {
            "content": temp_list[i]
          },
          "option": {
            "language": "ko",
            "model": "general",
            "tone": 0,
            "summaryCount": 5
          }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data).encode('UTF-8'))
        rescode = response.status_code
        if(rescode == 200):
            print (response.text)
        else:
            print("Error : " + response.text)
        summary_list.append(response.text)
    return summary_list

#요약문을 합치고 그 결과를 대상으로 요약 ; 반복 ; 요약문이 매우 작아질때까지 반복하고, i=1일때 종료 #오류 제어
def Unlimited_Summary(summary_list_temp):
    for j in range(10000):
        T_summary_list = []
        for s in summary_list_temp:
            s = s.replace('{"summary":"', '').replace('"}', '').split('\\n')
            T_summary_list.append(s)
        
        T_summary_list = list(itertools.chain(*T_summary_list))
        
        k = 0
        temp_list = []
        while k < len(T_summary_list):
            sen_old = T_summary_list[k]
            for i in range(1,len(T_summary_list)):
                if k+i == len(T_summary_list):
                    break
                print(k+i)
                sen_new = sen_old + ' ' + T_summary_list[k+i]
                if len(sen_new) >= 2000:
                    break
                sen_old = sen_new
            temp_list.append(sen_old)
            k += i
        print(i)
        summary_list_temp = Summary(temp_list)
        if i == 1: #오류 방지
            return summary_list_temp[0].replace('{"summary":"', '').replace('"}', '').split('\\n')

#초기 요약
summary_list_p = Summary(temp_list_p)
summary_list_n = Summary(temp_list_n)

#무한 요약
Result_summary_p = Unlimited_Summary(summary_list_p)
Result_summary_n = Unlimited_Summary(summary_list_n)

#결과 출력
print("네이버 요약기 결과")
print('긍정 요약문\n', Result_summary_p)
print('부정 요약문\n', Result_summary_n)

df_naver = pd.DataFrame(zip(Result_summary_p, Result_summary_n), columns = ['긍정','부정'])
df_naver.to_json(r'.\Naver_Summary_DF.json')

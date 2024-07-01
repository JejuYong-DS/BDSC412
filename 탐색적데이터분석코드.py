#모듈
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
#%%#
#한글 폰트 오류 해결
from matplotlib import font_manager, rc
font_path = './malgun.ttf'
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

#Open DataBase
with open (r'.\Unique_Num_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_unique_num = pd.DataFrame(df_dict)

with open (r'.\Product_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_product = pd.DataFrame(df_dict)

with open (r'.\Comment_Preprocessed_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_comm_preprocessed = pd.DataFrame(df_dict)

#데이터 확인
df_unique_num.info() ; df_unique_num.describe()
df_product.info() ; df_product.describe()
df_comm_preprocessed.info() ; df_comm_preprocessed.describe()

#%%#빈도 분석
#품목별 제품 빈도 분석
print(df_product['품목종류번호'].value_counts())
fig, ax = plt.subplots()
fig.suptitle('품목별 제품 빈도 분석')
colors = ['#505050','#686868', '#808080', '#A0A0A0', '#B0B0B0', '#C0C0C0'] #흑백 그라데이션
ax.bar([0,1,2,3,4,5], df_product['품목종류번호'].value_counts() , color = colors)
plt.xticks([0,1,2,3,4,5] , ['상의', '바지', '아우터', '양말/레그웨어', '스커트', '원피스'])
plt.show()

#제품 성별 빈도 분석
fig, ax = plt.subplots()
fig.suptitle('제품 성별 빈도 분석')
colors = ['#2020A0', '#DC143C', '#202020'] #파랑 빨강 검정
ax.bar([0,2,1], df_product['제품성별'].value_counts() , color = colors )
plt.xticks([0,2,1] , ['남','여','공용'])
plt.show()

#별점 빈도 분석
fig, ax = plt.subplots()
fig.suptitle('별점 빈도 분석')
colors = ['#1E90FF', '#87CEFA', '#F08080', '#A52A2A', '#DC143C']
ax.bar([0,1,2,3,4], df_comm_preprocessed['별점'].value_counts() , color = colors)
plt.xticks([0,1,2,3,4] , ['5점','4점', '3점','2점','1점'])
plt.show()
print(df_comm_preprocessed['별점'].value_counts())

#감정별 빈도 분석
fig, ax = plt.subplots()
fig.suptitle('감정별 빈도 분석')
colors = ['#2020A0', '#DC143C'] #파랑 빨강
ax.bar([0,1], df_comm_preprocessed['emotion'].value_counts() , color = colors )
plt.xticks([0,1] , ['긍정','부정'])
plt.show()

#%%
#품사 태깅 확인
for i in range(5):
    print(str(i+1), df_comm_preprocessed['pos'][i],'\n')

#%%#시각화를 위한 연산
#문장 길이 측정
def text_len(df_temp):
    #문장 길이 측정
    sr_pos_text_len = df_temp[df_temp['emotion']==1]['tokenized'].map(lambda x: len(x))
    sr_neg_text_len = df_temp[df_temp['emotion']==0]['tokenized'].map(lambda x: len(x))
    print('긍정 댓글 평균 길이 :', round(np.mean(sr_pos_text_len), 1))
    print('부정 댓글 평균 길이 :', round(np.mean(sr_neg_text_len), 1))
    return sr_pos_text_len, sr_neg_text_len

#단어 빈도 확인
def counter_token(df_temp, num, word):
    #Counter 모듈
    pos_words = np.hstack(df_temp[df_temp.emotion == 1][word].values)
    neg_words = np.hstack(df_temp[df_temp.emotion == 0][word].values)
    pos_count = Counter(pos_words)
    neg_count = Counter(neg_words)
    #가장 많이 나온 단어 15선
    print('가장 많이 나온 단어',num,'개')
    print('긍정\n', pos_count.most_common(num))
    print('\n부정\n', neg_count.most_common(num))
    #출력은 리스트로, return값은 Dict로 
    return dict(pos_count.most_common(num)), dict(neg_count.most_common(num))

#%%#그래프 함수
#sr1은 긍정문서 시리즈, sr2는 부정문서 시리즈
#댓글 길이 히스토그램
def text_len_plt(sr1, sr2, title = ''):
    #시각화    
    fig,(ax1,ax2) = plt.subplots(1,2,figsize=(10,5))
    fig.suptitle('댓글 길이 ' + title + ' by 히스토그램')
    #긍정 댓글
    ax1.hist(sr1, color='blue')
    ax1.set_title('긍정 댓글')
    ax1.set_xlabel('댓글 길이')
    ax1.set_ylabel('샘플 수')
    #부정 댓글
    ax2.hist(sr2, color='red')
    ax2.set_title('부정 댓글')
    ax2.set_xlabel('댓글 길이')
    ax2.set_ylabel('샘플 수')
    #그래프 출력
    plt.show()

#댓글 길이 박스플롯
def box_plot_plt(sr_1, sr_2, title = ''):    
    fig,(ax1,ax2) = plt.subplots(1,2,figsize=(10,5))
    fig.suptitle('댓글 길이 ' + title +' by 박스플롯')
    ax1.boxplot(sr_1)
    ax1.set_title('긍정 댓글')
    ax2.boxplot(sr_2)
    ax2.set_title('부정 댓글')
    #그래프 출력
    plt.show()

#워드 클라우드
def wordcloud_def(dict1):
    wc = WordCloud(font_path=font_path, width = 200, height = 200, max_font_size=60, background_color='white', colormap = 'Greens', ).generate_from_frequencies(dict1)
    plt.figure()
    plt.imshow(wc)
    plt.axis('off')

#%%#데이터베이스 시각화 결과
#문장 길이
sr_pos_, sr_neg_ = text_len(df_comm_preprocessed)
#박스플롯
box_plot_plt(sr_pos_, sr_neg_)
#문장길이 시각화
text_len_plt(sr_pos_, sr_neg_)

#단어 빈도 분석
#형태소
dict_pos_token, dict_neg_token = counter_token(df_comm_preprocessed, num = 20, word='tokenized')
wordcloud_def(dict_pos_token) ; wordcloud_def(dict_neg_token)
#명사
dict_pos_noun, dict_neg_noun = counter_token(df_comm_preprocessed, num = 20, word='noun')
wordcloud_def(dict_pos_noun) ; wordcloud_def(dict_neg_noun)

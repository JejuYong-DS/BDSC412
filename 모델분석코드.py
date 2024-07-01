#모듈
import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import math
from sklearn.preprocessing import normalize
#%%#
#한글 폰트 오류 해결
from matplotlib import font_manager, rc
font_path = './malgun.ttf'
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

#Open DataBase
with open (r'.\Comment_Preprocessed_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_comm_preprocessed = pd.DataFrame(df_dict)

#데이터 확인
df_comm_preprocessed.info() ; df_comm_preprocessed.describe()

df = df_comm_preprocessed

#%%# 잠재 의미 분석 LSA
def LSA_topic_modeling(df_temp, topic, n): #topic은 토픽 개수(상위 t개), n은 한 토픽에 들어갈 단어의 개수
    #TF-IDF행렬 만들기
    vectorizer = TfidfVectorizer(smooth_idf = True)
    Tf_Idf_matrix = vectorizer.fit_transform(df_temp['noun_sen'])
    
    #절단된 SVD
    #U, s, VT = np.linalg.svd(Tf_Idf_matrix)
    svd_model = TruncatedSVD(n_components=topic, algorithm='randomized', n_iter=100, random_state=0)
    svd_model.fit(Tf_Idf_matrix)
    #토픽 개수
    print('토픽 개수 :',len(svd_model.components_))
    
    #토픽 결과 출력
    terms = vectorizer.get_feature_names()
    topic_list = []
    for topic, comp in enumerate(svd_model.components_):
        print(topic+1,'번째 토픽 :', [(terms[topic], comp[topic].round(4)) for topic in comp.argsort()[:-n - 1:-1]])
        topic_sentence = ' '.join([terms[topic] for topic in comp.argsort()[:-n - 1:-1]])
        topic_list.append(topic_sentence)
    return topic_list

#LSA 기반 토픽모델링 결과 출력
LSA_topic_modeling(df[df.emotion == 1], 5, 7)
LSA_topic_modeling(df[df.emotion == 0], 5, 7)

#%%# TextRank 분석
#분석에 사용할 df생성
temp = df[df['emotion']!=1].index
df_p = df_comm_preprocessed.drop(temp).reset_index(drop=True)
df_p = df_p[['댓글','tokenized']]
temp = df[df['emotion']!=0].index
df_n = df.drop(temp).reset_index(drop=True)
df_n = df_n[['댓글','tokenized']]

#weightedGraph 연산
def weightedGraph_(df_temp):
    similarity_matrix = []
    for i, row_i in df_temp.iterrows():
        i_row_vec = []
        for j,row_j in df_temp.iterrows():
            if i == j:
                i_row_vec.append(0.0)
            else:
                intersection = len(set(row_i['tokenized'])&set(row_j['tokenized']))
                log_i = math.log1p(len(set(row_i['tokenized'])))
                log_j = math.log1p(len(set(row_j['tokenized'])))
                similarity = intersection/(log_i + log_j)
                i_row_vec.append(similarity)
        similarity_matrix.append(i_row_vec)
        #현재 진행 상황
        print(round(i/len(df_temp)*100,2),'%')
    
    return np.array(similarity_matrix)

#pagerank 계산
def pagerank(x, df=0.85, max_iter=30):
    assert 0 < df < 1
    # initialize
    A = normalize(x, axis=0, norm='l1')
    R = np.ones(A.shape[0]).reshape(-1,1)
    bias = (1 - df) * np.ones(A.shape[0]).reshape(-1,1)
    # iteration
    for _ in range(max_iter):
        R = df * (A * R) + bias
    return R

#TextRank 출력함수 num:댓글 수
def TextRank(df_temp, weightedGraph, num):
    R = pagerank(weightedGraph) # pagerank를 돌려서 rank matrix 반환
    R = R.sum(axis=1) # 반환된 matrix를 row 별로 sum 
    indexs = R.argsort()[-10:] # 해당 rank 값을 sort, 값이 높은 10개의 문장 index를 반환
    indexs = sorted(indexs)[:num] # sorted 하는 이유는 원래 문장 순서에 맞춰 보여주기 위함
    
    res_list = []
    for index in indexs: 
        print(df_temp['댓글'][index],'\n') #rank값이 높은 문장을 프린트
        res_list.append(df_temp['댓글'][index])

#weightedGraph 정의
weightedGraph_p = weightedGraph_(df_p)
weightedGraph_n = weightedGraph_(df_n)

#TextRank 결과 출력
print('positive')
TextRank(df_p, weightedGraph_p, num = 4)
print('negative')
TextRank(df_n, weightedGraph_n, num = 4)

#!pip install git+https://github.com/haven-jeon/PyKoSpacing.git
#!pip install git+https://github.com/ssut/py-hanspell.git
#!pip install konlpy
import json
import numpy as np
import pandas as pd
import requests #spell_checker 선행
from pykospacing import Spacing #띄어쓰기 교정 모듈
from hanspell import spell_checker #맞춤법 교정 모듈
from konlpy.tag import Okt

with open (r'.\Comment_DF.json', 'r') as file:
    df_comm_dict = json.load(file)
    df_comm = pd.DataFrame(df_comm_dict)

df_comm.info() ; df_comm.describe()
#%%
#교정
#한글, 공백 제외 모두 제거
df_comm['댓글'] = df_comm['댓글'].str.replace("[^ㄱ-ㅎ ㅏ-ㅣ 가-힣 ]", "").replace('',np.nan)
df_comm.dropna(how = 'any',inplace = True)
df_comm.info()

#띄어쓰기 교정
spacing = Spacing()
for i in range(len(df_comm)):
    df_comm['댓글'][i] = spacing(df_comm['댓글'][i])
    #현재 진행 상황
    print(round(i/len(df_comm)*100,2),'%')

#맞춤법 교정,,, 네이버 맞춤법 검사기 기반 제작된 패키지,,,
for i in range(len(df_comm)):
    df_comm['댓글'][i] = spell_checker.check(df_comm['댓글'][i]).checked
    #현재 진행 상황
    print(round(i/len(df_comm)*100,2),'%')

#저장 #토큰화 및 불용어 처리 이전 데이터베이스 #백업파일
#df_comm.to_json(r'.\Comment_Preprocessing_DF.json')

with open (r'.\Comment_Preprocessing_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_comm = pd.DataFrame(df_dict)

#%%
#토큰화
okt = Okt()

df_comm['noun']=''
df_comm['pos']=''
df_comm['tokenized'] = ''

for i in range(len(df_comm)):
    df_comm['noun'][i]=okt.nouns(df_comm['댓글'][i])
    df_comm['pos'][i] = okt.pos(df_comm['댓글'][i],stem = True)
    df_comm['tokenized'][i] = okt.morphs(df_comm['댓글'][i], stem = True)#stem = True로 좋습니다 좋아요 등을 정제
    #현재 진행 상황
    print(round(i/len(df_comm)*100,2),'%')

#불용어 처리 @[텍스트마이닝을 위한 한국어 불용어 목록 연구] 논문 인용
stopwords_list = '''가량, 가지, 각, 간, 갖은, 개, 개국, 개년, 개소, 개월, 걔, 거, 거기, 거리, 건, 것, 겨를, 격,
겸, 고, 군, 군데, 권, 그, 그거, 그것, 그곳, 그까짓, 그네, 그녀, 그놈, 그대, 그래, 그래도,
그서, 그러나, 그러니, 그러니까, 그러다가, 그러면, 그러면서, 그러므로, 그러자, 그런, 그런데,
 그럼, 그렇지만, 그루, 그리고, 그리하여, 그분, 그이, 그쪽, 근, 근데, 글쎄, 글쎄요, 기,
김, 나, 나름, 나위, 남짓, 내, 냥, 너, 너희, 네, 네놈, 녀석, 년, 년대, 년도, 놈, 누구, 니,
다른, 다만, 단, 달, 달러, 당신, 대, 대로, 더구나, 더욱이, 데, 도, 동, 되, 두, 두세, 두어,
둥, 듯, 듯이, 등, 등등, 등지, 따라서, 따름, 따위, 딴, 때문, 또, 또는, 또한, 리, 마당, 마련,
마리, 만, 만큼, 말, 매, 맨, 명, 몇, 몇몇, 모, 모금, 모든, 무렵, 무슨, 무엇, 뭐, 뭣, 미터,
및, 바, 바람, 바퀴, 박, 발, 발짝, 번, 벌, 법, 별, 본, 부, 분, 뻔, 뿐, 살, 새, 서너, 석, 설,
섬, 세, 세기, 셈, 쇤네, 수, 순, 스무, 승, 시, 시간, 식, 씨, 아, 아냐, 아니, 아니야, 아무,
아무개, 아무런, 아아, 아이, 아이고, 아이구, 야, 약, 양, 얘, 어, 어느, 어디, 어머, 언제, 에이,
엔, 여기, 여느, 여러, 여러분, 여보, 여보세요, 여지, 역시, 예, 옛, 오, 오랜, 오히려, 온, 온갖,
올, 왜냐하면, 왠, 외, 요, 우리, 원, 월, 웬, 위, 음, 응, 이, 이거, 이것, 이곳, 이놈, 이래,
이런, 이런저런, 이른바, 이리하여, 이쪽, 일, 일대, 임마, 자, 자기, 자네, 장, 저, 저것, 저기,
저놈, 저런, 저쪽, 저편, 저희, 적, 전, 점, 제, 조, 주, 주년, 주일, 줄, 중, 즈음, 즉, 지, 지경,
지난, 집, 짝, 쪽, 쯤, 차, 참, 채, 척, 첫, 체, 초, 총, 측, 치, 큰, 킬로미터, 타, 터, 턱, 톤,
통, 투, 판, 퍼센트, 편, 평, 푼, 하기야, 하긴, 하물며, 하지만, 한, 한두, 한편, 허허, 헌, 현,
호, 혹은, 회, 흥'''.replace('\n', ' ').split(', ')
#추가할 불용어
stopwords_add_list = '''은, 는, 이, 가, 을, 를, 에, 다, 으로, 로, 입니다, 하다, 무탠, 다드'''.replace('\n', ' ').split(', ')
stopwords_list += stopwords_add_list
#불용어리스트 저장
with open(r".\불용어리스트.txt", "w") as f:
    for word in stopwords_list:
        f.write(word+'\n')
#불용어처리 시작
df_comm['noun'] = df_comm['noun'].apply(lambda x: [item for item in x if item not in stopwords_list])

df_comm['tokenized'] = df_comm['tokenized'].apply(lambda x: [item for item in x if item not in stopwords_list])
print('불용어 처리 완료')

#명사 역토큰화 ; 전처리된 명사 단어를 다시 조합
df_comm['noun_sen'] = ''
for i in range(len(df_comm)):
    df_comm['noun_sen'][i] = ' '.join(df_comm['noun'][i])

#감정 분류; 별점 0(1,2,3) vs 1(4,5)
df_comm['emotion'] = np.select([df_comm.별점 > 3], [1], default = 0)

#저장
df_comm.to_json(r'.\Comment_Preprocessed_DF.json')

with open (r'.\Comment_Preprocessed_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_comm_preprocessed = pd.DataFrame(df_dict)

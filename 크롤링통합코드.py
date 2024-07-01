################BDSC412 고주용 기석주 통합 코드################
####본 코드의 저작권은 고주용, 기석주에게 있음
####제품고유번호추출, 제품정보추출, 제품댓글추출
####제품고유번호를 통해 제품에 대한 URL을 크롤링, 얻은 URL을 바탕으로 제품정보추출 및 DB구축
####제품댓글추출은 제품 페이지 내 동적페이지(댓글 등)인 부분이 있어서, 구매후기게시판에서 데이터 마이닝.
#### \ 구매후기게시판을 통해 제품고유번호, 작성자, 댓글, 평점 데이터 추출 및 DB구축
#%%#
#모듈
import requests
from bs4 import BeautifulSoup as bs
import time, random
import pandas as pd
import json

#%%#
#제품고유번호추출

#헤더
header = { 
    "User-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42",
}

#분류 코드
Classification_Code = ['002', '003', '001', '008', '022', '020'] #순서대로 아우터, 바지, 상의, 양말/레그웨어, 스커트, 원피스
unique_num_list = []
class_code_list = []

#크롤링
for classification_code in Classification_Code:    
    page = 0
    while True:
        page += 1
        #현재 진행 상황
        print('page :', page, 'Class_Code :', classification_code)
        
        #사이트의 감시를 피하기 위해 사용
        time.sleep(random.sample(range(3), 1)[0])
        #URL
        url = 'https://www.musinsa.com/brands/musinsastandard?category3DepthCodes=&category2DepthCodes=&category1DepthCode=' + classification_code + '&colorCodes=&startPrice=&endPrice=&exclusiveYn=&includeSoldOut=&saleGoods=&timeSale=&includeKeywords=&sortCode=NEW&tags=&page=' + str(page) + '&size=90&listViewType=small&campaignCode=&groupSale=&outletGoods=&boutiqueGoods='
        resp = requests.get(url, timeout = 5, headers=header).text
        soup = bs(resp, 'html.parser')
        
        soup_unique = soup.find_all(class_='list_info')
        #크롤링 할 대상이 없을 때, 정지 코드
        if soup_unique == []:
            break
        
        #고유번호 추출코드
        for n in soup_unique:
            #고유번호
            #n.text는 인덱스 오류 발생 #IndexError: list index out of range
            unique_num = str(n).split("goods/")[1].split('"')[0]
            
            #리스트에 저장
            unique_num_list.append(unique_num)
            class_code_list.append(classification_code)
            #결과 출력
            print("추출한 제품 코드 :", unique_num)
            
#데이터프레임으로 저장
df_unique_num = pd.concat([pd.DataFrame(unique_num_list),pd.DataFrame(class_code_list)], axis = 1)
df_unique_num.columns = ['Unique_Code','Class_Code']
df_unique_num.drop_duplicates(subset=['Unique_Code'], inplace = True) #중복 제거

#JSON으로 저장
df_unique_num.to_json(r'.\Unique_Num_DF.json')
#df_unique_num.info() ; df_unique_num.describe()

time.sleep(10) #이건 그냥 넣고싶었음

#JSON으로 열기, read_json은 str형태의 숫자 데이터가 int형태로 바뀜에 따라 사용 불가. 따라서 해당 코드로 사용.
with open (r'.\Unique_Num_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_unique_num = pd.DataFrame(df_dict)

#%%#
#제품정보추출

unique_num_list = df_unique_num['Unique_Code'].values.tolist()
class_code_list = df_unique_num['Class_Code'].values.tolist()

main_list = []
for num, classification, i in zip(unique_num_list, class_code_list, range(len(unique_num_list))):
    #사이트의 감시를 피하기 위해 사용
    time.sleep(random.sample(range(3), 1)[0])
    
    #현재 진행 상황
    print(str(round(i/len(unique_num_list)*100, 1)) + '%')

    #URL 연결
    main_url = "https://www.musinsa.com/app/goods/" + num
    resp = requests.get(main_url, timeout = 5, headers=header).text ; soup = bs(resp, 'html.parser')
    print("URL :",main_url)
    
    #제품명
    goods_name = soup.find(class_='product_title').text.replace('\n','')
    #print(" 제품명 :", goods_name)
    #제품명 임시 전처리
    while True:
        if '(' in goods_name:
            temp = goods_name.split('(')[1].split(')')[0]
            goods_name = goods_name.replace('('+temp+')','')
        elif '[' in goods_name:
            temp = goods_name.split('[')[1].split(']')[0]
            goods_name = goods_name.replace('['+temp+']','')
        else :
            goods_name = goods_name.strip()
            break
    #print(" 전처리 후 제품명 :", goods_name)
    
    #제품 성별 추출
    product_sex = soup.select_one('span.txt_gender').text.replace('\n','').strip()
    #print(' 제품 성별 :', product_sex)

    #리스트 통합
    temp_list = [num, classification, goods_name, product_sex]
    main_list.append(temp_list)


#데이터 프레임 구축
df_product = pd.DataFrame(main_list, columns = ['고유번호', '품목종류번호', '제품명', '제품성별'])
df_product.drop_duplicates(subset=['고유번호'], inplace = True) #중복 제거

#JSON으로 저장
df_product.to_json(r'.\Product_DF.json')
df_product.info() ; df_product.describe()

time.sleep(10)
#JSON으로 열기
with open (r'.\Product_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_product = pd.DataFrame(df_dict)
    
#%%#
#제품댓글추출

unique_num_list = df_unique_num['Unique_Code'].values.tolist()

page = 0
df_comm = pd.DataFrame([], columns = ['고유번호', '닉네임', '댓글', '별점'])
while True:
    page += 1
    #현재 진행 상황
    print('Page :', page, '진행도 :', str(round(page/10,3))+'%')
    
    #사이트의 감시를 피하기 위해 사용
    time.sleep(random.sample(range(3), 1)[0])
    time.sleep(random.sample(range(3), 1)[0])
    #구매후기게시판 URL
    comm_url = 'https://www.musinsa.com/app/reviews/lists?type=&year_date=2022&month_date=&day_date=&max_rt=2022&min_rt=2009&brand=musinsastandard&page='+ str(page) +'&sort=new&hash_id=&best_type=&s_type=all&q='
    c_resp = requests.get(comm_url, timeout = 5, headers=header).text ; comm_soup = bs(c_resp, 'html.parser')
    review_list = comm_soup.find_all(class_="review-list")

    #스크래핑 할 대상이 없을 때, 정지 코드. 그러나 구현하기 너무 힘들다,,, 대체제로 10000페이지 되면 종료
    if page == 7600:    #if soup_unique == []: #이쯤에서 크롤링 막힘,, 총 10만개의 데이터가 크롤링 되었으나 90%가 중복 데이터. 총 11961개의 데이터를 이용
        print('댓글 스크래핑 정지')
        break

    temp_main = []
    #스크래핑
    for review in review_list :
        #제품 코드 == unique_code
        item_code = str(review.find(class_ = "review-goods-information__link")).split("goods/")[1].split('/0')[0]
        
        #데이터 프레임에 없는 상품 제거
        if item_code not in unique_num_list:
            print(item_code,'제거')
            continue
        
        #사용자 닉네임
        user_ID = review.select_one(".review-profile__name").get_text().strip().replace('\n','')
        user_ID = user_ID[5:].replace(" ", "")

        #댓글
        comm = review.select_one(".review-contents__text").get_text().strip().replace('\n','')


        #별점
        rating = str(review.find(class_="review-list__rating__active")).split('style="width: ')[1].split('%')[0]
        rating = int(int(rating)/20) #별점을 1,2,3,4,5 로 만든다
        
        #리스트 통합
        temp_list = [item_code, user_ID, comm, rating]
        temp_main.append(temp_list)
        
    #데이터프레임 생성
    df_temp = pd.DataFrame(temp_main, columns = ['고유번호', '닉네임', '댓글', '별점'])
    df_comm = pd.concat([df_comm, df_temp])
    

#댓글 데이터프레임 완성
df_comm.reset_index(drop = True, inplace = True)
df_comm.drop_duplicates(subset=['댓글'], inplace = True) #중복 제거
df_comm.reset_index(drop = True, inplace = True) #중복 제거 후 다시
df_comm.info() ; df_comm.describe()

#JSON으로 저장
df_comm.to_json(r'.\Comment_DF.json')

#JSON으로 열기
with open (r'.\Comment_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_comm = pd.DataFrame(df_dict)
    
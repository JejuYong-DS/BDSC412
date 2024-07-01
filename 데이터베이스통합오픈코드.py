#모듈
import json
import pandas as pd
#%%
#Open DataBase
with open (r'.\Unique_Num_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_unique_num = pd.DataFrame(df_dict)

with open (r'.\Product_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_product = pd.DataFrame(df_dict)

with open (r'.\Comment_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_comm = pd.DataFrame(df_dict)

with open (r'.\Comment_Preprocessing_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_comm_preprocessing = pd.DataFrame(df_dict)

with open (r'.\Comment_Preprocessed_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_comm_preprocessed = pd.DataFrame(df_dict)

with open (r'.\Naver_Summary_DF.json', 'r') as file:
    df_dict = json.load(file)
    df_naver = pd.DataFrame(df_dict)
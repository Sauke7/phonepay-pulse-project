import pandas as pd
import json
import os
path="C:/phonepayproject/pulse/data/map/insurance/hover/country/india/state/"
map_state_list=os.listdir(path)
map_state_list
clm={'State':[], 'Year':[],'Quater':[],'district_name':[], 'district_count':[], 'district_Transacion_amount':[]}

for i in map_state_list:
    p_i=path+i+"/"
    map_yr=os.listdir(p_i)
    for j in map_yr:
        p_j=p_i+j+"/"
        map_yr_list=os.listdir(p_j)
        for k in map_yr_list:
            p_k=p_j+k
            Data=open(p_k,'r')
            D=json.load(Data)
            data_section = D.get('data', {})
            hover_Data_List =  data_section.get('hoverDataList')
            for z in hover_Data_List :
              Name=z['name']
              count=z['metric'][0]['count']
              amount=z['metric'][0]['amount']
              clm['district_name'].append(Name)
              clm['district_count'].append(count)
              clm['district_Transacion_amount'].append(amount)
              clm['State'].append(i)
              clm['Year'].append(j)
              clm['Quater'].append(int(k.strip('.json')))
map_insur=pd.DataFrame(clm)
print(map_insur)

import mysql.connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="k.dybalasai",
    database="phonepay"
)
mycursor = mydb.cursor()
cursor = mydb.cursor()
cursor.execute("USE phonepay")
mycursor.execute("""
CREATE TABLE IF NOT EXISTS map_insur (
    State VARCHAR(50),
    Year INT,
    Quater INT,
    district_name VARCHAR(50),
    district_count BIGINT,
    district_Transacion_amount BIGINT
)
""")

query = """
INSERT INTO map_insur
(State, Year, Quater, district_name, district_count, district_Transacion_amount)
VALUES (%s, %s, %s, %s, %s, %s)
"""

values = [tuple(x) for x in map_insur.to_numpy()]

mycursor.executemany(query, values)
mydb.commit()   
print("✅ Data inserted successfully into map_insur table")
query = """
SELECT * FROM map_trans LIMIT 10;
"""

mycursor.execute(query)
result = mycursor.fetchall()
for row in result:
    print(row)

# cursor.execute("DROP TABLE IF EXISTS map_insur;")
# mydb.commit()

# print("✅ map_insur table dropped successfully")
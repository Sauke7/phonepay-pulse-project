import pandas as pd
import json
import os
path="C:/phonepayproject/pulse/data/aggregated/insurance/country/india/state/"
inc_state_list=os.listdir(path)
inc_state_list
clm={'State':[], 'Year':[],'Quater':[],'Transacion_type':[], 'Transacion_count':[], 'Transacion_amount':[]}

for i in inc_state_list:
    p_i=path+i+"/"
    inc_yr=os.listdir(p_i)
    for j in inc_yr:
        p_j=p_i+j+"/"
        inc_yr_list=os.listdir(p_j)
        for k in inc_yr_list:
            p_k=p_j+k
            Data=open(p_k,'r')
            D=json.load(Data)
            for z in D['data']['transactionData']:
              Name=z['name']
              count=z['paymentInstruments'][0]['count']
              amount=z['paymentInstruments'][0]['amount']
              clm['Transacion_type'].append(Name)
              clm['Transacion_count'].append(count)
              clm['Transacion_amount'].append(amount)
              clm['State'].append(i)
              clm['Year'].append(j)
              clm['Quater'].append(int(k.strip('.json')))
              
Agg_insure=pd.DataFrame(clm)
print(Agg_insure)

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
CREATE TABLE IF NOT EXISTS Aggre_insure (
    State VARCHAR(50),
    Year INT,
    Quater INT,
    Transacion_type VARCHAR(50),
    Transacion_count BIGINT,
    Transacion_amount BIGINT
)
""")

query = """
INSERT INTO Aggre_insure
(State, Year, Quater, Transacion_type, Transacion_count, Transacion_amount)
VALUES (%s, %s, %s, %s, %s, %s)
"""

values = [tuple(x) for x in Agg_insure.to_numpy()]

mycursor.executemany(query, values)
mydb.commit()   
print("✅ Data inserted successfully into Aggre_insure table")
# query = """
#  SELECT * FROM Aggre_insure LIMIT 10;
#  """

# mycursor.execute(query)
# result = mycursor.fetchall()
# for row in result:
#     print(row)

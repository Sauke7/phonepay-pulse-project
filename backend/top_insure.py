import pandas as pd
import json
import os

path = "C:/phonepayproject/pulse/data/top/insurance/country/india/"
top_state_list = os.listdir(path)   

clm = {
    'State': [],
    'Year': [],
    'Quater': [],
    'district_count': [],
    'district_Transacion_amount': []
}

for j in top_state_list:                 
    p_j = os.path.join(path, j)

    if not os.path.isdir(p_j):
        continue

    for k in os.listdir(p_j):              
        p_k = os.path.join(p_j, k)

        if not p_k.endswith('.json'):
            continue

        with open(p_k, 'r') as Data:
            D = json.load(Data)

        states_list = D['data'].get('states')
        if states_list is None:
            continue

        for values in states_list:
            clm['State'].append(values['entityName'])
            clm['district_count'].append(values['metric']['count'])
            clm['district_Transacion_amount'].append(values['metric']['amount'])
            clm['Year'].append(j)
            clm['Quater'].append(int(k.strip('.json')))

top_insure = pd.DataFrame(clm)
print(top_insure)

import mysql.connector
mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "k.dybalasai",
        database = "phonepay",
        autocommit = True )
mycursor = mydb.cursor()
cursor = mydb.cursor()
cursor.execute("USE phonepay")
mycursor.execute("""
CREATE TABLE IF NOT EXISTS top_insure (
    State VARCHAR(50),
    Year INT,
    Quater INT,
    district_count BIGINT,
    district_Transacion_amount BIGINT
)
""")

query = """
INSERT INTO top_insure
(State, Year, Quater, district_count, district_Transacion_amount)
VALUES (%s, %s, %s, %s, %s)
"""

values = [tuple(x) for x in top_insure.to_numpy()]

mycursor.executemany(query, values)
mydb.commit()   
print("✅ Data inserted successfully top_insure into  table")
query = """
SELECT * FROM top_insure LIMIT 10;
"""

mycursor.execute(query)
result = mycursor.fetchall()
for row in result:
    print(row)
import pandas as pd
import json
import os

path = "C:/phonepayproject/pulse/data/top/user/country/india/"
top_state_list = os.listdir(path)   

clm = {
    'State': [],
    'Year': [],
    'Quater': [],
    'registeredUsers': []
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
            clm['State'].append(values['name'])
            clm['registeredUsers'].append(values['registeredUsers'])
            clm['Year'].append(j)
            clm['Quater'].append(int(k.strip('.json')))

top_user = pd.DataFrame(clm)
print(top_user)

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
CREATE TABLE IF NOT EXISTS top_user (
    State VARCHAR(50),
    Year INT,
    Quater INT,
    registeredUsers BIGINT
)
""")

query = """
INSERT INTO top_user
(State, Year, Quater, registeredUsers)
VALUES (%s, %s, %s, %s)
"""

values = [tuple(x) for x in top_user.to_numpy()]

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


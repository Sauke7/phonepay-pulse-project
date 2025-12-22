import pandas as pd
import json
import os

path = "C:/phonepayproject/pulse/data/map/user/hover/country/india/state/"
map_state_list = os.listdir(path)

clm = {
    'State': [],
    'District': [],
    'Year': [],
    'Quater': [],
    'app_opens': [],
    'district_registeredUsers': []
}

for i in map_state_list:
    p_i = os.path.join(path, i)

    for j in os.listdir(p_i):
        p_j = os.path.join(p_i, j)

        for k in os.listdir(p_j):
            p_k = os.path.join(p_j, k)

            with open(p_k, 'r') as Data:
                D = json.load(Data)

            hover_data = D.get('data', {}).get('hoverData')
            if hover_data is None:
                continue

            for district, values in hover_data.items():
                clm['State'].append(i)
                clm['District'].append(district)
                clm['Year'].append(j)
                clm['Quater'].append(int(k.strip('.json')))
                clm['app_opens'].append(values['appOpens'])
                clm['district_registeredUsers'].append(values['registeredUsers'])

map_user = pd.DataFrame(clm)
print(map_user.head())


import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="k.dybalasai",
    database="phonepay"
)

cursor = mydb.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS map_user (
    State VARCHAR(50),
    District VARCHAR(100),
    Year INT,
    Quater INT,
    appOpens BIGINT,
    district_registeredUsers BIGINT
);
""")

query = """
INSERT INTO map_user
(State, District, Year, Quater, appOpens, district_registeredUsers)
VALUES (%s, %s, %s, %s, %s, %s)
"""

values = [tuple(x) for x in map_user.to_numpy()]
cursor.executemany(query, values)
mydb.commit()

print("✅ Data inserted successfully into map_user table")

cursor.execute("SELECT * FROM map_user LIMIT 10")
for row in cursor.fetchall():
    print(row)



# cursor.execute("DROP TABLE IF EXISTS map_insur;")
# mydb.commit()

# print("✅ map_insur table dropped successfully")
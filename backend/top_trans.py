import pandas as pd
import json
import os

path = "C:/phonepayproject/pulse/data/top/transaction/country/india/state/"
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

top_Trans = pd.DataFrame(clm)
print(top_Trans)

# import mysql.connector
# mydb = mysql.connector.connect(
#         host = "localhost",
#         user = "root",
#         password = "k.dybalasai",
#         database = "phonepay",
#         autocommit = True )
# mycursor = mydb.cursor()
# cursor = mydb.cursor()
# cursor.execute("USE phonepay")
# mycursor.execute("""
# CREATE TABLE IF NOT EXISTS top_trans (
#     State VARCHAR(50),
#     Year INT,
#     Quater INT,
#     district_count BIGINT,
#     district_Transacion_amount BIGINT
# )
# """)

# query = """
# INSERT INTO top_trans
# (State, Year, Quater, district_count, district_Transacion_amount)
# VALUES (%s, %s, %s, %s, %s)
# """

# values = [tuple(x) for x in top_Trans.to_numpy()]

# mycursor.executemany(query, values)
# mydb.commit()   
# print("✅ Data inserted successfully into top_Trans table")
# query = """
# SELECT * FROM top_Trans LIMIT 10;
# """

# mycursor.execute(query)
# result = mycursor.fetchall()
# for row in result:
#     print(row)
# cursor.execute("DROP TABLE IF EXISTS top_Trans;")
# mydb.commit()

# print("✅ top_Trans table dropped successfully")
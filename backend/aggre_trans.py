import pandas as pd
import json
import os
import mysql.connector

# Path to aggregated transaction data
path = "C:/phonepayproject/pulse/data/aggregated/transaction/country/india/state/"
Agg_state_list = os.listdir(path)

# Columns
clm = {
    'State': [],
    'Year': [],
    'Quater': [],
    'Transacion_type': [],
    'Transacion_count': [],
    'Transacion_amount': []
}

# Extract data
for i in Agg_state_list:
    p_i = os.path.join(path, i)

    for j in os.listdir(p_i):
        p_j = os.path.join(p_i, j)

        for k in os.listdir(p_j):
            p_k = os.path.join(p_j, k)

            with open(p_k, 'r') as Data:
                D = json.load(Data)

            for z in D['data']['transactionData']:
                clm['Transacion_type'].append(z['name'])
                clm['Transacion_count'].append(z['paymentInstruments'][0]['count'])
                clm['Transacion_amount'].append(z['paymentInstruments'][0]['amount'])
                clm['State'].append(i)
                clm['Year'].append(j)
                clm['Quater'].append(int(k.strip('.json')))

# Create DataFrame
Agg_Trans = pd.DataFrame(clm)
print(Agg_Trans.head())

# MySQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="k.dybalasai",
    
)
mycursor = mydb.cursor()

# Create table
cursor = mydb.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS phonepay")
cursor.execute("USE phonepay")
mycursor.execute("""
CREATE TABLE IF NOT EXISTS Aggre_Trans (
    State VARCHAR(50),
    Year INT,
    Quater INT,
    Transacion_type VARCHAR(50),
    Transacion_count BIGINT,
    Transacion_amount BIGINT
)
""")

# Insert data
query = """
INSERT INTO Aggre_Trans
(State, Year, Quater, Transacion_type, Transacion_count, Transacion_amount)
VALUES (%s, %s, %s, %s, %s, %s)
"""

values = [tuple(x) for x in Agg_Trans.to_numpy()]

mycursor.executemany(query, values)
mydb.commit()

print("✅ Data inserted successfully into Aggre_Trans table")
# query = """
# SELECT * FROM Aggre_Trans LIMIT 10;
# """

# mycursor.execute(query)
# result = mycursor.fetchall()
# for row in result:
#     print(row)

import pandas as pd
import json
import os
import mysql.connector

# ---------- DATA EXTRACTION ----------
path = "C:/phonepayproject/pulse/data/aggregated/user/country/india/state/"
states = os.listdir(path)

data = {
    'State': [],
    'Year': [],
    'Quater': [],
    'Brand_Name': [],
    'User_Count': [],
    'Registered_Users': []
}

for state in states:
    state_path = os.path.join(path, state)

    for year in os.listdir(state_path):
        year_path = os.path.join(state_path, year)

        for file in os.listdir(year_path):
            file_path = os.path.join(year_path, file)

            with open(file_path, 'r') as f:
                D = json.load(f)

            data_section = D.get('data', {})
            users_by_device = data_section.get('usersByDevice')

            if users_by_device is None:
                continue

            registered_users = data_section['aggregated']['registeredUsers']

            for device in users_by_device:
                data['State'].append(state)
                data['Year'].append(year)
                data['Quater'].append(int(file.strip('.json')))
                data['Brand_Name'].append(device['brand'])
                data['User_Count'].append(device['count'])
                data['Registered_Users'].append(registered_users)

agg_user = pd.DataFrame(data)
print(agg_user.head())

# ---------- MYSQL CONNECTION ----------
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="k.dybalasai",
    database="phonepay"
)
cursor = mydb.cursor()

# ---------- TABLE CREATION (FRESH & CORRECT) ----------
cursor.execute("""
CREATE TABLE Aggre_user (
    State VARCHAR(50),
    Year INT,
    Quater INT,
    Brand_Name VARCHAR(50),
    User_Count BIGINT,
    Registered_Users BIGINT
)
""")

# ---------- INSERT DATA ----------
query = """
INSERT INTO Aggre_user
(State, Year, Quater, Brand_Name, User_Count, Registered_Users)
VALUES (%s, %s, %s, %s, %s, %s)
"""

values = [tuple(x) for x in agg_user.to_numpy()]
cursor.executemany(query, values)
mydb.commit()

print("✅ Data inserted successfully into Aggre_user table")

# ---------- VIEW DATA ----------
cursor.execute("SELECT * FROM Aggre_user LIMIT 10")
for row in cursor.fetchall():
    print(row)
# cursor.execute("DROP TABLE IF EXISTS Aggre_user;")
# mydb.commit()

# print("✅ Aggre_user table dropped successfully")
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",  
    database="constructora" 
)

cursor = conn.cursor()

with open('marketplace.sql', 'r', encoding='utf-8') as file:
    sql_script = file.read()

for result in cursor.execute(sql_script, multi=True):
    if result.with_rows:
        print(f"Filas afectadas: {result.rowcount}")
conn.commit()
cursor.close()
conn.close()

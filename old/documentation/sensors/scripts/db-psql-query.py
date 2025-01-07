import psycopg2

connection = psycopg2.connect(database="psql", user="postgres", host="localhost", password="*Something*", port=5432)

cursor = connection.cursor()
cursor.execute("SELECT * FROM psql.Logs;")

# Fetch all rows from database
record = cursor.fetchall()
print("Data from Database:- ", record)
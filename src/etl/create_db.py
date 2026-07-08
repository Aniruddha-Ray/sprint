import sqlite3

connection = sqlite3.connect("C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\db\\nifty100.db")

connection.execute("PRAGMA foreign_keys = ON;")

with open("C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\db\\schema.sql", "r") as schema_sql_file:

    connection.executescript(schema_sql_file.read())

connection.commit()

connection.close()

print("Database Created Successfully")
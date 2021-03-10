import mysql.connector

db_conn = mysql.connector.connect(host="kafka-3855.eastus2.cloudapp.azure.com", user="kafka", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
                DROP TABLE standard_order, custom_order
                ''')

db_conn.commit()
db_conn.close()

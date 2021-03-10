import mysql.connector

db_conn = mysql.connector.connect(host="kafka-3855.eastus2.cloudapp.azure.com", user="kafka", password="password", database="events")
db_cursor = db_conn.cursor()


db_cursor.execute('''CREATE TABLE standard_order (
          id VARCHAR(50) NOT NULL,
          customer_id VARCHAR(50) NOT NULL,
          customer_address VARCHAR(50) NOT NULL,
          order_date VARCHAR(50) NOT NULL,
          date_created VARCHAR(100) NOT NULL,
          PRIMARY KEY (id))
          ''')


db_cursor.execute('''CREATE TABLE custom_order (
          id VARCHAR(50) NOT NULL,
          customer_id VARCHAR(50) NOT NULL,
          customer_address VARCHAR(50) NOT NULL,
          design VARCHAR(250) NOT NULL,
          name VARCHAR(50) NOT NULL,
          order_date VARCHAR(50) NOT NULL,
          date_created VARCHAR(100) NOT NULL,
          PRIMARY KEY (id))
          ''')


db_conn.commit()
db_conn.close()

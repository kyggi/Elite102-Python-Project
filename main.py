
import mysql.connector
connection = mysql.connector.connect(user = 'root', database = 'example', password = 'Huynh08k!')

cursor = connection.cursor()

 

testQuery = ('SELECT * FROM students')

 

cursor.execute(testQuery)

 

for item in cursor:

    print(item)

addData = ('INSERT INTO Students (name, age, gender) VALUES ("Connor",3,"Male")')

 

cursor.execute(addData)

 

connection.commit()

cursor.close()

connection.close()
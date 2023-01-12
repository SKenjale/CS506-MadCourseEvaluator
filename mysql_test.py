import mysql.connector
from mysql.connector import Error

def connect():
    """ Connect to MySQL database """
    conn = None
    try:
        conn = mysql.connector.connect(
            host='24.240.33.86',
            database='mad_men',
            user='db_user',
            password='madmen',
            auth_plugin='mysql_native_password'
        )
        if conn.is_connected():
            print('Connected to MySQL database')
            cursor = conn.cursor()
            cursor.execute('select * from professor;')
            outputs = cursor.fetchall()
            for output in outputs:
                print(output)
            cursor.close()
    except Error as e:
        print(e)
    finally:
        if conn is not None and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    connect()

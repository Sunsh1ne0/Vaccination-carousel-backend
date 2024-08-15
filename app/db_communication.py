from datetime import datetime
import psycopg2

conn = None

def connect_to_db():
    global conn
    try:
    # пытаемся подключиться к базе данных
        conn = psycopg2.connect(dbname='carousel_db', user='postgres', password='Robot123', host="10.5.0.5", port="5432")
        print("Connecting to carousel")
        return 0
    except:
        # в случае сбоя подключения будет выведено сообщение
        print('Can`t establish connection to database')
        conn = None
        return 1

def init_tables():
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * from information_schema.tables where table_name=%s", ('carousel_stats',))
                if not bool(curs.rowcount):
                    curs.execute('CREATE TABLE carousel_stats (id Serial, timestamp TIMESTAMP, current_speed float8, dropsAmount INT, rotationAmount INT, vaccinationAmount1 INT, vaccinationAmount2 INT, startFlag boolean, sessionFlag boolean)')
                    conn.commit()
                curs.execute("SELECT * from information_schema.tables where table_name=%s", ('carousel_settings',))
                if not bool(curs.rowcount):
                    curs.execute('CREATE TABLE carousel_settings (id Serial, timestamp TIMESTAMP, rotDir text, targetSpeed float8, vacPos1 INT, vacPos2 INT, pusher text)')
                    curs.execute('INSERT INTO carousel_settings (timestamp, rotDir, targetSpeed, vacPos1, vacPos2, pusher) VALUES (%s, %s, %s, %s, %s, %s)', (datetime.now(), 'Counterclockwise', 1.8, 2, 3, 'Drop all'))
                    conn.commit()
            return 0
        return 'NO CONNECTION (INITIALIZE)'
    except:
        return 1

def update_settings(rotDir, targetSpeed, vacPos1, vacPos2, pusher):
    try:
        print(conn)
        if conn:
            with conn.cursor() as curs:
                curs.execute('UPDATE carousel_settings SET timestamp = %s, rotDir = %s, targetSpeed = %s, vacPos1 = %s, vacPos2 = %s, pusher = %s WHERE id = %s', (datetime.now(), rotDir, targetSpeed, vacPos1, vacPos2, pusher, 1))
                conn.commit()
                return 0
        return 'NO CONNECTION (UPDATE SETTINGS)'
    except:
        return 1
    
def update_stats(currentSpeed, dropsAmount, rotationAmount, vaccinationAmount1, vaccinationAmount2, startFlag, sessionFlag):
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute('INSERT INTO carousel_stats (timestamp, current_speed, dropsAmount, rotationAmount, vaccinationAmount1, vaccinationAmount2, startFlag, sessionFlag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (datetime.now(), currentSpeed, dropsAmount, rotationAmount, vaccinationAmount1, vaccinationAmount2, startFlag, sessionFlag))
                conn.commit()
                return 0
        return 'NO CONNECTION (UPDATE STATS)'
    except:
        return 1
    
def read_stats():
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute('SELECT * FROM carousel_stats ORDER BY id DESC LIMIT 1')
                rows = curs.fetchall()
                return rows
        return 'NO CONNECTION (READ STATS)'
    except:
        return []

def read_settings():
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute('SELECT * FROM carousel_settings WHERE id = %s', (1,))
                rows = curs.fetchall()
                return rows
        return 'NO CONNECTION (READ SETTINGS)'
    except:
        return []
    
def remove_old_stats():
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute('DELETE FROM carousel_stats WHERE timestamp < NOW() - INTERVAL \'1 day\'')
                conn.commit()
                return 0
        return 'NO CONNECTION (REMOVE OLD STATS)'
    except:
        return 1

def drop_tables():
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute('DROP TABLE carousel_settings')
                curs.execute('DROP TABLE carousel_stats')
                conn.commit()
                return 0
        return 'NO CONNECTION (DROP TABLES)'
    except:
        return 1
    
def disconnect_from_db():
    if conn:
        conn.close()
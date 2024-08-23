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
                curs.execute('CREATE TABLE IF NOT EXISTS carousel_stats (id Serial, timestamp TIMESTAMP, current_speed float8, dropsAmount INT, rotationAmount INT, vaccinationAmount1 INT, vaccinationAmount2 INT, startFlag boolean, sessionFlag boolean, sessionNum INT)')
                curs.execute('SELECT * FROM carousel_stats ORDER BY id DESC LIMIT 1')
                rows = curs.fetchall()
                if len(rows) == 0:
                    curs.execute('INSERT INTO carousel_stats (timestamp, current_speed, dropsAmount, rotationAmount, vaccinationAmount1, vaccinationAmount2, startFlag, sessionFlag, sessionNum) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (datetime.now(), 0, 0, 0, 0, 0, False, False, 0))
                    conn.commit()
        
                curs.execute('CREATE TABLE IF NOT EXISTS carousel_settings (id Serial, timestamp TIMESTAMP, rotDir text, targetSpeed float8, vacPos1 INT, vacPos2 INT, pusher text, control text)')                
                curs.execute('SELECT * FROM carousel_settings ORDER BY id DESC LIMIT 1')
                rows = curs.fetchall()
                if len(rows) == 0:
                    curs.execute('INSERT INTO carousel_settings (timestamp, rotDir, targetSpeed, vacPos1, vacPos2, pusher, control) VALUES (%s, %s, %s, %s, %s, %s, %s)', (datetime.now(), 'Counterclockwise', 1.8, 2, 3, 'Drop all', 'Включен'))
                    conn.commit()
            return 0
        return 'NO CONNECTION (INITIALIZE)'
    except:
        return 1

def update_settings(rotDir, targetSpeed, vacPos1, vacPos2, pusher, control):
    try:
        print(conn)
        if conn:
            with conn.cursor() as curs:
                curs.execute('UPDATE carousel_settings SET timestamp = %s, rotDir = %s, targetSpeed = %s, vacPos1 = %s, vacPos2 = %s, pusher = %s, control = %s WHERE id = %s', (datetime.now(), rotDir, targetSpeed, vacPos1, vacPos2, pusher, control, 1))
                conn.commit()
                return 0
        return 'NO CONNECTION (UPDATE SETTINGS)'
    except:
        return 1
    
def update_stats(currentSpeed, dropsAmount, rotationAmount, vaccinationAmount1, vaccinationAmount2, startFlag, sessionFlag, sessionNum):
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute('INSERT INTO carousel_stats (timestamp, current_speed, dropsAmount, rotationAmount, vaccinationAmount1, vaccinationAmount2, startFlag, sessionFlag, sessionNum) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (datetime.now(), currentSpeed, dropsAmount, rotationAmount, vaccinationAmount1, vaccinationAmount2, startFlag, sessionFlag, sessionNum))
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

def get_sessions_num(date: str):
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute(f"SELECT DISTINCT carousel_stats.sessionnum FROM carousel_stats where carousel_stats.timestamp between '{date}' and date '{date}' + INTERVAL '1 day'")
                rows = curs.fetchall()
                if len(rows) != 0:
                    sessionStartDict = []
                    sessionEndDict = []
                    for row in rows:
                        row=row[0]
                        curs.execute(f"SELECT * from carousel_stats where carousel_stats.timestamp between '{date}' and date '{date}' + INTERVAL '1 day' and carousel_stats.sessionnum={row} and carousel_stats.sessionflag=true order by id ASC limit 1")
                        startID = curs.fetchall()
                        if len(startID) != 0:
                            startID = startID[0]
                            sessionStartDict.append(startID)
                        curs.execute(f"SELECT * from carousel_stats where carousel_stats.timestamp between '{date}' and date '{date}' + INTERVAL '1 day' and carousel_stats.sessionnum={row} and carousel_stats.sessionflag=true order by id DESC limit 1")
                        endID = curs.fetchall()
                        if len(endID) != 0:
                            endID = endID[0]
                            sessionEndDict.append(endID)
                    return [sessionStartDict, sessionEndDict, len(rows)]
                return [[], [], 0]
        return [[], [], 0]
    except:
        return [[], [], 0]
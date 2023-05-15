import datetime 

VALERIE_DB = "/home/zoewong/valerie/database/valerie.db"

oldest_data_time = datetime.datetime.strptime("2023-05-14 15:00:00.000000", '%Y-%m-%d %H:%M:%S.%f')

TEMP_HUMIDITY_TABLE = "temp_humidity_table"

def reverse_log_cols(logs):
    return [log[::-1] for log in logs]

def create_tH_table(conn, cursor): 
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {TEMP_HUMIDITY_TABLE} (temperature real, humidity real, datetime timestamp)""")
    conn.commit()

def insert_into_tH_table(conn, cursor, new_data):
    cursor.executemany(f"""INSERT into {TEMP_HUMIDITY_TABLE} VALUES (?,?,?)""", new_data)
    conn.commit()

def get_from_tH_table(conn, cursor, curr_time=None, prev_days=None):
    if curr_time and prev_days:
        earliest_log_time = curr_time - datetime.timedelta(days=prev_days)
        logs = cursor.execute(f"""SELECT * FROM {TEMP_HUMIDITY_TABLE} WHERE datetime > ? AND datetime > ? ORDER BY datetime DESC""", (earliest_log_time,oldest_data_time,)).fetchall()
    else:
        logs = cursor.execute(f"""SELECT * FROM {TEMP_HUMIDITY_TABLE} WHERE datetime > ? ORDER BY datetime DESC""", (oldest_data_time,)).fetchall()
    conn.commit()
    return reverse_log_cols(logs)

def parse_tH_data(prev_logs):
    return "\n".join([f"Temperature: {temperature}{chr(176)}F, Humidity: {humidity}%" for (temperature, humidity, datetime) in prev_logs])


ESP_OCCUPANCY_TABLE = "esp_occupancy_table"
WEB_OCCUPANCY_TABLE = "web_occupancy_table"

def create_occupancy_table(conn, cursor, isESP=True):
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {ESP_OCCUPANCY_TABLE if isESP else WEB_OCCUPANCY_TABLE} (occupancy int, datetime timestamp)""")
    conn.commit()

def insert_into_occupancy_table(conn, cursor, new_data, isESP=True):
    if isESP:
        cursor.executemany(f"""INSERT into {ESP_OCCUPANCY_TABLE} VALUES (?,?)""", new_data)
    else:
        cursor.execute(f"""INSERT into {WEB_OCCUPANCY_TABLE} VALUES (?,?)""", new_data)
    conn.commit()

def get_from_occupancy_table(conn, cursor, curr_time=None, prev_days=None, isESP=True):
    if curr_time and prev_days:
        earliest_log_time = curr_time - datetime.timedelta(days=prev_days)
        logs = cursor.execute(f"""SELECT * FROM {ESP_OCCUPANCY_TABLE if isESP else WEB_OCCUPANCY_TABLE} WHERE datetime > ? AND datetime > ? ORDER BY datetime DESC""", (earliest_log_time,oldest_data_time,)).fetchall()
    else:
        logs = cursor.execute(f"""SELECT * FROM {ESP_OCCUPANCY_TABLE if isESP else WEB_OCCUPANCY_TABLE} WHERE datetime > ? ORDER BY datetime DESC""", (oldest_data_time,)).fetchall()
    conn.commit()
    return reverse_log_cols(logs)


AVG_WAIT_TIME_TABLE = 'wait_time_table'

def create_wait_time_table(conn, cursor, isESP=True):
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {AVG_WAIT_TIME_TABLE} (avg_wait_time real, datetime timestamp)""")
    conn.commit()

def insert_into_wait_time_table(conn, cursor, new_data):
    cursor.executemany(f"""INSERT into {AVG_WAIT_TIME_TABLE} VALUES (?,?)""", new_data)
    conn.commit()

def get_from_wait_time_table(conn, cursor, curr_time=None, prev_days=None, date=None):
    if curr_time and prev_days:
        earliest_log_time = curr_time - datetime.timedelta(days=prev_days)
        logs = cursor.execute(f"""SELECT * FROM {AVG_WAIT_TIME_TABLE} WHERE datetime > ? AND datetime > ? ORDER BY datetime DESC""", (earliest_log_time,oldest_data_time,)).fetchall()
    elif curr_time and date:
        start_time = date
        end_time = date + datetime.timedelta(days=1)
        logs = cursor.execute(f"""SELECT * FROM {AVG_WAIT_TIME_TABLE} WHERE datetime > ? AND datetime < ? ORDER BY datetime DESC""", (start_time,end_time)).fetchall()
    else:
        logs = cursor.execute(f"""SELECT * FROM {AVG_WAIT_TIME_TABLE} WHERE datetime > ? ORDER BY datetime DESC""", (oldest_data_time,)).fetchall()
    conn.commit()
    return reverse_log_cols(logs)



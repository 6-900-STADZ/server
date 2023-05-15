from flask import Flask, render_template, request
import requests 
import datetime
import pandas as pd
import plotly
import plotly.express as px
import json
import pytz

from database.database_utils import connect_to_database, close_db_connection
from database.access_database import *

app = Flask(__name__)

test_mode = True
t_rH_period = 4 if test_mode else 10
esp_occupancy_period = 1 if test_mode else 5

def convert_ms_to_min(ms):
    return ms/1000/60

@app.route("/")
def default_page(): 
    return render_template('template.html')

@app.route("/bus_info", methods=['GET','POST'])
def bus_info():
    if request.method == 'GET':
        data = request.args
        stopId = int(data.get('stop'))

        url = "https://api.goswift.ly/real-time/miami/predictions"

        querystring = {"stop":stopId}

        headers = {
            "Accept": "application/xml, application/json",
            "Authorization": "81ee30b5d4fc8c9836dc7585889004d2"
        }

        response = requests.get(url, headers=headers, params=querystring).json()
        return response
    else:
        "OOPS! Expecting a POST Request"
    
@app.route("/temp_humidity_data", methods=['GET'])
def temp_humidity_data_method():
    if request.method == "GET":    
        args = request.args
        time = float(args.get('time')) if args.get('time') else None
        curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))
        
        conn, cursor = connect_to_database(VALERIE_DB)
        temp_humidity_logs = get_from_tH_table(conn, cursor, curr_time, time)
        close_db_connection(conn)
        return temp_humidity_logs
    
    # elif request.method == "POST":
    #     data = request.json
    #     temperature_today = data.get('t')
    #     humidity_today = data.get('rh')

    #     if test_mode:
    #         curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))
    #         time_tH_today = [(t,rh, curr_time - datetime.timedelta(minutes=t_rH_period*index))
    #                                 for index, (t,rh) in enumerate(zip(temperature_today[::-1], humidity_today[::-1]))]
    #     else:
    #         curr_day = datetime.date.today().astimezone(pytz.timezone('US/Eastern'))
    #         start_time = datetime.datetime(curr_day.year, curr_day.month, curr_day.day, hour=8)
    #         time_tH_today = [(t,rh, start_time + datetime.timedelta(minutes=t_rH_period*index))
    #                                 for index, (t,rh) in enumerate(zip(temperature_today, humidity_today))]
    
    #     conn, cursor = connect_to_database(VALERIE_DB)
    #     create_tH_table(conn, cursor)
    #     insert_into_tH_table(conn, cursor, time_tH_today)
    #     close_db_connection(conn)
    #     return "SUCCESSFUL POSTING!"
    else: 
        return "OOPS! Expecting a GET or POST Request"
    
@app.route("/occupancy/ESP", methods=['GET'])
def esp_occupancy():
    if request.method == 'GET':
        args = request.args
        time = int(args.get('time')) if args.get('time') else None
        curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))
        
        conn, cursor = connect_to_database(VALERIE_DB)
        occupancy_logs = get_from_occupancy_table(conn, cursor, curr_time, time)
        close_db_connection(conn)
        return occupancy_logs
    
    # elif request.method == "POST":
    #     data = request.json
    #     try:
    #         with open('/tmp/foo.txt', 'w') as f:
    #             f.write(str(data))
    #     except Exception as e:
    #         return str(e)
    #     conn, cursor = connect_to_database(VALERIE_DB)

    #     # POST OCCUPANCY DATA
    #     occupancy_today = data.get('occupancy')
    #     if test_mode:
    #         curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))
    #         time_occupancy_today = [(occupancy, curr_time - datetime.timedelta(minutes=esp_occupancy_period*index))
    #                                 for index, occupancy in enumerate(occupancy_today[::-1])]
            
    #     else:
    #         curr_day = datetime.date.today().astimezone(pytz.timezone('US/Eastern'))
    #         start_time = datetime.datetime(curr_day.year, curr_day.month, curr_day.day, hour=8)

    #         time_occupancy_today = [(occupancy, start_time + datetime.timedelta(minutes=esp_occupancy_period*index))
    #                                 for index, occupancy in enumerate(occupancy_today)]
            
    #     create_occupancy_table(conn, cursor)
    #     insert_into_occupancy_table(conn, cursor, time_occupancy_today)

    #     close_db_connection(conn)
    #     return "SUCCESSFUL POSTING!"
    else: 
        return "OOPS! Expecting a GET or POST Request"

@app.route("/occupancy/WEB", methods=['GET','POST'])
def web_occupancy():
    if request.method == 'GET':
        args = request.args
        time = float(args.get('time')) if args.get('time') else None
        curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))
        
        conn, cursor = connect_to_database(VALERIE_DB)

        occupancy_logs = get_from_occupancy_table(conn, cursor, curr_time, time, isESP=False)
        close_db_connection(conn)
        return occupancy_logs
    
    elif request.method == "POST":
        data = request.json
        curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))
        curr_occupancy = int(data.get('occupancy'))

        conn, cursor = connect_to_database(VALERIE_DB)

        create_occupancy_table(conn,cursor, isESP=False)
        insert_into_occupancy_table(conn, cursor, (curr_occupancy, curr_time), isESP=False)
        close_db_connection(conn)
        
        return "SUCCESSFUL POSTING!"
    else: 
        return "OOPS! Expecting a GET or POST Request"

@app.route("/wait_time", methods=['GET'])
def wait_time():
    if request.method == 'GET':
        args = request.args
        date = datetime.datetime.strptime(args.get('date'), '%Y-%m-%d') if args.get('date') else None
        time = float(args.get('time')) if args.get('time') else None
        curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))

        conn, cursor = connect_to_database(VALERIE_DB)
        wait_time_logs = get_from_wait_time_table(conn, cursor, curr_time, time, date)
        close_db_connection(conn)
        formatted_wait_time_logs = [[str(datetime.datetime.strptime(":".join(time.split(":")[:2]), '%Y-%m-%d %H:%M')), wait_time] for [time, wait_time] in wait_time_logs]
        wait_time_logs = {}
        for [dt, wt] in formatted_wait_time_logs:
            if dt not in wait_time_logs:
                wait_time_logs[dt] = []
            wait_time_logs[dt].append(wt)
        return wait_time_logs
    
    # elif request.method == 'POST':
    #     data = request.json
    #     avg_wait_time_today = data.get('avg_wait_time')

    #     if test_mode:
    #         curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))
    #         time_avg_wait_time_today = [(t, curr_time - datetime.timedelta(minutes=esp_occupancy_period*index))
    #                                 for index, t in enumerate(avg_wait_time_today)]
            
    #     else:
    #         curr_day = datetime.date.today().astimezone(pytz.timezone('US/Eastern'))
    #         start_time = datetime.datetime(curr_day.year, curr_day.month, curr_day.day, hour=8)

    #         time_avg_wait_time_today = [(t, start_time + datetime.timedelta(minutes=esp_occupancy_period*index))
    #                                 for index, t in enumerate(avg_wait_time_today)]

    #     conn, cursor = connect_to_database(VALERIE_DB)
    #     create_wait_time_table(conn, cursor)
    #     insert_into_wait_time_table(conn, cursor, time_avg_wait_time_today)
    #     close_db_connection(conn)
    #     return "SUCCESSFUL POSTING"
    else:
        return "OOPS! Expecting a GET or POST Request"

@app.route("/all_data", methods=['GET', 'POST'])
def get_all_data():
    if request.method == 'GET':
        curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))
        
        # get all data 
        conn, cursor = connect_to_database(VALERIE_DB)
        temp_humidity_logs = get_from_tH_table(conn, cursor, curr_time)
        esp_occupancy_logs = get_from_occupancy_table(conn, cursor, curr_time)
        web_occupancy_logs = get_from_occupancy_table(conn, cursor, curr_time, isESP=False)
        wait_time_logs = get_from_wait_time_table(conn, cursor, curr_time)
        close_db_connection(conn)

        temp_logs = [[time, t] for [time,_, t] in temp_humidity_logs]
        humidity_logs = [[time, rh] for [time,rh,_] in temp_humidity_logs]

        return {
            't': temp_logs,
            'rh': humidity_logs,
            'esp_occupancy': esp_occupancy_logs,
            'web_occupancy': web_occupancy_logs,
            # 'wait_time': wait_time_logs
        }

        # create dataframe of time vs. data 
        t_df = pd.DataFrame(formatted_temp_logs, columns=['DateTime', f"Temperature (in {chr(176)}F)"])
        rH_df = pd.DataFrame(formatted_humidity_logs, columns=['DateTime', 'Relative Humidity (in %)'])
        esp_occ_df = pd.DataFrame(formatted_esp_occupancy_logs, columns=['DateTime', 'Occupancy', 'Method'])
        web_occ_df = pd.DataFrame(formatted_web_occupancy_logs, columns=['DateTime', 'Occupancy', 'Method'])
        occ_df = pd.concat([esp_occ_df, web_occ_df])
        wt_df = pd.DataFrame(formatted_wait_time_logs, columns=['DateTime', 'Wait Time (in Minutes)'])

        # make line graph
        t_fig = px.line(t_df, x="DateTime", y=f"Temperature (in {chr(176)}F)")
        rH_fig = px.line(rH_df, x="DateTime", y="Relative Humidity (in %)")
        occ_fig = px.line(occ_df, x="DateTime", y="Occupancy", color="Method")
        # wt_fig = px.line(wt_df, x="DateTime", y="Average Wait Time (in Minutes)")
        # wt_fig = px.histogram(pd.DataFrame([[formatted_wait_time_logs[0][0], wait_time] for wait_time in [0,0,1,2,4]], columns=['DateTime', 'Wait Time (in Minutes)']), x='Wait Time (in Minutes)')
        wt_fig = px.histogram(wt_df[(wt_df['DateTime'] == formatted_wait_time_logs[0][0])], x='Wait Time (in Minutes)', range_x=[0, 12], range_y=[0,10])

        # turn into json object for export and embedding in template:
        temp_graph_JSON = json.dumps(t_fig, cls=plotly.utils.PlotlyJSONEncoder)
        humidity_graph_JSON = json.dumps(rH_fig, cls=plotly.utils.PlotlyJSONEncoder)
        occupancy_graph_JSON = json.dumps(occ_fig, cls=plotly.utils.PlotlyJSONEncoder)
        waitTime_graph_JSON = json.dumps(wt_fig, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('plot_template.html', 
                               temp_graph_JSON=temp_graph_JSON, 
                               humidity_graph_JSON=humidity_graph_JSON, 
                               occupancy_graph_JSON=occupancy_graph_JSON,
                               waitTime_graph_JSON=waitTime_graph_JSON,
                               )
    elif request.method == "POST":
        data = request.json
        try:
            with open('/tmp/foo.txt', 'w') as f:
                f.write(str(data))
        except Exception as e:
            return str(e)
        conn, cursor = connect_to_database(VALERIE_DB)
            
        # POST TEMPERATURE & HUMIDITY DATA
        temperature_today = data.get('t')
        humidity_today = data.get('rh')

        if test_mode:
            curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))
            time_tH_today = [(t,rh, curr_time - datetime.timedelta(minutes=t_rH_period*index))
                                    for index, (t,rh) in enumerate(zip(temperature_today[::-1], humidity_today[::-1]))]
        else:
            curr_day = datetime.date.today().astimezone(pytz.timezone('US/Eastern'))
            start_time = datetime.datetime(curr_day.year, curr_day.month, curr_day.day, hour=8)
            time_tH_today = [(t,rh, start_time + datetime.timedelta(minutes=t_rH_period*index))
                                    for index, (t,rh) in enumerate(zip(temperature_today, humidity_today))]
    
        create_tH_table(conn, cursor)
        insert_into_tH_table(conn, cursor, time_tH_today)

        # POST OCCUPANCY DATA
        occupancy_today = data.get('occupancy')
        if test_mode:
            curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))
            time_occupancy_today = [(occupancy, curr_time - datetime.timedelta(minutes=esp_occupancy_period*index))
                                    for index, occupancy in enumerate(occupancy_today[::-1])]
            
        else:
            curr_day = datetime.date.today().astimezone(pytz.timezone('US/Eastern'))
            start_time = datetime.datetime(curr_day.year, curr_day.month, curr_day.day, hour=8)

            time_occupancy_today = [(occupancy, start_time + datetime.timedelta(minutes=esp_occupancy_period*index))
                                    for index, occupancy in enumerate(occupancy_today)]
            
        create_occupancy_table(conn, cursor)
        insert_into_occupancy_table(conn, cursor, time_occupancy_today)

        # POST WAIT ITME DATA 
        wait_time_today = data.get('wait_time')
        # wait_time_today = [int(wt) for wt in data.get('wait_time').split(",")[:-1]]

        if test_mode:
            curr_time = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))
            wait_time_index = len(wait_time_today)-1
            time_wait_time_today = []
            for occupancy_index, occ in enumerate(occupancy_today[::-1]):
                for _ in range(occ):
                    time_wait_time_today.append((wait_time_today[wait_time_index], 
                                                 curr_time - datetime.timedelta(minutes=esp_occupancy_period*occupancy_index)))
                    wait_time_index -= 1            
        else:
            curr_day = datetime.date.today().astimezone(pytz.timezone('US/Eastern'))
            start_time = datetime.datetime(curr_day.year, curr_day.month, curr_day.day, hour=8)

            time_wait_time_today = [(t, start_time + datetime.timedelta(minutes=esp_occupancy_period*index))
                                    for index, t in enumerate(wait_time_today)]

        create_wait_time_table(conn, cursor)
        insert_into_wait_time_table(conn, cursor, time_wait_time_today)

        close_db_connection(conn)
        return "SUCCESSFUL POSTING!"
    else: 
        return "OOPS! Expecting a GET or POST Request"

if __name__ == "__main__":
    app.run(host='0.0.0.0')

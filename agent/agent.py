# This is template code.  It is not currently working.

import configparser, datetime, json, socket, sqlite3, ssl, time
import asyncio
import concurrent.futures
import requests

# Settings
class Settings:
    agent_path = ''

    def load_settings():
        pass

# Data
class Data:
    def __init__(self):
        self.con = sqlite3.connect(Settings.agent_path + 'agent_sqlite.db', isolation_level=None)
        self.cursor = self.con.cursor()

    def __del__(self):
        self.con.close()

    def create_tables(self):
        sql = "create table if not exists jobs(parameters json);"
        #sql += "other tables"
        self.cursor.executescript(sql)
        self.con.commit()

    def insert_jobs(self, parameters):
        sql = "delete from jobs;"
        self.cursor.execute(sql)
        sql = "insert into jobs(parameters) values (?);"
        self.cursor.execute(sql, [parameters])
        self.con.commit()

    def select_jobs(self):
        sql = "select * from jobs;"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows


# Code
class Code:
    def load_jobs(self):
        parameters = {"name":"Test", "url":"http://localhost:8000", "validate":1, "text":"user"}
        parameters = json.dumps(parameters)
        D = Data()
        D.create_tables()
        D.insert_jobs(parameters)

    def run_jobs(self, data, poll_time):
        # Add logic switch for Selenium/Code Jobs
        self.run_api(data, poll_time)


    def run_api(self, data, poll_time):  
        #print(data[0])
        data = json.loads(data[0])   
        packet = {}
        name = data['name']
        url = data['url']
        ptime = int(poll_time)
        valid = 1
        response = 1 
        start_time = time.perf_counter()   
        res = requests.get(data['url'])
        elapsed_time = round(time.perf_counter() - start_time, 2)
        response_code = res.status_code
        if res.status_code != 200: response = 0
    
        if data['validate'] == True:
            if data['text'] in res.text:
                valid = 1
            else: valid = 0           
    
        #D = Data()
        #D.insert_metrics(ptime, name, url, response, response_code, valid, elapsed_time)
        print(ptime, name, url, response, response_code, valid, elapsed_time)

class Network:
    pass

class Process:
    def launcher(self):
        C = Code()
        D = Data()
        N = Network()
        poll_time = str(time.time()).split('.')[0]
                
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(C.run_jobs, i, poll_time) for i in D.select_jobs()]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result(timeout=5)
                except concurrent.futures.TimeoutError:
                    print("Too long!")
                    sys.stdout.flush()

        # N.send/receive? <-send receive data.  Data will most likely be sent the second poll due to the async launch 

    def scheduler(self):
        while True:
            a = datetime.datetime.now().second
            if a == 0:
                self.launcher() 
                time.sleep(1)

C = Code()
C.load_jobs()
P = Process()
P.scheduler()

#References:https://clasense4.wordpress.com/2012/07/29/python-redis-how-to-cache-python-mysql-result-using-redis/
#https://opensource.com/article/18/4/how-build-hello-redis-with-python
#https://docs.microsoft.com/en-us/azure/redis-cache/cache-python-get-started
#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from flask import Flask, redirect, render_template, request
import urllib
import datetime
import json
import pypyodbc
import time
import random
import pickle
import hashlib
import redis

server = 'surajkawthekar.database.windows.net'
database = 'myDatabase'
username = 'surajkawthekar'
password = 'Smk@111093'
driver = '{ODBC Driver 13 for SQL Server}'
app = Flask(__name__)
R_SERVER = redis.Redis(host='surajkawthekar.redis.cache.windows.net',
        port=6379, db=0, password='Tw6Viq1Ci7MB41Ua23SO6rHin08Ggbv1u4xOwNCFAmI=')

# print("Opened database successfully")

# conn.execute('CREATE TABLE students (name TEXT, addr TEXT, city TEXT, pin TEXT)')
# print("Table created successfully")
# conn.close()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    cnxn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server
                            + ';PORT=1443;DATABASE=' + database
                            + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()
    starttime = time.time()
    cursor.execute('SELECT TOP 8000 * from [equake]')
    rows = cursor.fetchall()
    endtime = time.time()
    duration = endtime - starttime
    return render_template('city.html', ci=rows, timedur=duration)

@app.route('/quakerange', methods=['GET'])
def quake():
    # connect to DB2
    sql="select * from [equake]".encode('utf-8')
    magn = float(request.args.get('mag'))
    magn1 = float(request.args.get('mag1'))
    
    cnxn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server
                            + ';PORT=1443;DATABASE=' + database
                            + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()
    
        
    
    starttime = time.time()
    for i in range(0,1500):
        random1 = round(random.uniform(float(magn),float(magn1)),3)
        hash = hashlib.sha224(sql).hexdigest()
        key = "sql_cache:" + hash
        if (R_SERVER.get(key)):
            print ("This was return from redis")
        else:
            cursor.execute("select * from [equake] where mag>'"+ str(random1) +"'")
            data = cursor.fetchall()
        
            rows1=[]
            for x in data:
                rows1.append(str(x))
                R_SERVER.set(key,pickle.dumps(list(rows1)))
        # Put data into cache for 1 hour
                R_SERVER.expire(key, 36)
                print ("This is the cached data")
    endtime = time.time()  
        # Note that for security reasons we are preparing the statement first,
        # then bind the form input as value to the statement to replace the
        # parameter marker.   
           
    duration = endtime - starttime
    return render_template('viewrangedquakes.html',timedur=duration)

@app.route('/quakerange1', methods=['GET'])
def quake1():
    # connect to DB2
    magn = float(request.args.get('mag'))
    magn1 = float(request.args.get('mag1'))
    query1 = float(request.args.get('query'))

    cnxn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server
                            + ';PORT=1443;DATABASE=' + database
                            + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()
    starttime = time.time()
    for i in range(0,int(query1)):
          random1 = round(random.uniform(float(magn),float(magn1)),3)
          cursor.execute("select * from [equake] where mag>'"+ str(random1) +"'")  
        # Note that for security reasons we are preparing the statement first,
        # then bind the form input as value to the statement to replace the
        # parameter marker.
    rows=[]
    rows = cursor.fetchall()
    endtime = time.time()
    duration = endtime - starttime
    return render_template('viewrange.html',timedur=duration)

if __name__ == '__main__':
    app.run(debug=True)

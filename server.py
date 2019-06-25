#Refences: The following code has been referred from https://github.com/IBM-Cloud/cloud-sql-database/blob/master/templates/index.html
import os
from flask import Flask,redirect,render_template,request
import urllib
import datetime
import json
import ibm_db

app = Flask(__name__)

# get service information if on IBM Cloud Platform
if 'VCAP_SERVICES' in os.environ:
    db2info = json.loads(os.environ['VCAP_SERVICES'])['dashDB For Transactions'][0]
    db2cred = db2info["credentials"]
    appenv = json.loads(os.environ['VCAP_APPLICATION'])
else:
    raise ValueError('Expected cloud environment')

# handle database request and query city information


# main page to dump some environment information
@app.route('/')
def index():
   return render_template('index.html', app=appenv)

# for testing purposes - use name in URI
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/search', methods=['GET'])
def city():
    # connect to DB2
    magn = request.args.get('name')
    db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")
    if db2conn:
        sql = "select * from earthquake where mag >'"+magn+"'"
        sql1 = "select count(*) from earthquake where mag > '"+magn+"'"
        # Note that for security reasons we are preparing the statement first,
        # then bind the form input as value to the statement to replace the
        # parameter marker.
        stmt = ibm_db.exec_immediate(db2conn,sql)

        stmt1 = ibm_db.exec_immediate(db2conn,sql1)

        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        result1 = ibm_db.fetch_assoc(stmt1)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        rows1=[]
        rows1= result1
        # close database connection
        ibm_db.close(db2conn)
    return render_template('city.html', ci=rows , ci1=rows1)
    
@app.route('/quakerange', methods=['GET'])
def quake():
    # connect to DB2
    magn = request.args.get('mag')
    magn1 = request.args.get('mag1')
    sdate = request.args.get('date1')
    edate = request.args.get('date2')

    db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")
    if db2conn:
        sql = "select * from earthquake where mag>'"+magn+"'and mag <'"+magn1+"' and time>'"+sdate+"' and time <'"+edate+"'" 
        # Note that for security reasons we are preparing the statement first,
        # then bind the form input as value to the statement to replace the
        # parameter marker.
        stmt = ibm_db.exec_immediate(db2conn,sql)

        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            res1 = result["TIME"].split("T")
            if res1[0]>=sdate and res1[0]<=edate:
                rows.append(result.copy())
                result = ibm_db.fetch_assoc(stmt)
            # close database connection
        ibm_db.close(db2conn)
    return render_template('viewrangedquakes.html', ci=rows)

@app.route('/quakelocation', methods=['GET'])
def quakeradius():
    # connect to DB2
    lati = float(request.args.get('latitude'))
    longi = float(request.args.get('longitude'))
    rad = float(request.args.get('radius'))
    db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")
    
    longi1 = longi-(rad*0.014)
    longi2 = longi+(rad*0.014)
    lati1 = lati-rad
    lati2 = lati+rad    

    if db2conn:
        sql = "select * from earthquake where latitude > ? and latitude < ? and longitude > ? and longitude < ?" 
        # Note that for security reasons we are preparing the statement first,
        # then bind the form input as value to the statement to replace the
        # parameter marker.
        stmt = ibm_db.prepare(db2conn,sql)
        ibm_db.bind_param(stmt, 1, str(lati1))
        ibm_db.bind_param(stmt, 2, str(lati2))
        ibm_db.bind_param(stmt, 3, str(longi1))
        ibm_db.bind_param(stmt, 4, str(longi2))
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
    return render_template('base.html', ci=rows)
@app.route('/city/<name>')
def cityroute(name=None):
    return city(name)

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
 app.run(host='0.0.0.0', port=int(port))
from flask import Flask, jsonify 
from dataRecollector import getJobsPythonJobs, getJobsRemote, getJobsIndeed
import time, atexit, urllib, os
from apscheduler.schedulers.background import BackgroundScheduler
import mysql.connector
from dotenv import load_dotenv

app= Flask(__name__)
load_dotenv()

dbAccessInfo={
    "user":os.getenv("DB_USERNAME"),
    "password":os.getenv("DB_PASS"),
    "host":'localhost',
    "database":os.getenv("DATABASE")
}

def removeLinksDown():
    con= mysql.connector.connect(user=dbAccessInfo["user"], password=dbAccessInfo["password"], host=dbAccessInfo["host"], database=dbAccessInfo["database"])
    cursor=con.cursor(buffered=True)
    cursor.execute("SELECT jobId, jobLink FROM jobs")
    record=cursor.fetchall()
    for job in record:
        try:
            urllib.request.urlopen(job[1])
        except urllib.error.URLError as e:
            if(str(e)=="HTTP Error 404: Not Found"):
                print(e)
                cursor.execute("DELETE FROM jobs WHERE jobId=%s",(job[0],))
                con.commit()
    cursor.close()
    con.close()

def limitDBEntries():
    limit=200
    con= mysql.connector.connect(user=dbAccessInfo["user"], password=dbAccessInfo["password"], host=dbAccessInfo["host"], database=dbAccessInfo["database"])
    cursor=con.cursor(buffered=True)
    cursor.execute("SELECT jobId FROM jobs")
    record=cursor.fetchall()
    if len(record)>limit: #200 entries is the limit for the database
        entriesToDelete=len(record)-limit
        cursor.execute("DELETE FROM jobs LIMIT %s",(entriesToDelete,))
        con.commit()
        print(str(entriesToDelete) + " entries were deleted successfully")
    cursor.close()
    con.close()

def registerJobs(jobList):
    con= mysql.connector.connect(user=dbAccessInfo["user"], password=dbAccessInfo["password"], host=dbAccessInfo["host"], database=dbAccessInfo["database"])
    cursor=con.cursor(buffered=True)
    for job in jobList:
        data_job=(job["link"],)
        cursor.execute("SELECT jobId FROM jobs WHERE jobLink=%s",data_job)
        if cursor.rowcount==0:
            add_jobs=''' INSERT INTO jobs(jobName,jobCompany,jobLink) VALUE(%s,%s,%s)'''
            data_job=(job["jobName"],job["jobCompany"],job["link"])
            cursor.execute(add_jobs,data_job)
            con.commit()
    cursor.close()
    con.close()

def UpdateDatabase():
    try:
        #REGISTER JOBS TO THE DATABASE
        registerJobs(getJobsPythonJobs())
        registerJobs(getJobsRemote())   
        registerJobs(getJobsIndeed())
        #Remove down links 404 not found
        removeLinksDown()
        #LIMIT DATABASE ENTRIES
        limitDBEntries()
        print("The DataBase has been updated successfully")
    except Exception:
        print("Something went terribly wrong")

def getTotalJobs():
    jobsList=[]
    #FETCH JOBS IN THE DATABASE
    con= mysql.connector.connect(user=dbAccessInfo["user"], password=dbAccessInfo["password"], host=dbAccessInfo["host"], database=dbAccessInfo["database"])
    cursor=con.cursor(buffered=True)
    getJobsSQL='''SELECT jobName, jobCompany, jobLink FROM jobs'''
    cursor.execute(getJobsSQL)
    record=cursor.fetchall()
    for column in record:
        job={
            "Job name":column[0],
            "Job Company":column[1],
            "Job Link":column[2]
        }
        jobsList.append(job.copy())
    con.close()
    return jobsList

#START BACKGROUND SCHEDULER
scheduler= BackgroundScheduler()
scheduler.add_job(func=UpdateDatabase,trigger="interval",hours=20)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def home():
    return jsonify(getTotalJobs())

if __name__=="__main__":
    app.run(debug=True, use_reloader=False)

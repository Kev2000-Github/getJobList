from commonCustom import openParsePage
from flask_sqlalchemy import SQLAlchemy
import re

#GET INFO FROM WEB SCRAPPING
def getJobsPythonJobs():
    jobList=[]
    #SCRAPPING FIRST PAGE
    soup=openParsePage("http://pythonjobs.github.io/","section",{"class":"job_list"})
    jobsContainer=soup.find_all("div",class_="job")
    for job in jobsContainer:
        jobData={
        "jobName":job.find("h1").text.strip(),
        "jobCompany":job.find_all("span")[3].text.strip(),
        "link":"http://pythonjobs.github.io/"+job.find("a")["href"]
        }
        jobList.append(jobData.copy())
    return jobList

def getJobsRemote():
    jobList=[]
    #SCRAPPING SECOND PAGE
    soup=openParsePage("https://remote.co/remote-jobs/developer/","div",{"class":"card-body"})
    jobsContainer=soup.find_all("a",class_="card")
    for job in jobsContainer:
        jobData={
        "jobName":job.find('span',class_="font-weight-bold").text,
        "jobCompany":job.find('p',class_="text-secondary").text.strip().split('   ')[0].strip(),
        "link":"https://remote.co"+job["href"]
        }
        jobList.append(jobData.copy())
    return jobList

def getJobsIndeed():
    jobList=[]
    #THIRD SCRAPPING
    soup=openParsePage("https://au.indeed.com/jobs?q=software+developer&sort=date","td",{"id":"resultsCol"})
    jobsContainer=soup.find_all("div",class_="jobsearch-SerpJobCard")
    for job in jobsContainer:
        jobData={
        "jobName":job.find("a",class_="jobtitle").text.strip(),
        "jobCompany":job.find('span',class_="company").text.strip(),
        "link":"https://au.indeed.com"+job.find("a",class_="jobtitle")["href"]
        }
        jobList.append(jobData.copy())
    return jobList

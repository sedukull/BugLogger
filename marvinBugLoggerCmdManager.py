#!/usr/bin/python2.7

import sys

sys.path.append("/usr/lib/python2.7")
sys.path.append("/usr/lib/python2.7/site-packages")
sys.path.append("/usr/local/lib/python2.7")
sys.path.append("/usr/local/lib/python2.7/site-packages")
print "Content-type: text/html\n\n"

from time import asctime
import cgi
from marvinBugLogger import TcSearchLocalDb, Codes, MarvinBugLogger, MiscHandler
import os
from multiprocessing import Process
import threading
from subprocess import Popen

def logBugs(version, build, hyptype, type):
    logger = MiscHandler.getLogger()
    if not version and not build and not hyptype and not type:
        print "\n=== Invalid Inputs==="
        logger.debug("=== LogBugs: Invalid Inputs ===")
        return 
    tc_search_local_db_obj = TcSearchLocalDb(logger)
    sub = "BugLogger Report : " + str(version)  + ":" + str(hyptype) + ":" + str(build) + ":" + str(type)
    if tc_search_local_db_obj:
        ret = tc_search_local_db_obj.insertBuildInfo(version, build, hyptype, type, '', Codes.STARTED, asctime())
        if ret != Codes.FAILED:
            print "\n==== Jobid : %s ====" %str(ret[0])
            #Popen("marvinBugLoggerService.py " + str(version) + " " + str(build) + " " + str(hyptype) + " " + str(type) + " " + str(ret[0]),shell=True)
            launchBugLoggerService(version,build,hyptype,type,ret[0])
            MiscHandler.sendEmail(sub,"===Adding Job Successful.Please Check===")
            return 
    MiscHandler.sendEmail(sub,"===Adding Job Failed.Please Check===")

'''
def launchBugLoggerService(version,build,hyptype,type,jobid):
    obj_marvin_buglogger = MarvinBugLogger(version,build,hyptype,type,jobid)
    obj_marvin_buglogger.init()
'''
  
        
def launchBugLoggerService(version,build,hyptype,type,jobid):
    obj_marvin_buglogger = MarvinBugLogger(version,build,hyptype,type,jobid)
    p = Process(target=obj_marvin_buglogger.init(),args=())
    p.start()
    return 

def getJobStatus(jobid):
    logger = MiscHandler.getLogger()
    tc_search_local_db_obj = TcSearchLocalDb(logger)
    if tc_search_local_db_obj:
        ret = tc_search_local_db_obj.getJobStatus(jobid)
        if ret != FAILED:
            print "\n==== Jobid : %s . Status : %s====" %(str(jobid),str(status))

def deleteBugs(bugs):
    logger = MiscHandler.getLogger()
    tc_search_local_db_obj = TcSearchLocalDb(logger)
    if tc_search_local_db_obj:
        if tc_search_local_db_obj.deleteBugs(bugs) == Codes.FAILED:
            print "\n==== MarvinBugLogger Deletion Failed ===="
        else:
            print "\n==== MarvinBugLogger Deletion Successful===="

def main():
    fields = cgi.FieldStorage()
    if fields["cmd"].value == Codes.LogBugs:
        #print "\n==== Received Command :LogBugs. Arguments : Version : %s Build : %s HypType : %s Component : %s==== "%(fields["version"],fields["build"],fields["hyptype"],fields["type"])
        logBugs(fields["version"].value,fields["build"].value,fields["hyptype"].value,fields["type"].value)
    if fields["cmd"].value == Codes.DeleteBugs:
        print "\n==== Received Command:DeleteBugs.===="
        deleteBugs(fields["bugs"].value)
    if fields["cmd"].value == Codes.GetJobStatus:
        print "\n==== Received Command:GetJobStatus.===="
        getJobStatus(fields["jobid"].value)

main()

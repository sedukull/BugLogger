'''
Config Part of Bug Filing
'''
import sys
import traceback

sys.path.append("/usr/lib/python2.7")
sys.path.append("/usr/lib/python2.7/site-packages")
sys.path.append("/usr/local/lib/python2.7")
sys.path.append("/usr/local/lib/python2.7/site-packages")

BugLoggerConfig = {
    "BUG_TRACKER_SRVR_DETAILS":
    {
        "URL": "http://bugs-ccp.citrix.com/",
        #"URL" : "http://10.223.240.213:8080/",
        "USER": "santhoshe",
        "PASSWD": "asdf!@34"
    },
    "FAILURE":
    {
        "ASSIGNEE": "santhoshe",
        "PROJECT": "CS",
        "COMPONENTS": "Automation"
    },
    "ERROR":
    {
        "ASSIGNEE": "santhoshe",
        "PROJECT": "CS",
        "COMPONENTS": "Automation"
    },
    "MISC_DETAILS":
    {
        "VERIFY_BUG_STATUS_IN_DB":True,
        "ENVIRONMENT": "NA",
        "DESCRIPTION": "Test Case Failed. Attached are CS and Test Run Logs",
        "PRIORITY": 3,
        "STATUS": "open",
        "RESOLUTION": "resolved",
        "COMPONENTS": "Automation",
        "CS_LOG_PATH": "",
        "TEST_LOGS": "",
        "TYPE": "Bug",
        "COMPRESSED": "yes",
        "TEST_OUT_FOLDER_MNT_PATH":"/root/softwares/BugLogger/nfs_mnt_jenkins_out_log_path/",
        "BUGS_OUTPUT_PATH":"/root/softwares/BugLogger/bugs_out/",
        "BUG_EXCLUSIONS":"/root/softwares/BugLogger/bug_exclusions/",
        "CS_LOG_FILE_NAME":"management-server-logs.tar.gz",
        "TC_RUN_LOG_FILE":"tc_run_log.tar.gz",
        "EMAIL_USERS":"santhosh.edukulla@citrix.com",
        "FROM_EMAIL_ADDRESS":"santhosh.edukulla@citrix.com",
        "LOG_ERROR_BUGS":"yes",
        "LOG_PATH":"/root/softwares/BugLogger/bugs_out/logs/",
        "UPDATE_SLEEP_TIME":3600,
        "ATTACH_LOG_TO_BUG":False,
        "NFS_SERVER":"http://nfs1.lab.vmops.com/automation/",
        "MAX_ATTACHMENT_SIZE":10
    },
    "DB_DETAILS":
    {
       "DB_HOST":"localhost",
       "DB_USER":"root",
       "DB_PASSWD":"password",
       "CATALOG":"cloud_bugs"   
    }
}

class Codes:
    STARTED = "started"
    FAILED = "failed"
    SUCCESS = "success"
    FINISH = "finished"
    STOPPED = "stopped"
    EXCEPTION_OCCURRED = "Exception Occurred"
    LogBugs = "LogBugs"
    DeleteBugs = "DeleteBugs"
    GetJobStatus = "GetJobStatus"
    OPEN = "open"
    REOPEN = "reopen" 
    NA = "Not Applicable"

    @staticmethod
    def GetDetailExceptionInfo(e):
        if e is not None:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            return str(repr(traceback.format_exception(
                exc_type, exc_value, exc_traceback)))
        else:
            return Codes.EXCEPTION_OCCURRED

    @staticmethod
    def GetCustomCodes(key):
        customfield_dict = {"severity": {"customfield_10001": "Normal"},
                           "DefectSource" :{"customfield_10803":"Internal"},
                           "Regression":{"customfield_10801" : "Yes"}}
       
        for k,value in customfield_dict.keys():
            if k == key:
                return value
        return None   

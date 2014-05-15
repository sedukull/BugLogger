#!/usr/bin/python2.7

import sys
sys.path.append("/usr/lib/python2.7")
sys.path.append("/usr/lib/python2.7/site-packages")
sys.path.append("/usr/local/lib/python2.7")
sys.path.append("/usr/local/lib/python2.7/site-packages")
from time import asctime
import cgi
from marvinBugLogger import TcSearchLocalDb, Codes, MiscHandler
from marvinBugLoggerConfig import BugLoggerConfig
import logging
import sys

#!/usr/bin/python
import time
from daemon import runner
'''
class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/bugloggerupdate.pid'
        self.pidfile_timeout = 5

    def run(self):
        logger = MiscHandler.getLogger(default="Update")
        sleep_tm = BugLoggerConfig["MISC_DETAILS"]["UPDATE_SLEEP_TIME"]
        while True:
            logger.debug(
                "====Update Service Starting.Time : %s ==== " %
                str(asctime))
            try:
                tc_search_local_db_obj = TcSearchLocalDb(logger)
                if tc_search_local_db_obj:
                    rows = tc_search_local_db_obj.fetchAllIssues()
                    if rows != Codes.FAILED:
                        jira_obj = JiraManager(logger)
                        ret = jira_obj.getBugsInfo(rows)
                        if ret != Codes.FAILED:
                            if tc_search_local_db_obj.updateBugInfo(ret) == FAILED:
                                logger.debug(
                                    "==== updateService Failed ==== :%s" %
                                    asctime())
                            else:
                                logger.debug(
                                    "==== updateService Successful ==== :%s" %
                                    asctime())
            except Exception as e:
                logger.debug(
                    "\n==== updateService Failed : %s====" %
                    Codes.GetDetailExceptionInfo(e))
            finally:
                logger.debug(
                    "==== Sleeping for %s seconds. Time : %s====" %
                    (str(sleep_tm), str(asctime)))
                time.sleep(sleep_tm) 

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
'''
def updateService(logger):
    try:
        tc_search_local_db_obj = TcSearchLocalDb(logger)
        if tc_search_local_db_obj:
            rows = tc_search_local_db_obj.fetchAllIssues()
            if rows != Codes.FAILED:
                jira_obj = JiraManager(logger)
                ret = jira_obj.getBugsInfo(rows)
                if ret != Codes.FAILED:
                    if tc_search_local_db_obj.updateBugInfo(ret) == FAILED:
                        logger.debug(
                            "==== updateService Failed ==== :%s" %
                            asctime())
                    else:
                        logger.debug(
                            "==== updateService Successful ==== :%s" %
                            asctime())
    except Exception as e:
        logger.debug(
            "\n==== updateService Failed : %s====" %
            Codes.GetDetailExceptionInfo(e))
        return Codes.FAILED

if __name__ != "__main__":
    logger = MiscHandler.getLogger(default="Update")
    sleep_tm = BugLoggerConfig["MISC_DETAILS"]["UPDATE_SLEEP_TIME"]
    while True:
        logger.debug(
            "====Update Service Starting.Time : %s ==== " %
            str(asctime))
        updateService(logger)
        logger.debug(
            "==== Sleeping for %s seconds. Time : %s====" %
            (str(sleep_tm), str(asctime)))
        time.sleep(sleep_tm)

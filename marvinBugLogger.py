#!/usr/bin/python2.7

import sys

sys.path.append("/usr/lib/python2.7")
sys.path.append("/usr/lib/python2.7/site-packages")
sys.path.append("/usr/local/lib/python2.7")
sys.path.append("/usr/local/lib/python2.7/site-packages")

from xunitparser import parse
from jira.client import JIRA
from marvinBugLoggerConfig import BugLoggerConfig, Codes
import gzip
import os
import zlib
import time
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from marvinBugLoggerDal import TcSearchLocalDb
from optparse import OptionParser


class TcResultParser:

    def __init__(self, xunit_file_folder, logger):
        self.__xunitOutFolder = xunit_file_folder
        self.__ts = None
        self.__tr = None
        self.__parsedTCResultDict = {}
        self.__logger = logger

    def getParsedTCResultInfo(self):
        try:
            self.__logger.debug(
                "=== Test Results Folder : %s===" %
                self.__xunitOutFolder)
            test_suites = []
            if self.__xunitOutFolder:
                if os.path.isdir(self.__xunitOutFolder):
                    for items in os.listdir(self.__xunitOutFolder):
                        if os.path.isfile(self.__xunitOutFolder + "/" + items) and items.startswith("test") and items.endswith("xml"):
                            test_suites.append(items)
                for files in test_suites:
                    self.__logger.debug(
                        "==== Retrieving Test Results Information for Test Suite:%s ====" %
                        str(files))
                    with open(self.__xunitOutFolder + "/" + files) as f:
                        self.__ts, self.__tr = parse(
                            self.__xunitOutFolder + "/" + files)
                    for tc in self.__ts:
                        if tc and (tc.result.lower() in ['failure', 'error']):
                            if tc.classname and tc.methodname:
                                key = tc.classname + "." + tc.methodname
                                self.__parsedTCResultDict[key] = [tc.result,
                                                                  MiscHandler.compressString(
                                                                      tc.message),
                                                                  MiscHandler.compressString(tc.trace)]
            if self.__parsedTCResultDict and len(self.__parsedTCResultDict) == 0:
                self.__logger.debug(
                    "\n======No Failed or Error Cases under : %s====" %
                    str(self.__xunitOutFolder))
                return Codes.FAILED
            self.__logger.debug(
                "==== Total Failed and Error Cases:%s ====" % len(
                    self.__parsedTCResultDict.keys()))
            return self.__parsedTCResultDict
        except Exception as e:
            self.__logger.debug(
                "\nParsing Xunit Test Output Failed : %s" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED


class MiscHandler:

    def __init__(self, logger, **kwargs):
        self.__inp = kwargs
        self.__compressedFilesInfo = {}
        self.__initializeCompressStructures()
        self.__logger = logger

    def __initializeCompressStructures(self):
        if self.__inp:
            for key, value in self.__inp.items():
                self.__compressedFilesInfo[key] = value

    @staticmethod
    def getLogger(default=None):
        try:
            logger = logging.getLogger('MarvinBugLogger')
            log_format = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s")
            if default:
                file_path = BugLoggerConfig[
                    "MISC_DETAILS"][
                    "LOG_PATH"] + "/misc/" + str(default) + "_Misc_MarvinBugLogger_" + str(time.strftime("%b_%d_%Y_%H_%M_%S",
                                                                                                         time.localtime()) + ".txt")
            else:
                file_path = BugLoggerConfig[
                    "MISC_DETAILS"][
                    "LOG_PATH"] + "/misc/" + "_Misc_MarvinBugLogger_" + str(time.strftime("%b_%d_%Y_%H_%M_%S",
                                                                                          time.localtime()) + ".txt")
            ch = logging.FileHandler(file_path, mode="a")
            ch.setFormatter(log_format)
            ch.setLevel(logging.DEBUG)
            logger.addHandler(ch)
            return logger
        except Exception as e:
            print "\n ==== Exception Occurred under getLogger:%s" % Codes.GetDetailExceptionInfo(e)

    @staticmethod
    def verifyFile(file_inp):
        # Need to check here, it returns false currently.
        return True
        if file_inp and file_inp != '':
            print os.path.exists(file_inp)
            return os.path.exists(file_inp)
        return False

    def __verifyAndCompressFiles(self):
        for key, value in self.__inp.items():
            if MiscHandler.verifyFile(value):
                ret = MiscHandler.compress(value)
                if ret != Codes.FAILED:
                    self.__compressedFilesInfo[key] = ret

    @staticmethod
    def DeCompress(file_to_decompress, out_path):
        try:
            if MiscHandler.verifyFile(file_to_decompress):
                cmd = "unzip " + file_to_decompress + " -d" + out_path
                os.system(cmd)
                return Codes.SUCCESS
            return Codes.FAILED
        except Exception as e:
            print "\n=========DeCompression failed: %s ====" % Codes.GetDetailExceptionInfo(e)
            return Codes.FAILED

    @staticmethod
    def sendEmail(sub="===BugLogger Report===", msg="Logging Bugs Failed"):
        if BugLoggerConfig["MISC_DETAILS"]["FROM_EMAIL_ADDRESS"]:
            sender = BugLoggerConfig["MISC_DETAILS"]["FROM_EMAIL_ADDRESS"]
        if BugLoggerConfig["MISC_DETAILS"]["EMAIL_USERS"]:
            receivers = BugLoggerConfig["MISC_DETAILS"]["EMAIL_USERS"]
        msg = MIMEMultipart('alternative')
        msg['Subject'] = sub
        msg['From'] = sender
        msg['To'] = receivers
        part1 = MIMEText(msg, 'plain')
        msg.attach(part1)
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, msg.as_string())
        smtpObj.quit()

    @staticmethod
    def notifyReport(mail_subject, failedBugCnt,
                     failedBugMisses, errorBugCnt, errorBugMisses, txt="===Bug Logger Report==="):
        try:
            if BugLoggerConfig["MISC_DETAILS"]["FROM_EMAIL_ADDRESS"]:
                sender = BugLoggerConfig["MISC_DETAILS"]["FROM_EMAIL_ADDRESS"]
            if BugLoggerConfig["MISC_DETAILS"]["EMAIL_USERS"]:
                receivers = BugLoggerConfig["MISC_DETAILS"]["EMAIL_USERS"]
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "[Automation]: Bug Log Report :" + \
                             str(mail_subject)
            msg['From'] = sender
            msg['To'] = receivers
            html_str = "<html> \
                        <head></head> \
                        <body><table border=\"1\"> \
                         <tr> \
                         <th>Item</th> \
      			 <th>Bugs Logged</th> \
                         <th>Bugs Missed</th> \
                         </tr> \
                         <tr> \
                         <td> Failed </td><td>" + str(failedBugCnt) + "</td><td>" + str(failedBugMisses) + "</td></tr><tr><td> Error </td><td>" + str(errorBugCnt) + "</td><td>" + str(errorBugMisses) + "</td></tr></table></body></html>"

            part1 = MIMEText(txt, 'plain')
            part2 = MIMEText(html_str, 'html')
            msg.attach(part1)
            msg.attach(part2)
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, receivers, msg.as_string())
            smtpObj.quit()
            print "Successfully sent email"
            return Codes.SUCCESS
        except Exception as e:
            print "Error: unable to send email : %s" % str(e)
            return Codes.FAILED

    @staticmethod
    def compressString(inp):
        return zlib.compress(inp) if inp else "None"

    @staticmethod
    def decompressString(inp):
        return zlib.decompress(inp) if inp else "None"

    @staticmethod
    def compress(dir_in, dir_out, zip_file_name):
        try:
            cmd = "tar -zcvf " + dir_out + "/" + zip_file_name + " " + dir_in
            os.system(cmd)
            return Codes.SUCCESS
        except Exception as e:
            print "\n====Exception Occurred under compress : %s====" % Codes.GetDetailExceptionInfo(e)
            return Codes.FAILED

    @staticmethod
    def attachFileToBug(issue_key, file, jira_conn, logger):
        try:
            if BugLoggerConfig["MISC_DETAILS"]["ATTACH_LOG_TO_BUG"]:
                if os.path.isfile(file) and jira_conn:
                    st = os.stat(file)
                    sz = (st.st_size / 1048576)
                    if sz > BugLoggerConfig["MISC_DETAILS"]["MAX_ATTACHMENT_SIZE"]:
                        logger.debug(
                            "=== File : %s Size : %s is too high to attach===" %
                            (file, str(sz)))
                        return
                    retry = 0
                    while retry < 2:
                        try:
                            with open(file) as f:
                                jira_conn.add_attachment(issue_key, f)
                                break
                        except Exception as e:
                            retry = retry + 1
                            continue
                    logger.debug(
                        "=== Bug : %s .Attaching Logs Successfull ===" %
                        str(issue_key))
            logger.debug("=== Attaching Logs to Bug Disabled ===")
        except Exception as e:
            logger.debug(
                "=== Attaching Log to Bug Failed===%s" %
                Codes.GetDetailExceptionInfo(e))

    def getCompressedFileInfo(self):
        self.__verifyAndCompressFiles()
        return self.__compressedFilesInfo


class MarvinBugLogger:

    def __init__(self, version, build, hypervisor, type, jobid):
        self.__connected = False
        self.__build = build
        self.__version = version
        self.__hypervisorType = hypervisor
        self.__buildBugsOutFolder = None
        self.__buildTestOutFolder = None
        self.__csLogs = None
        self.__type = type
        self.__tcLogs = None
        self.__logger = None
        self.__errorBugCnt = 0
        self.__failedBugCnt = 0
        self.__failedBugMisses = 0
        self.__errorBugMisses = 0
        self.__nfsLogPath = None
        self.__jobid = jobid
        self.__tcResultsPath = None

    def __initLogging(self):
        logFormat = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s")
        logger = logging.getLogger("MarvinBugLogger")
        logger.setLevel(logging.DEBUG)
        temp_dir = BugLoggerConfig["MISC_DETAILS"][
            "LOG_PATH"] + "/" + str(self.__hypervisorType)
        log_file_path = temp_dir + "/" + "MarvinBugLogger_" + str(self.__version) + "_" + str(self.__build) + "_Job_" + str(self.__jobid) + "_" + \
            time.strftime("%b_%d_%Y_%H_%M_%S",
                          time.localtime())
        stream = logging.FileHandler(log_file_path)
        stream.setFormatter(logFormat)
        stream.setLevel(logging.DEBUG)
        logger.addHandler(stream)
        self.__logger = logger

    def __parseOptions(self):
        parser = OptionParser()
        parser.add_option("-t", "--type", action="store",
                          default="bvt",
                          dest="component")
        parser.add_option("-v", "--version", action="store_true",
                          dest="version")
        parser.add_option("-b", "--build", action="store",
                          dest="build")
        parser.add_option("-h", "--hypervisor", action="store",
                          dest="hypervisor")
        parser.add_option("-j", "--job", action="store",
                          dest="job")
        (options, args) = parser.parse_args()
        print "\n=== Options === ", options, dir(options)
        if (not options.t or not options.v or not options.b or not options.h or not options.j):
            print "\n==== Invalid Options, Please Check ===="
            return Codes.FAILED
        self.__build = options.b
        self.__version = options.v
        self.__hypervisorType = options.h
        self.__type = options.t
        self.__jobid = options.j
        self.__tcResultsPath = None
        return Codes.SUCCESS

    def __setValues(self):
        self.JIRA_URL = BugLoggerConfig["BUG_TRACKER_SRVR_DETAILS"]["URL"]
        self.JIRA_USER = BugLoggerConfig[
            "BUG_TRACKER_SRVR_DETAILS"][
            "USER"]
        self.JIRA_PASSWD = BugLoggerConfig[
            "BUG_TRACKER_SRVR_DETAILS"][
            "PASSWD"]
        self.__buildTestOutFolder = BugLoggerConfig["MISC_DETAILS"][
            "TEST_OUT_FOLDER_MNT_PATH"] + "/" + self.__version + "/" + self.__hypervisorType + "/" + str(self.__build) + ".zip"
        self.__buildBugsOutFolder = BugLoggerConfig[
            "MISC_DETAILS"][
            "BUGS_OUTPUT_PATH"] + "/" + self.__version + "_" + self.__hypervisorType + "_" + str(self.__build) + "_" + str(self.__jobid)
        self.__nfsLogPath = BugLoggerConfig["MISC_DETAILS"]["NFS_SERVER"] + "/" + \
            str(self.__version) + "/" + str(self.__hypervisorType) + "/" + \
            str(self.__build) + ".zip"
        os.makedirs(self.__buildBugsOutFolder)

    def __unzipBugsInfo(self):
        '''
        First extract the contents under main zip folder.
        '''
        try:
            if (MiscHandler.DeCompress(self.__buildTestOutFolder, self.__buildBugsOutFolder) == Codes.SUCCESS):
                for root, dirs, files in os.walk(self.__buildBugsOutFolder):
                    if 'test_results.zip' in files:
                        self.__tcResultsPath = root + "/" + "test_results"
                        os.mkdir(self.__tcResultsPath)
                        if MiscHandler.DeCompress(root + "/" + "test_results.zip", self.__tcResultsPath) == Codes.SUCCESS:
                            self.__logger.debug(
                                "==== DeCompressing the test results Successful ====")
                            break
                for root, dirs, files in os.walk(self.__buildBugsOutFolder):
                    if 'test_run.zip' in files:
                        self.__tcLogs = root + "/" + "test_run.zip"
                        self.__logger.debug(
                            "=== Test Run Logs : %s===" % str(
                                self.__tcLogs))
                for root, dirs, files in os.walk(self.__buildBugsOutFolder):
                    if 'management' in dirs and 'var/log' in root:
                        self.__csLogs = root + "/" + \
                            dirs[dirs.index("management")]
                        if self.__csLogs and MiscHandler.compress(self.__csLogs, self.__buildBugsOutFolder, BugLoggerConfig["MISC_DETAILS"]["CS_LOG_FILE_NAME"]) == Codes.SUCCESS:
                            self.__logger.debug(
                                "==== Compressing the management server logs Successful ====")
                            self.__csLogs = self.__buildBugsOutFolder + "/" + \
                                BugLoggerConfig["MISC_DETAILS"][
                                    "CS_LOG_FILE_NAME"]
                            break
                self.__logger.debug(
                    "===Extracting Bug Information Successful. Build : %s and Version :%s===" %
                    (self.__build, self.__version))
                return Codes.SUCCESS
        except Exception as e:
            self.__logger.debug(
                "\n===Extracting Bug Information Failed. Build : %s and Version :%s===" %
                (self.__build, self.__version))
            return Codes.FAILED

    def __cleanFolders(self):
        os.system("rm -rf " + self.__buildBugsOutFolder)

    def init(self):
        try:
            self.__setValues()
            self.__initLogging()
            mail_subject = "[Automation]:" + \
                           str(self.__version) + ":" + \
                           str(self.__hypervisorType) + ":" + str(self.__build)
            self.__logger.debug(
                "==== Starting Bug Logger : %s ==== " %
                mail_subject)
            '''
            Unzip the bugs information folder
            '''
            if self.__unzipBugsInfo() != Codes.FAILED:
                tc_res_obj = TcResultParser(
                    self.__buildBugsOutFolder + "/test_results/",
                    self.__logger)
                '''
                Retrieve failed or error cases from tc results information
                '''
                parsed_tc_results = tc_res_obj.getParsedTCResultInfo()
                if parsed_tc_results == Codes.FAILED:
                    sub = "BugLogger Report : " + \
                        str(self.__version) + ":" + \
                        str(self.hhypervisorType) + ":" + str(self.__build)
                    MiscHandler.sendEmail(
                        sub,
                        "===Parsing TC Results Failed.Please Check===")
                    return
                '''
                Remove Bugs which are added for exclusions
                '''
                after_exclusion_bugs = self.removeExclusions(parsed_tc_results)
                if len(after_exclusion_bugs) == 0:
                    self.__logger.debug("=== No Bugs to Log. So, exiting===")
                    return
                '''
                Search local db for open bugs before logging
                '''
                tc_search_local_db_obj = TcSearchLocalDb(self.__logger)
                rows = []
                if BugLoggerConfig["MISC_DETAILS"]["VERIFY_BUG_STATUS_IN_DB"]:
                    rows = tc_search_local_db_obj.retrieveBugsForGivenHypTypeAndVersion(
                        self.__hypervisorType,
                        self.__version)
                    if not rows or (rows and not len(rows)):
                        self.__logger.debug(
                            "==== No Bugs in local DB for this version:%s. Hypervisor :%s ===" %
                            (str(self.__version), str(self.__hypervisorType)))
                final_bugs = self.getFinalBugsToLogInfo(
                    rows,
                    after_exclusion_bugs)
                if final_bugs == Codes.FAILED:
                    self.__logger.debug(
                        "=== No Bugs to log for this version : %s. Hypervisor: %s===" %
                        (str(self.__version), str(self.__hypervisorType)))
                else:
                    if self.logBugs(final_bugs, tc_search_local_db_obj) == Codes.FAILED:
                        tc_search_local_db_obj.updateBuildInfo(
                            self.__jobid,
                            self.__buildBugsOutFolder,
                            Codes.FAILED)
                    else:
                        tc_search_local_db_obj.updateBuildInfo(
                            self.__jobid,
                            self.__buildBugsOutFolder,
                            Codes.FINISH)
                '''
                Notify Users Post Logging
                '''
                if MiscHandler.notifyReport(mail_subject,
                                            self.__failedBugCnt,
                                            self.__failedBugMisses,
                                            self.__errorBugCnt,
                                            self.__errorBugMisses) == Codes.FAILED:
                    self.__logger.debug(
                        "==== Sending Email Notification Failed :%s ====" %
                        mail_subject)
                else:
                    self.__logger.debug(
                        "==== Sending Email Notification Successful :%s ====" %
                        mail_subject)
                    self.__cleanFolders()
            self.__logger.debug(
                "==== Finished Bug Logger : %s ==== " %
                mail_subject)
            return
        except Exception as e:
            self.__logger.debug(
                "====Exception Occurred under init :%s====" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def getFinalBugsToLogInfo(self, db_rows, to_search_bugs):
        try:
            failure_dict = {}
            error_dict = {}
            '''
            Check if DB has no rows to compare for bugs, return failure and error dicts for logging
            '''
            if len(db_rows) == 0:
                for testname, test_elem in to_search_bugs.items():
                    if test_elem[0] == "failure":
                        failure_dict[testname] = test_elem
                    if test_elem[0] == "error":
                        error_dict[testname] = test_elem
                return [failure_dict, error_dict]
            for testname, test_elem in to_search_bugs.items():
                test_name_match_check = False
                for row in db_rows:
                    if testname == row[0]:
                        test_name_match_check = True
                        '''
                        TestName matched but the bug is not in open state in local db
                        '''
                        if row[1] not in ["opened"]:
                            if test_elem[0] == "failure":
                                failure_dict[testname] = test_elem
                            if test_elem[0] == "error":
                                error_dict[testname] = test_elem
                        '''
                        TestName matched, bug is open but the test message didn't matched
                        '''
                        if row[1] in ["opened"] and row[3] != test_elem[1]:
                            if test_elem[0] == "failure":
                                failure_dict[testname] = test_elem
                            if test_elem[0] == "error":
                                error_dict[testname] = test_elem
                if test_name_match_check is False:
                    if test_elem[0] == "failure":
                        failure_dict[testname] = test_elem
                    if test_elem[0] == "error":
                        error_dict[testname] = test_elem
            return [failure_dict, error_dict]
        except Exception as e:
            self.__logger.debug(
                "==== getFinalBugsToLogInfo :Retrieving: Final Bugs to Log Failed : %s ==== " %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def removeExclusions(self, bugs_dict):
        '''
        @Desc : Search for exclusions in a file for a given hypervisor type and version
                Eliminates the bugs which needs to be excluded and return final dict for logging
        '''
        try:
            final_dict = {}
            file_path = ''
            check_exclusion = False
            if os.path.isdir(BugLoggerConfig["MISC_DETAILS"]["BUG_EXCLUSIONS"] + str(self.__version)):
                file_path = BugLoggerConfig["MISC_DETAILS"][
                    "BUG_EXCLUSIONS"] + str(self.__version) + "/" + "bug_exclusions.txt"
                if os.path.isfile(file_path):
                    check_exclusion = True
            if check_exclusion is False:
                self.__logger.debug(
                    "=== Found No Exclusions File for Version: %s====" %
                    (self.__version))
                return bugs_dict
            with open(file_path) as f:
                rows = f.readlines()
            final_rows = []
            for row in rows:
                # hyp_type,test_name,message
                temp = row.split(",")
                if temp[0].lower() == self.__hypervisorType.lower():
                    final_rows.append(temp)
            for testname, testinfo in bugs_dict.items():
                matched = False
                for row in final_rows:
                    if row[1] == testname:
                        if row[2] != '' and row[2] == MiscHandler.deCompressString(testinfo[1]):
                            matched = True
                            break
                if not matched:
                    final_dict[testname] = testinfo
            if len(final_dict) == 0:
                self.__logger.debug(
                    "==== After exclusion Checks, no Bugs to be logged for Hypervisor : %s Version:%s ====" %
                    (self.__hypervisorType, self.__version))
            return final_dict
        except Exception as e:
            self.__logger.debug(
                "====Exception Occurred under removeExclusions: %s====" %
                Codes.GetDetailExceptionInfo(e))
            return final_dict

    def logBugs(self, bugs_lst, tc_search_local_db):
        try:
            self.__logger.debug("==== Logging Bugs Started ===")
            if len(bugs_lst[0]) != 0:
                self.__logger.debug(
                    " === I: Logging Failed Bugs. Total : %s === " % (str(len(bugs_lst[0]))))
                failed_bugs = self.__logFailedBugs(bugs_lst[0])
                temp = []
                if failed_bugs != Codes.FAILED:
                    self.attachLogsToBugs(failed_bugs)
                    if BugLoggerConfig["MISC_DETAILS"]["VERIFY_BUG_STATUS_IN_DB"]:
                        for k, v in failed_bugs.items():
                            temp.append({"bugid": v[3],
                                         "testname": k,
                                         "type": self.__type,
                                         "version": self.__version,
                                         "result": v[0],
                                         "message": v[1],
                                         "hwtype": self.__hypervisorType,
                                         "subject": v[4],
                                         "trace": v[2],
                                         "updated_date": time.asctime(),
                                         "state": "opened",
                                         "buildjob": self.__jobid})
                        tc_search_local_db.addBugInfoToDb(temp)
            if not BugLoggerConfig["MISC_DETAILS"]["LOG_ERROR_BUGS"]:
                self.__logger.debug("=== Logging Error Bugs Disabled === ")
            else:
                if len(bugs_lst[1]) != 0:
                    self.__logger.debug(
                        " === II : Logging Error Bugs : Total : %s === " % (str(len(bugs_lst[1]))))
                    temp = []
                    error_bugs = self.__logErrorBugs(bugs_lst[1])
                    if error_bugs != Codes.FAILED:
                        self.attachLogsToBugs(error_bugs)
                        if BugLoggerConfig["MISC_DETAILS"]["VERIFY_BUG_STATUS_IN_DB"]:
                            for k, v in error_bugs.items():
                                temp.append({"bugid": v[3],
                                             "testname": k,
                                             "type": self.__type,
                                             "version": self.__version,
                                             "result": v[0],
                                             "message": v[1],
                                             "hwtype": self.__hypervisorType,
                                             "subject": v[4],
                                             "trace": v[2],
                                             "updated_date": time.asctime(),
                                             "state": "opened",
                                             "buildjob": self.__jobid})
                            tc_search_local_db.addBugInfoToDb(temp)
            return Codes.SUCCESS
        except Exception as e:
            self.__logger.debug(
                "==== logBugs Failed : %s====" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def attachLogsToBugs(self, bugs_dict):
        try:
            for key, value in bugs_dict.items():
                if value[0] == "error" and str(value[3]).lower() != "nobug":
                    MiscHandler.attachFileToBug(
                        value[3],
                        self.__tcLogs,
                        self.__jira,
                        self.__logger)
                if value[0] == "failure" and str(value[3]).lower() != "nobug":
                    MiscHandler.attachFileToBug(
                        value[3],
                        self.__csLogs,
                        self.__jira,
                        self.__logger)
        except Exception as e:
            self.__logger.debug(
                "=== Exception Occurred Under attachLogsToBugs: %s" %
                Codes.GetDetailExceptionInfo(e))

    def __logErrorBugs(self, bugs_dict):
        try:
            project = BugLoggerConfig["ERROR"]["PROJECT"]
            assignee = BugLoggerConfig["ERROR"]["ASSIGNEE"]
            component = BugLoggerConfig["ERROR"]["COMPONENTS"]
            if bugs_dict:
                for test_name, test_values in bugs_dict.items():
                    try:
                        self.__logger.debug(
                            "=== TestName :%s ===" %
                            str(test_name))
                        summary = "Automation:TCError123 " + \
                            test_name + " Failed"
                        environment_str = "Hypervisor:" + self.__hypervisorType
                        ret = self.__searchIssue(
                            project,
                            summary.strip("\n"),
                            self.__version,
                            environment_str)
                        if ret != Codes.FAILED:
                            for issue in ret:
                                self.__logger.debug(
                                    "==== Issue with given details :%s Already available in Jira in open,reopen,inprogress state=== " % str(
                                        issue.key))
                                comment = "Observed the issue again in Build :" + \
                                    str(self.__build) + "\n====Log File Path Below : ==== \n" + \
                                    str(self.__nfsLogPath)
                                self.__jira.add_comment(
                                    issue.key,
                                    comment)
                            continue
                        else:
                            self.__logger.debug(
                                "==== Issue does not exist in Jira in open,reopen,inprogress state, will create one=== ")
                        description = "\n====Log File Path Below : ==== \n" + \
                                      str(self.__nfsLogPath) + "\n\n"
                        if BugLoggerConfig["MISC_DETAILS"]["ATTACH_LOG_TO_BUG"]:
                            description = description + \
                                "\n==== log files are attached to this bug====\n"

                        description = description + "====Failure Message:====\n" + \
                            MiscHandler.decompressString(test_values[1])
                        description = description + "\n\n====Trace Observed====\n" + \
                            MiscHandler.decompressString(test_values[2])

                        if self.__connected or self.__connectToBugTracker():
                            self.__logger.debug(
                                "==== Test Name : %s to be logged ===" %
                                (str(test_name)))
                            #self.__logger.debug("summary:%s environment:%s component:%s assignee:%s version:%s "%(summary,environment_str,component,assignee,self.__version))
                            issue = self.__jira.create_issue(
                                project={"key": project},
                                summary=summary.strip("\n"),
                                issuetype={
                                    "name": "Bug"},
                                priority={
                                    "name": "P3"},
                                environment=environment_str,
                                description=description,
                                components=[
                                    {'name': component}],
                                assignee={
                                    'name': assignee},
                                versions=[{"name": str(self.__version)}],
                                customfield_10001={"value": "Normal"},
                                customfield_10803={"value": "Internal"},
                                customfield_10801={"value": "Yes"},
                                labels=["Automation"])
                            if issue:
                                self.__errorBugCnt = self.__errorBugCnt + 1
                                bugs_dict[test_name].append(issue.key)
                                bugs_dict[test_name].append(summary)
                                bugs_dict[test_name].append(environment_str)
                                self.__logger.debug(
                                    "=== Creating Jira Issue Successful ====")
                            else:
                                self.__errorBugMisses = self.__errorBugMisses + \
                                    1
                                bugs_dict[test_name].append("NoBug")
                                bugs_dict[test_name].append(summary)
                                bugs_dict[test_name].append(environment_str)
                                self.__logger.debug(
                                    "=== Creating Jira Issue Failed : %s====" %
                                    str(test_name))
                    except Exception as e:
                        self.__logger.debug(
                            "=== Exception in for loop logErrors :%s ===" %
                            Codes.GetDetailExceptionInfo(e))
                        continue
            self.__logger.debug(
                " === Finished Logging Bugs for Test Errors  ==== ")
            return bugs_dict
        except Exception as e:
            self.__logger.debug(
                "=== Exception occurred under __logErrorBugs %s" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def __searchIssue(self, project, summary, version, environ_str):
        try:
            if self.__connected or self.__connectToBugTracker():
                search_str = "project = %s and status in (%s) and affectedVersion in (%s) and summary ~ \"%s\" and environment ~ \"%s\"" % (
                    project,
                    "\"Open\",\"Reopened\",\"In Progress\"",
                    version,
                    summary,
                    environ_str)
                self.__logger.debug("==== Searching Issue :%s===" % search_str)
                issues = self.__jira.search_issues(search_str)
                if len(issues) == 0:
                    return Codes.FAILED
                return issues
            return Codes.FAILED
        except Exception as e:
            self.__logger.debug(
                "=== Searching Issue Failed : %s ===" %
                (Codes.GetDetailExceptionInfo(e)))
            return Codes.FAILED

    def __logFailedBugs(self, bugs_dict):
        try:
            project = BugLoggerConfig["FAILURE"]["PROJECT"]
            assignee = BugLoggerConfig["FAILURE"]["ASSIGNEE"]
            component = BugLoggerConfig["FAILURE"]["COMPONENTS"]
            if bugs_dict:
                for test_name, test_values in bugs_dict.items():
                    try:
                        self.__logger.debug(
                            "=== TestName :%s ===" %
                            str(test_name))
                        summary = "Automation:" + test_name + " Failed"
                        environment_str = "Hypervisor:" + \
                                          str(self.__hypervisorType)
                        ret = self.__searchIssue(
                            project,
                            summary.strip("\n"),
                            self.__version,
                            environment_str)
                        if ret != Codes.FAILED:
                            for issue in ret:
                                self.__logger.debug(
                                    "==== Issue with given details :%s Already available in Jira in open,reopen,inprogress state=== " % str(
                                        issue.key))
                                comment = "Observed the issue again in Build :" + \
                                    str(self.__build) + "\n====Log File Path Below : ==== \n" + \
                                    str(self.__nfsLogPath)
                                self.__jira.add_comment(
                                    issue.key,
                                    comment)
                            continue
                        else:
                            self.__logger.debug(
                                "==== Issue does not exist in Jira in open,reopen,inprogress state, will create one=== ")

                        description = "\n==== Log File Path Below : ==== \n" + \
                                      str(self.__nfsLogPath) + "\n\n"
                        if BugLoggerConfig["MISC_DETAILS"]["ATTACH_LOG_TO_BUG"]:
                            description = description + \
                                "\n==== Log Files are Attached here====\n"

                        description = description + "====Failure Message:====\n" + \
                            MiscHandler.decompressString(test_values[1])
                        description = description + "\n\n====Trace Observed====\n" + \
                            MiscHandler.decompressString(test_values[2])
                        if self.__connected or self.__connectToBugTracker():
                            self.__logger.debug(
                                "==== Test Name : %s ===" %
                                (str(test_name)))
                            #self.__logger.debug("summary:%s environment:%s component:%s assignee:%s version:%s description:%s"%(summary,environment_str,description,component,assignee,self.__version))
                            issue = self.__jira.create_issue(
                                project={"key": project},
                                summary=summary.strip(),
                                issuetype={
                                    "name": "Bug"},
                                priority={
                                    "name": "P3"},
                                environment=environment_str,
                                description=description,
                                components=[
                                    {'name': component}],
                                assignee={
                                    'name': assignee},
                                versions=[{"name": str(self.__version)}],
                                customfield_10001={"value": "Normal"},
                                customfield_10803={"value": "Internal"},
                                customfield_10801={"value": "Yes"},
                                labels=["Automation"])
                            if issue:
                                self.__failedBugCnt = self.__failedBugCnt + 1
                                bugs_dict[test_name].append(issue.key)
                                bugs_dict[test_name].append(summary)
                                bugs_dict[test_name].append(environment_str)
                                self.__logger.debug(
                                    "=== Creating Jira Issue Successful : %s ====" %
                                    str(test_name))
                            else:
                                self.__failedBugMisses = self.__failedBuMisses + \
                                    1
                                bugs_dict[test_name].append("NoBug")
                                bugs_dict[test_name].append(summary)
                                bugs_dict[test_name].append(environment_str)
                                self.__logger.debug(
                                    "=== Creating Jira Issue Failed : %s ====" %
                                    str(test_name))
                    except Exception as e:
                        self.__logger.debug(
                            "=== Exception in for loop : %s ====" %
                            Codes.GetDetailExceptionInfo(e))
                        continue
            self.__logger.debug(
                " === Finished Logging Bugs for Failures  === ")
            return bugs_dict
        except Exception as e:
            self.__logger.debug(
                "\n === Exception occurred under __logFailedBugs %s ===" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def __connectToBugTracker(self):
        try:
            self.__jira = JIRA(
                options={'server': self.JIRA_URL},
                basic_auth=(self.JIRA_USER,
                            self.JIRA_PASSWD))
            self.__jira.session()
            self.__connected = True
            return Codes.SUCCESS
        except Exception as e:
            self.__logger.debug(
                "Not able to connect to bug tracker: %s" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def isIssueOpen(self, issueKey):
        try:
            i = self.jira.issue(issueKey)
            if i and i.fields.status:
                res = i.fields.status.name
                if res.lower() in ['open', 'reopened', 'in progress']:
                    return True
            return False
        except Exception as e:
            self.__logger.debug(
                "Issue does not Exist %s" %
                Codes.GetDetailExceptionInfo(e))
            return False


class JiraManager:

    def __init__(self, logger):
        self.JIRA_URL = BugLoggerConfig["BUG_TRACKER_SRVR_DETAILS"]["URL"]
        self.JIRA_USER = BugLoggerConfig[
            "BUG_TRACKER_SRVR_DETAILS"][
            "USER"]
        self.JIRA_PASSWD = BugLoggerConfig[
            "BUG_TRACKER_SRVR_DETAILS"][
            "PASSWD"]
        self.__logger = logger
        self.__jira = None

    def __searchIssue(self, key):
        try:
            project = '"' + BugLoggerConfig["FAILURE"]["PROJECT"] + \
                      '",' + '"' + BugLoggerConfig["ERROR"]["PROJECT"] + '"'
            search_str = "project in (%s) and  key=%s" % (project, key)
            issues = self.__jira.search_issues(search_str)
            return issues
        except Exception as e:
            self.__logger.debug(
                " Search Issues Failed :%s" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def getBugsInfo(self, bugs_lst):
        try:
            self.__connectToBugTracker()
            return_dict = {}
            for items in bugs_lst:
                issues = self.__searchIssue(items[0])
                if issues != Codes.FAILED:
                    for issue in issues:
                        ret = self.isIssueOpen(issue.key)
                        if ret:
                            return_dict[issue.key] = "opened"
                        else:
                            return_dict[issue.key] = "resolved"
            return return_dict
        except Exception as e:
            self.__logger.debug(
                "Get Bugs Information Failed: %s" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def isIssueOpen(self, issueKey):
        i = self.jira.issue(issueKey)
        if i and i.fields.status:
            res = i.fields.status.name
            if res.lower() in ['open', 'reopened', 'in progress']:
                return True
        return False

    def __connectToBugTracker(self):
        try:
            self.__jira = JIRA(
                options={'server': self.JIRA_URL},
                basic_auth=(self.JIRA_USER,
                            self.JIRA_PASSWD))
            self.__jira.session()
            self.__connected = True
            return Codes.SUCCESS
        except Exception as e:
            self.__logger.debug(
                "Not able to connect to bug tracker: %s" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

if __import__ == "__main__":
    obj_marvin_buglogger = MarvinBugLogger()
    if obj_marvin_buglogger.init() == Codes.FAILED:
        print "\n==== MarvinBugLogger Initialization Failed ===="

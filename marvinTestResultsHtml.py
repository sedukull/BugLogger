#!/usr/bin/python2.7

from xunitparser import parse
from jira.client import JIRA
from marvinBugLoggerConfig import BugLoggerConfig, Codes
import gzip
import os
import zlib
import time
import logging
import smtplib
import HTML
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from marvinBugLoggerDal import TcSearchLocalDb
from optparse import OptionParser


class TcResultHtmlView:

    def __init__(self, xunit_file_folder, logger):
        self.__xunitOutFolder = xunit_file_folder
        self.__ts = None
        self.__tr = None
        self.__parsedTCResultDict = {}
        self.__logger = logger

    def generateHtmlView(self):
	try:
            self.__logger.debug(
                "=== Test Results Folder : %s===" %
                self.__xunitOutFolder)
	    """Create html table with rows 'SNo', 'TCName', 'Result','Time'"""
	    t = HTML.table(header_row=['SNo', 'TCName', 'Result', 'RunTime'])
            test_suites = []	
	    no = 1	
            if self.__xunitOutFolder:
                if os.path.isdir(self.__xunitOutFolder):
		    for items in os.listdir(self.__xunitOutFolder):
                        if os.path.isfile(self.__xunitOutFolder + "/" + items) and items.startswith("test") and items.endswith("xml"):
                            test_suites.append(items)
                for files in test_suites:
                    with open(self.__xunitOutFolder + "/" + files) as f:
                        self.__ts, self.__tr = parse(self.__xunitOutFolder + "/" + files)
                    for tc in self.__ts :
		        t.rows.append([no, tc.classname+"_"+tc.methodname, tc.result, tc.time.total_seconds()])
			no = no + 1
            return t
	except Exception as e:
	    self.__logger.debug(
		"\nParsing Xunit Test Output Failed : %s" % 
		Codes.GetDetailExceptionInfo(e))
	    return Codes.FAILED

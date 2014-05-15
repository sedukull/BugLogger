#!/usr/bin/python2.7

from marvinBugLoggerConfig import BugLoggerConfig, Codes
import sqlalchemy
import time
import sys



sys.path.append("/usr/lib/python2.7")
sys.path.append("/usr/lib/python2.7/site-packages")
sys.path.append("/usr/local/lib/python2.7")
sys.path.append("/usr/local/lib/python2.7/site-packages")

class TcSearchLocalDb:

    def __init__(self, logger):
        self.__logger = logger
        self.__engine = None
        self.__metaData = None
        self.DB_HOST = BugLoggerConfig["DB_DETAILS"]["DB_HOST"]
        self.DB_USER = BugLoggerConfig["DB_DETAILS"]["DB_USER"]
        self.DB_PASSWD = BugLoggerConfig["DB_DETAILS"]["DB_PASSWD"]
        self.DB_CATALOG = BugLoggerConfig["DB_DETAILS"]["CATALOG"]

    def __connect(self):
        try:
            self.__engine = sqlalchemy.create_engine(
                "mysql+mysqldb://" +
                self.DB_USER +
                ":" +
                self.DB_PASSWD +
                "@" +
                self.DB_HOST +
                "/" +
                self.DB_CATALOG)
            self.__metaData = sqlalchemy.MetaData(schema=self.DB_CATALOG)
        except Exception as e:
            self.__logger.debug(
                "\n=== Exception Occurred under __connect :%s" %
                Codes.GetDetailExceptionInfo(e))

    def fetchOpenIssues(self):
        try:
            self.__connect()
            bugs = sqlalchemy.Table(
                'bugs',
                self.__metaData,
                autoload=True,
                autoload_with=self.__engine)
            with self.__engine.connect() as conn:
                cur = conn.execute(
                    "select bugid from bugs where state in (\"open\",\"reopen\")")
                rows = cur.fetchall()
            return rows
        except Exception as e:
            self.__logger.debug(
                "\n=== Exception Occurred under __connect :%s" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def fetchAllIssues(self):
        try:
            self.__connect()
            bugs = sqlalchemy.Table(
                'bugs',
                self.__metaData,
                autoload=True,
                autoload_with=self.__engine)
            with self.__engine.connect() as conn:
                cur = conn.execute("select bugid from bugs")
                rows = cur.fetchall()
            return rows
        except Exception as e:
            self.__logger.debug(
                "\n=== Exception Occurred under __connect :%s" %
                Codes.GetDetailExceptionInfo(e))

    def deleteBugs(self, bugs):
        try:
            self.__connect()
            bugs = sqlalchemy.Table(
                'bugs',
                self.__metaData,
                autoload=True,
                autoload_with=self.__engine)
            with self.__engine.connect() as conn:
                conn.execute("delete from bugs where bugid in ( " + bugs + ")")
            return Codes.SUCCESS
        except Exception as e:
            self.__logger.debug(
                "\n=== Exception Occurred under __connect :%s" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def addBugInfoToDb(self, bugs_info):
        try:
            self.__connect()
            bugs = sqlalchemy.Table(
                'bugs',
                self.__metaData,
                autoload=True,
                autoload_with=self.__engine)
            with self.__engine.connect() as conn:
                conn.execute(bugs.insert(), bugs_info)
        except Exception as e:
            self.__logger.debug(
                "\n=== Exception Occurred under execute :%s" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def insertBuildInfo(self, ver, build, hyp_type,
                        type, file_paths, state, ts):
        try:
            self.__connect()
            build_tbl = sqlalchemy.Table(
                'build',
                self.__metaData,
                autoload=True,
                autoload_with=self.__engine)
            with self.__engine.connect() as conn:
                conn.execute(
                    build_tbl.insert(),
                    {"buildno": str(build),
                     "version": str(ver),
                     "hyptype": str(hyp_type),
                     "type": type,
                     "file_paths": file_paths,
                     "state": state,
                     "updated_date": ts})
                cur = conn.execute("select @@identity")
                rows = cur.fetchall()
                if rows:
                    return rows[0]
            return Codes.FAILED
        except Exception as e:
            print "\n===Here===", str(e)
            self.__logger.debug(
                "\n === Inserting Build Information Failed:%s ====" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def updateBugInfo(self, bugs):
        try:
            self.__connect()
            with self.__engine.connect() as conn:
                for bug, state in bugs:
                    conn.execute(
                        "update bugs set state = '" +
                        state +
                        "' where bugid = '" +
                        bug +
                        "'")
            return Codes.SUCCESS
        except Exception as e:
            self.__logger.debug(
                "\n === Inserting Build Information Failed:%s ====" %
                Codes.GetDetailExceptionInfo(e))

    def getJobStatus(self, jobid):
        try:
            self.__connect()
            with self.__engine.connect() as conn:
                cur = conn.execute(
                    "select state from build where id  = " +
                    str(jobid))
                rows = cur.fetchall()
                if rows:
                    return rows[0]
        except Exception as e:
            self.__logger.debug(
                "\n === Getting Job Status Failed for Job : %s :%s====" % (str(jobid), Codes.GetDetailExceptionInfo(e)))

    def updateBuildInfo(self, jobid, file_paths, status):
        try:
            self.__connect()
            with self.__engine.connect() as conn:
                cmd = "update build set file_paths='" + file_paths + "', updated_date='" + \
                    time.asctime() + "', state= '" + status + \
                    "' where jobid = " + str(jobid)
                conn.execute(cmd)
            return Codes.SUCCESS
        except Exception as e:
            self.__logger.debug(
                "\n === Inserting Build Information Failed:%s ====" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def retrieveBugsForGivenHypTypeAndVersion(self, hyp_type, version):
        try:
            self.__connect()
            rows = []
            with self.__engine.connect() as conn:
                cur = conn.execute("select testname,state,result,message, bugid, type,trace from bugs where version = '" +
                                   str(version) + "' and hyptype = '" + str(hyp_type) + "'")
                rows = cur.fetchall()
            return rows
        except Exception as e:
            self.__logger.debug(
                "==== RetrievingBugsForGivenHypTypeAndVersion Failed:%s ====" %
                Codes.GetDetailExceptionInfo(e))
            return Codes.FAILED

    def close(self):
        if self.__connHandle:
            self.__connHandle.close()

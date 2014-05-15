import sys
from marvinBugLogger import TcSearchLocalDb, Codes, MarvinBugLogger, MiscHandler

version = str(sys.argv[1])
build = str(sys.argv[2])
hyptype = str(sys.argv[3])
type = str(sys.argv[4])
jobid = str(sys.argv[5])

obj_marvin_buglogger = MarvinBugLogger(version,build,hyptype,type,jobid)
obj_marvin_buglogger.init()




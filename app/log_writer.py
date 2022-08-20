## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import io
import os 
import time
import calendar
import sys

from command_formatter import command_formatter

class log_writer:
  
  def __init__(self):  
    pass
 
  #@public
  def replaceLogFile(self):
    print('start of replaceLogFile()')
    import config_cliprocessor
    import traceback
    traceback.print_stack()
#    ok = False
    cft = command_formatter()
    verboseLogFilePath = config_cliprocessor.inputVars.get('verboseLogFilePath')
    print('ee verboseLogFilePath is: ', verboseLogFilePath)
    verboseLogFileAndPath = verboseLogFilePath + '/log-verbose.log'
    verboseLogFileAndPath = cft.formatPathForOS(verboseLogFileAndPath)
    acmSummaryLogFileAndPath = verboseLogFilePath + '/log-acm-summary.log'
    acmSummaryLogFileAndPath = cft.formatPathForOS(acmSummaryLogFileAndPath)
    current_GMT = time.gmtime()
    ts = calendar.timegm(current_GMT)
    timeString = "Time Stamp at start of log is: " + str(ts)
    if os.path.exists(verboseLogFileAndPath):
      print('1 x')
      first_line = ''
      with open(verboseLogFileAndPath) as f:
        first_line = f.readline()
      if "[ acm ] Time Stamp at start of log is:" in first_line:
        print('2 x')
#        ok = True
        time_stamp_string = first_line.replace("[ acm ] Time Stamp at start of log is:", "")
        time_stamp_string = time_stamp_string.replace(" ", "")
        verboseLogFileAndPath_part = verboseLogFileAndPath.replace(".log", "")
        backupVerboseLogFileAndPath = verboseLogFileAndPath_part + "-" + time_stamp_string + ".log"
        backupVerboseLogFileAndPath = "".join(backupVerboseLogFileAndPath.splitlines())
        if os.path.exists(backupVerboseLogFileAndPath):
          backupVerboseLogFileAndPath = backupVerboseLogFileAndPath.replace('.log','')+'.a.log'
        #consider making this recursive N times if necessary
        if os.path.exists(backupVerboseLogFileAndPath):
          backupVerboseLogFileAndPath = backupVerboseLogFileAndPath.replace('.log','')+'.a.log'
        #consider making this recursive N times if necessary
        if os.path.exists(backupVerboseLogFileAndPath):
          backupVerboseLogFileAndPath = backupVerboseLogFileAndPath.replace('.log','')+'.a.log'
        #consider making this recursive N times if necessary
        if os.path.exists(backupVerboseLogFileAndPath):
          backupVerboseLogFileAndPath = backupVerboseLogFileAndPath.replace('.log','')+'.a.log'
        os.rename(verboseLogFileAndPath, backupVerboseLogFileAndPath)
      else:
#///
        if os.path.isfile(verboseLogFileAndPath):
          time_stamp_string = ''
          with open(verboseLogFileAndPath,'r') as fin:
            lines = fin.readlines()
          for line in lines:
            # do something
            if "[ acm ] Time Stamp at start of log is:" in line:
              print('99 x')
              time_stamp_string = line.replace("[ acm ] Time Stamp at start of log is:", "")
              time_stamp_string = time_stamp_string.replace(" ", "")
              quit('---888rrr!!!')
          verboseLogFileAndPath_part = verboseLogFileAndPath.replace(".log", "")
          if len(time_stamp_string) == 0:
            backupVerboseLogFileAndPath = verboseLogFileAndPath_part + "-" + str(ts) + "TIMEERROR.log"
            backupVerboseLogFileAndPath = "".join(backupVerboseLogFileAndPath.splitlines())
          else:
            backupVerboseLogFileAndPath = verboseLogFileAndPath_part + "-" + time_stamp_string + ".log"
            backupVerboseLogFileAndPath = "".join(backupVerboseLogFileAndPath.splitlines())
          if os.path.exists(backupVerboseLogFileAndPath):
            backupVerboseLogFileAndPath = backupVerboseLogFileAndPath.replace('.log','')+'.a.log'
          #consider making this recursive N times if necessary
          if os.path.exists(backupVerboseLogFileAndPath):
            backupVerboseLogFileAndPath = backupVerboseLogFileAndPath.replace('.log','')+'.a.log'
          #consider making this recursive N times if necessary
          if os.path.exists(backupVerboseLogFileAndPath):
            backupVerboseLogFileAndPath = backupVerboseLogFileAndPath.replace('.log','')+'.a.log'
          #consider making this recursive N times if necessary
          if os.path.exists(backupVerboseLogFileAndPath):
            backupVerboseLogFileAndPath = backupVerboseLogFileAndPath.replace('.log','')+'.a.log'
          os.rename(verboseLogFileAndPath, backupVerboseLogFileAndPath)

#///


    if os.path.exists(acmSummaryLogFileAndPath):
      print('3 x')
      first_line = ''
      with open(acmSummaryLogFileAndPath) as f:
        first_line = f.readline()
      if "[ acm ] Time Stamp at start of log is:" in first_line:
        print('4 x')
        time_stamp_string = first_line.replace("[ acm ] Time Stamp at start of log is:", "")
        time_stamp_string = time_stamp_string.replace(" ", "")
        acmSummaryLogFileAndPath_part = acmSummaryLogFileAndPath.replace(".log", "")
        backupAcmSummaryLogFileAndPath = acmSummaryLogFileAndPath_part + "-" + time_stamp_string + ".log"
        backupAcmSummaryLogFileAndPath = "".join(backupAcmSummaryLogFileAndPath.splitlines())
        if os.path.exists(backupAcmSummaryLogFileAndPath):
          backupAcmSummaryLogFileAndPath = backupAcmSummaryLogFileAndPath.replace('.log','')+'.a.log'
        #consider making this recursive N times if necessary
        if os.path.exists(backupAcmSummaryLogFileAndPath):
          backupAcmSummaryLogFileAndPath = backupAcmSummaryLogFileAndPath.replace('.log','')+'.a.log'
        #consider making this recursive N times if necessary
        if os.path.exists(backupAcmSummaryLogFileAndPath):
          backupAcmSummaryLogFileAndPath = backupAcmSummaryLogFileAndPath.replace('.log','')+'.a.log'
        #consider making this recursive N times if necessary
        if os.path.exists(backupAcmSummaryLogFileAndPath):
          backupAcmSummaryLogFileAndPath = backupAcmSummaryLogFileAndPath.replace('.log','')+'.a.log'
        os.rename(acmSummaryLogFileAndPath, backupAcmSummaryLogFileAndPath)
    if not os.path.exists(verboseLogFilePath):
      print('5 x')
      os.makedirs(verboseLogFilePath)
    self.writeMetaLog("acm", timeString)
    print('end of replaceLogFile()')
#    if not ok:
#      print(ok)
#      quit('lkjhgfdsa')

  #@public
  def writeLogVerbose(self, tool, line):  
    import config_cliprocessor
    cft = command_formatter()
    verboseLogFilePath = config_cliprocessor.inputVars.get('verboseLogFilePath')
    verboseLogFileAndPath = verboseLogFilePath + '/log-verbose.log'
    verboseLogFileAndPath = cft.formatPathForOS(verboseLogFileAndPath)
    outputLine = "[ " + str(tool) + " ] " + str(line)
    with open(verboseLogFileAndPath, "a", encoding="utf-8") as f:
      f.write(outputLine + '\n')
    try:
      print(outputLine)
      if (tool == 'terraform') and ('Error: expected ' in line):
        sys.exit(1)
    except UnicodeEncodeError as e:
      print(outputLine.encode('utf-8'))
      print("The preceding line is returned here as a byte array because it threw a UnicodeEncodeError which was handled by encoding its as utf-8, which returns a byte array.  ")

  #@public
  def writeMetaLog(self, tool, line):
    import config_cliprocessor
    cft = command_formatter()
    verboseLogFilePath = config_cliprocessor.inputVars.get('verboseLogFilePath')
    ##Add work item to set up logic for log file time stamps in names, etc.
    verboseLogFileAndPath = verboseLogFilePath + '/log-verbose.log'
    verboseLogFileAndPath = cft.formatPathForOS(verboseLogFileAndPath)
    acmSummaryLogFileAndPath = verboseLogFilePath + '/log-acm-summary.log'
    acmSummaryLogFileAndPath = cft.formatPathForOS(acmSummaryLogFileAndPath)
    outputLine = "[ " + str(tool) + " ] " + str(line)
    with io.open(verboseLogFileAndPath, "a", encoding="utf-8") as f:
      f.write(outputLine + '\n')
    with io.open(acmSummaryLogFileAndPath, "a", encoding="utf-8") as f:
      f.write(outputLine + '\n')
    try:
      print(outputLine)
    except UnicodeEncodeError as e:
      print(outputLine.encode('utf-8'))
      print("The preceding line is returned here as a byte array because it threw a UnicodeEncodeError which was handled by encoding its as utf-8, which returns a byte array.  ")

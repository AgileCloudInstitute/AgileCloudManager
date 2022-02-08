## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import io
import os 
import time
import calendar

import config_cliprocessor
import changes_taxonomy
  
def replaceLogFile():
  verboseLogFilePath = config_cliprocessor.inputVars.get('verboseLogFilePath')
  verboseLogFileAndPath = verboseLogFilePath + 'log-verbose.log'
  acmSummaryLogFileAndPath = verboseLogFilePath + 'log-acm-summary.log'
  current_GMT = time.gmtime()
  ts = calendar.timegm(current_GMT)
  timeString = "Time Stamp at start of log is: " + str(ts)
  if os.path.exists(verboseLogFileAndPath):
    first_line = ''
    with open(verboseLogFileAndPath) as f:
      first_line = f.readline()
    if "[ acm ] Time Stamp at start of log is:" in first_line:
      time_stamp_string = first_line.replace("[ acm ] Time Stamp at start of log is:", "")
      time_stamp_string = time_stamp_string.replace(" ", "")
      verboseLogFileAndPath_part = verboseLogFileAndPath.replace(".log", "")
      backupVerboseLogFileAndPath = verboseLogFileAndPath_part + "-" + time_stamp_string + ".log"
      backupVerboseLogFileAndPath = "".join(backupVerboseLogFileAndPath.splitlines())
      os.rename(verboseLogFileAndPath, backupVerboseLogFileAndPath)
  if os.path.exists(acmSummaryLogFileAndPath):
    first_line = ''
    with open(acmSummaryLogFileAndPath) as f:
      first_line = f.readline()
    if "[ acm ] Time Stamp at start of log is:" in first_line:
      time_stamp_string = first_line.replace("[ acm ] Time Stamp at start of log is:", "")
      time_stamp_string = time_stamp_string.replace(" ", "")
      acmSummaryLogFileAndPath_part = acmSummaryLogFileAndPath.replace(".log", "")
      backupAcmSummaryLogFileAndPath = acmSummaryLogFileAndPath_part + "-" + time_stamp_string + ".log"
      backupAcmSummaryLogFileAndPath = "".join(backupAcmSummaryLogFileAndPath.splitlines())
      os.rename(acmSummaryLogFileAndPath, backupAcmSummaryLogFileAndPath)
  writeLogVerbose("acm", timeString)
  writeMetaLog("acm", timeString)
  
def writeLogVerbose(tool, line):
  verboseLogFilePath = config_cliprocessor.inputVars.get('verboseLogFilePath')
  verboseLogFileAndPath = verboseLogFilePath + 'log-verbose.log'
  acmSummaryLogFileAndPath = verboseLogFilePath + 'log-acm-summary.log'
  outputLine = "[ " + str(tool) + " ] " + str(line)
##1.21.22 commenting out the next 2 lines.
#  if "changeTaxonomy is:" in outputLine:
#    changes_taxonomy.storeChangeTaxonomy(outputLine)
  with io.open(verboseLogFileAndPath, "a", encoding="utf-8") as f:
    f.write(outputLine + '\n')
  try:
    print(outputLine)
  except UnicodeEncodeError as e:
    print(outputLine.encode('utf-8'))
    print("The preceding line is returned here as a byte array because it threw a UnicodeEncodeError which was handled by encoding its as utf-8, which returns a byte array.  ")

def writeMetaLog(tool, line):
  verboseLogFilePath = config_cliprocessor.inputVars.get('verboseLogFilePath')
  ##Add work item to set up logic for log file time stamps in names, etc.
  verboseLogFileAndPath = verboseLogFilePath + 'log-verbose.log'
  acmSummaryLogFileAndPath = verboseLogFilePath + 'log-acm-summary.log'
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

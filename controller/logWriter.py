## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import io

def writeLogVerbose(line, **inputVars):
  verboseLogFilePath = inputVars.get('verboseLogFilePath')
  ##Ad work item to set up logic for log file time stamps in names, etc.
  verboseLogFileAndPath = verboseLogFilePath + 'log-verbose-timestamp.log'

  with io.open(verboseLogFileAndPath, "a", encoding="utf-8") as f:
    f.write(line + '\n')

## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import subprocess
import re
import sys

from command_formatter import command_formatter
from log_writer import log_writer

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

class controller_custom:

  outputVariables = []

  def __init__(self):  
    pass

  #@public
  def runCustomController(self, operation, systemConfig, controllerPath, controllerCommand, mappedVariables, serviceType, instance):
    import config_cliprocessor
    cf = command_formatter()
    lw = log_writer()
    cmdPrefix = ""
    if ("$location" in controllerCommand) and (not controllerCommand.startswith("$location")):
      cmdParts = controllerCommand.split("$location")
      cmdPrefix = controllerCommand.split("$location")[0]
      print('cmdParts is: ', str(cmdParts))
      print('cmdPrefix is: ', str(cmdPrefix))
    print('operation is: ', operation)
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    fullControllerPath = userCallingDir + controllerPath #+"\""
    fullControllerPath = cf.formatPathForOS(fullControllerPath)
    from command_builder import command_builder
    cbldr = command_builder()
    outputDict = {'calledFromCustomController':True}
    varsFragment = cbldr.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, 'customController', outputDict)
    controllerCommand = cmdPrefix+fullControllerPath+' '+operation+' '+varsFragment
    logString = 'controllerCommand is: '+ controllerCommand
    lw.writeLogVerbose('shell', logString)
    self.runShellCommand(controllerCommand)


  #@public
  def runShellCommand(self, commandToRun):
    lw = log_writer()
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    captureOutputs = False
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        if 'ERROR in customController.' in decodedline:
          lw.writeLogVerbose("shell", decodedline)
          sys.exit(1)
        if decodedline.startswith('Finished output variables.'):
          captureOutputs = False
        if captureOutputs:
          lineParts = decodedline.split(' = ')
          lineDict = {'varName':lineParts[0].replace(' ', ''), 'varValue':lineParts[1].replace(' ','')}
          self.outputVariables.append(lineDict)
#          print('self.outputVariables is: ', self.outputVariables)
        if decodedline.startswith('Output variables:'):
          captureOutputs = True
        lw.writeLogVerbose("shell", decodedline)
      else:
        break


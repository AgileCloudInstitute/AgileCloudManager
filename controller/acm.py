## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import cliInputProcessor as cliproc
import crudOperations as crudops 
import configReader
import setup
import sys

inputArgs=sys.argv

def printProperties(input_vars):
  print("cliproc.domain is: ", cliproc.domain)
  print("cliproc.command is: ", cliproc.command)


def runInfraCommands(inputVariables):
  if cliproc.domain == 'setup':
    if cliproc.command == 'on':
      setup.runSetup(**inputVariables)
    elif cliproc.command == 'off':
      setup.undoSetup(**inputVariables)

  elif cliproc.domain == 'foundation':
    if cliproc.command == 'on':
      crudops.onFoundation(cliproc.command, **inputVariables)
    elif cliproc.command == 'off':
      crudops.offFoundation(**inputVariables)

  elif cliproc.domain == 'system':
    if cliproc.command == 'on':
      crudops.onSystem(cliproc.command, **inputVariables)
    elif cliproc.command == 'off':
      crudops.offSystem(**inputVariables)

  elif cliproc.domain == 'project':
    if cliproc.command == 'on':
      crudops.onProject(cliproc.command, **inputVariables)
    elif cliproc.command == 'off':
      crudops.offProject(**inputVariables)

  elif cliproc.domain == 'pipeline':
    if cliproc.command == 'on':
      crudops.onPipeline(cliproc.command, **inputVariables)
    elif cliproc.command == 'off':
      crudops.offPipeline(**inputVariables)

  elif cliproc.domain == 'tfbackend':
    if cliproc.command == 'on':
      crudops.onTfBackend(**inputVariables)
    elif cliproc.command == 'off':
      crudops.offTfBackend(**inputVariables)

##############################################################################
### Create Infrastructure By Calling The Functions
##############################################################################
inputVars = cliproc.processInputArgs(inputArgs)

#printProperties(inputVars)

runInfraCommands(inputVars)

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

  if cliproc.domain == 'admin':
    typeName = 'admin'
    yamlInfraConfigFileAndPath = inputVariables.get('yamlInfraConfigFileAndPath')
    foundationInstanceName = configReader.getFoundationInstanceName(yamlInfraConfigFileAndPath)
    adminInstanceName = configReader.getAdminInstanceName(yamlInfraConfigFileAndPath)
    instanceNames = [adminInstanceName]

    if cliproc.command == 'on':
      operation = 'on'
      crudops.terraformCrudOperation(operation, 'none', typeName, None, None, instanceNames, **inputVariables)

    elif cliproc.command == 'off':
      operation = 'off'
      crudops.terraformCrudOperation(operation, 'none', typeName, None, None, instanceNames, **inputVariables)

  if cliproc.domain == 'foundation':

    if cliproc.command == 'on':
      crudops.onFoundation(cliproc.command, **inputVariables)

    elif cliproc.command == 'off':
      crudops.offFoundation(**inputVariables)

  if cliproc.domain == 'system':

    if cliproc.command == 'on':
      crudops.onSystem(cliproc.command, **inputVariables)

    elif cliproc.command == 'off':
      crudops.offSystem(**inputVariables)

  if cliproc.domain == 'project':

    if cliproc.command == 'on':
      crudops.onProject(cliproc.command, **inputVariables)

    elif cliproc.command == 'off':
      crudops.offProject(**inputVariables)

  if cliproc.domain == 'pipeline':

    if cliproc.command == 'on':
      crudops.onPipeline(cliproc.command, **inputVariables)

    elif cliproc.command == 'off':
      crudops.offPipeline(**inputVariables)

##############################################################################
### Create Infrastructure By Calling The Functions
##############################################################################
inputVars = cliproc.processInputArgs(inputArgs)

#printProperties(inputVars)

runInfraCommands(inputVars)

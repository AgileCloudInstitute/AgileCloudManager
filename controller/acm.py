## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import changes_manifest
import config_cliprocessor as cliproc
import config_fileprocessor
import workflow_platform
import workflow_system
import setup
import logWriter

import sys
#import os

inputArgs=sys.argv
  
def runInfraCommands():
#  userCallingDir = os.path.abspath(".")
  if cliproc.domain == 'setup':
    if cliproc.command == 'on':
      setup.runSetup()
    elif cliproc.command == 'off':
      setup.undoSetup()
#  if cliproc.domain == 'configure':
##    quit('BREAKPOINT to debug configure.')
#    if cliproc.command == 'on':
#      setup.runConfigure()
#    elif cliproc.command == 'off':
#      setup.undoConfigure()

  #Figure out where to put the first logging command.  Leaving it here for now because we want to first create the location for the logs before writing to that location.
  if (cliproc.domain == 'platform') or (cliproc.domain == 'foundation') or (cliproc.domain == 'services'):
    logWriter.replaceLogFile()

  if cliproc.domain == 'platform':
    if cliproc.command == 'on':
      workflow_platform.onPlatform(cliproc.command)
    elif cliproc.command == 'off':
      workflow_platform.offPlatform()

  elif cliproc.domain == 'foundation':
    keyDir = cliproc.inputVars.get('keysDir')
    yamlInfraConfigFileAndPath = cliproc.inputVars.get('yamlInfraConfigFileAndPath')
    systemInstanceName = config_fileprocessor.getFirstLevelValue(yamlInfraConfigFileAndPath, "name")
    changes_manifest.initializeChangesManagementDataStructures('foundation', "on")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(changes_manifest.changesManifest)) + " changes. "
    logWriter.writeLogVerbose("acm", logString)
    if cliproc.command == 'on':
      changes_manifest.updateStartOfPlatformRun('foundation', "In Process")
      changes_manifest.updateStartOfASystem('foundation', systemInstanceName, "In Process")
      changes_manifest.updateStartOfAFoundation('foundation', systemInstanceName, "In Process")
      workflow_system.onFoundation(cliproc.command, systemInstanceName, keyDir, 'cli')
      changes_manifest.updateEndOfAFoundation('foundation', systemInstanceName)
      changes_manifest.updateEndOfASystem('foundation', systemInstanceName)
      changes_manifest.updateEndOfPlatformRun('foundation')
    elif cliproc.command == 'off':
      changes_manifest.updateStartOfPlatformRun('foundation', "In Process")
      changes_manifest.updateStartOfASystem('foundation', systemInstanceName, "In Process")
      changes_manifest.updateStartOfAFoundation('foundation', systemInstanceName, "In Process")
      workflow_system.offFoundation(systemInstanceName, keyDir, yamlInfraConfigFileAndPath)
      changes_manifest.updateEndOfAFoundation('foundation', systemInstanceName)
      changes_manifest.updateEndOfASystem('foundation', systemInstanceName)
      changes_manifest.updateEndOfPlatformRun('foundation')
  elif cliproc.domain == 'services':
    keyDir = cliproc.inputVars.get('keysDir')
    yamlInfraConfigFileAndPath = cliproc.inputVars.get('yamlInfraConfigFileAndPath')
    systemInstanceName = config_fileprocessor.getFirstLevelValue(yamlInfraConfigFileAndPath, "name")
    changes_manifest.initializeChangesManagementDataStructures('services', "on")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(changes_manifest.changesManifest)) + " changes. "
    logWriter.writeLogVerbose("acm", logString)
    if cliproc.command == 'on':
      changes_manifest.updateStartOfPlatformRun('services', "In Process")
      changes_manifest.updateStartOfASystem('services', systemInstanceName, "In Process")
      changes_manifest.updateStartOfAServicesSection('services', systemInstanceName)
      workflow_system.onServices(cliproc.command, 'services', systemInstanceName, keyDir, yamlInfraConfigFileAndPath)
      changes_manifest.updateEndOfAServicesSection('services', systemInstanceName)
      changes_manifest.updateEndOfASystem('services', systemInstanceName)
      changes_manifest.updateEndOfPlatformRun('services')
    elif cliproc.command == 'off':
      changes_manifest.updateStartOfPlatformRun('services', "In Process")
      changes_manifest.updateStartOfASystem('services', systemInstanceName, "In Process")
      changes_manifest.updateStartOfAServicesSection('services', systemInstanceName)
      workflow_system.offServices('services', systemInstanceName, keyDir, None, yamlInfraConfigFileAndPath)
      changes_manifest.updateEndOfAServicesSection('services', systemInstanceName)
      changes_manifest.updateEndOfASystem('services', systemInstanceName)
      changes_manifest.updateEndOfPlatformRun('services')
  sys.exit(0)

##############################################################################
### Deploy Platform By Calling The Functions
##############################################################################

cliproc.processInputArgs(inputArgs)
runInfraCommands()

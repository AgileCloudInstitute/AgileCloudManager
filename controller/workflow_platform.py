## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import sys

import config_fileprocessor
import workflow_system
import logWriter
import changes_manifest
import config_cliprocessor
import command_builder
import changes_taxonomy

def onPlatform(command):
  test = config_cliprocessor.inputVars.get("test")
  typeOfTest = config_cliprocessor.inputVars.get("testType")

  yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlPlatformConfigFileAndPath')
  systemInstanceNames = config_fileprocessor.getInstanceNames(yamlPlatformConfigFileAndPath, 'systems')

  changes_manifest.initializeChangesManagementDataStructures('platform', command)

  logString = "This run of the Agile Cloud Manager will complete " + str(len(changes_manifest.changesManifest)) + " changes. "
  logWriter.writeLogVerbose("acm", logString)
#  logString = "The " + str(len(changes_manifest.changesManifest)) + " changes that will be made in this run are itemized in the changesManifest as follows: "
#  logWriter.writeLogVerbose("acm", logString)
#  for change in changes_manifest.changesManifest:
#    logString = str(change)
#    logWriter.writeLogVerbose("acm", logString)
  changes_manifest.updateStartOfPlatformRun('platform', "In Process")
  for systemInstanceName in systemInstanceNames:
    infraConfigFile = config_fileprocessor.getPropertyFromFirstLevelList(yamlPlatformConfigFileAndPath, 'systems', systemInstanceName, 'infraConfigFile')
    keyDir = config_fileprocessor.getKeyDir(yamlPlatformConfigFileAndPath, 'systems', systemInstanceName)
#    print('keyDir is: ', keyDir)
#    quit('dd')
    if infraConfigFile == "default":
      yaml_infra_config_file_and_path = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    else:
      yaml_infra_config_file_and_path = config_cliprocessor.inputVars.get('acmConfigPath')+command_builder.getSlashForOS() + infraConfigFile
    changes_manifest.updateStartOfASystem('platform', systemInstanceName, "In Process")
    if config_fileprocessor.checkTopLevelType(yaml_infra_config_file_and_path, "networkFoundation"):
      changes_manifest.updateStartOfAFoundation('platform', systemInstanceName, "In Process")
      print('...infraConfigFile is: ', infraConfigFile)
#      quit("j")
      workflow_system.onFoundation("on", systemInstanceName,keyDir, 'platform', infraConfigFile)
      changes_manifest.updateEndOfAFoundation('platform', systemInstanceName)
    else:
      logString = "WARNING: There is NOT any networkFoundation block in " + yaml_infra_config_file_and_path + " .  The program is continuing in case you are launching a SaaS that does not need a Foundation.  If your configuration requires a networkFoundation, then a downstream error will occur unless you add a networkFoundation block. "
      logWriter.writeLogVerbose("acm", logString)
    logString = "------------------ DONE WITH onFoundation() -------------------"
    logWriter.writeLogVerbose("acm", logString)
    changes_manifest.updateStartOfAServicesSection('platform', systemInstanceName)
    workflow_system.onServices(command, 'platform', systemInstanceName, keyDir, yaml_infra_config_file_and_path)
    changes_manifest.updateEndOfAServicesSection('platform', systemInstanceName)
    changes_manifest.updateEndOfASystem('platform', systemInstanceName)
    if (test==True) and (typeOfTest=="workflow"):
      print("stub test q stuff goes here.")
    logString = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    logWriter.writeLogVerbose("acm", logString)
    logWriter.writeLogVerbose("acm", logString)
    logWriter.writeLogVerbose("acm", logString)
    logString = "+++++++++++++++ DONE WITH " + systemInstanceName + " SYSTEM. +++++++++++"
    logWriter.writeLogVerbose("acm", logString)
    logString = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    logWriter.writeLogVerbose("acm", logString)
    logWriter.writeLogVerbose("acm", logString)
    logWriter.writeLogVerbose("acm", logString)
  changes_manifest.updateEndOfPlatformRun('platform')


def offPlatform():
#++
  test = config_cliprocessor.inputVars.get("test")
  typeOfTest = config_cliprocessor.inputVars.get("testType")
  yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlPlatformConfigFileAndPath')
  systemInstanceNames = config_fileprocessor.getInstanceNames(yamlPlatformConfigFileAndPath, 'systems')
  changes_manifest.initializeChangesManagementDataStructures('platform', "off")
  logString = "This run of the Agile Cloud Manager will complete " + str(len(changes_manifest.changesManifest)) + " changes. "
  logWriter.writeLogVerbose("acm", logString)
#  logString = "The " + str(len(changes_manifest.changesManifest)) + " changes that will be made in this run are itemized in the changesManifest as follows: "
#  logWriter.writeLogVerbose("acm", logString)
#  for change in changes_manifest.changesManifest:
#    logString = str(change)
#    logWriter.writeLogVerbose("acm", logString)
  changes_manifest.updateStartOfPlatformRun('platform', "In Process")
  print('len(systemInstanceNames) is: ', len(systemInstanceNames))
#  quit('d')
  for systemInstanceName in reversed(systemInstanceNames):
    useTheForce = config_fileprocessor.getForce(yamlPlatformConfigFileAndPath, 'systems', systemInstanceName)
    print(useTheForce)
#    quit('koko')
    infraConfigFile = config_fileprocessor.getPropertyFromFirstLevelList(yamlPlatformConfigFileAndPath, 'systems', systemInstanceName, 'infraConfigFile')
    keyDir = config_fileprocessor.getKeyDir(yamlPlatformConfigFileAndPath, 'systems', systemInstanceName)
    if infraConfigFile == "default":
      yaml_infra_config_file_and_path = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    else:
      yaml_infra_config_file_and_path = config_cliprocessor.inputVars.get('acmConfigPath') +command_builder.getSlashForOS()+ infraConfigFile
#    quit('koko 2')
    changes_manifest.updateStartOfASystem('platform', systemInstanceName, "In Process")
    hasFoundation = config_fileprocessor.checkTopLevelType(yaml_infra_config_file_and_path, "networkFoundation")
    print(useTheForce, ' : ', hasFoundation)
#    quit('vvv')
    if (useTheForce == True) and (hasFoundation):
      changes_manifest.updateStartOfSkipServicesSection()
      changes_manifest.updateStartOfAServicesSection('platform', systemInstanceName)
      print("test and typeOfTest are: ", test, " ", typeOfTest)
      workflow_system.skipServices('platform', systemInstanceName, keyDir, yaml_infra_config_file_and_path)
      changes_manifest.updateEndOfAServicesSection('platform', systemInstanceName)
      changes_manifest.updateEndOfSkipServicesSection()
    else:
      changes_manifest.updateStartOfAServicesSection('platform', systemInstanceName)
#      quit('before offServices() ')
      workflow_system.offServices('platform', systemInstanceName, keyDir, yamlPlatformConfigFileAndPath, yaml_infra_config_file_and_path)
#      quit('3!')
      changes_manifest.updateEndOfAServicesSection('platform', systemInstanceName)
      logString = "------------------ DONE WITH offServices() -------------------"
      logWriter.writeLogVerbose("acm", logString)
    if config_fileprocessor.checkTopLevelType(yaml_infra_config_file_and_path, "networkFoundation"):
      changes_manifest.updateStartOfAFoundation('platform', systemInstanceName, "In Process")
      if (test==True) and (typeOfTest=="workflow"):
        pass
      else:
        workflow_system.offFoundation(systemInstanceName, keyDir, yaml_infra_config_file_and_path)
      changes_manifest.updateEndOfAFoundation('platform', systemInstanceName)
    else:
      logString = "WARNING: There is NOT any networkFoundation block in " + yaml_infra_config_file_and_path + " .  The program is continuing in case you are launching a SaaS that does not need a Foundation.  If your configuration requires a networkFoundation, then a downstream error will occur unless you add a networkFoundation block. "
      logWriter.writeLogVerbose("acm", logString)
      if useTheForce == True:
#..
        hasProjects = workflow_system.checkDestroyType('projects', yaml_infra_config_file_and_path)
        hasReleaseDefs = workflow_system.checkDestroyType('releaseDefinitions', yaml_infra_config_file_and_path)
        print(hasProjects)
        print(hasReleaseDefs)
        print('hasFoundation is: ', hasFoundation)
#        if not hasFoundation:
#          print('006')
#        quit('got it!')
#..
        logString = "WARNING: YOU MUST VALIDATE WHAT IF ANYTHING HAPPENED with " + systemInstanceName + " because the --force flag works by deleting a foundation which will only delete system contents if all the system contents are bundled within the foundation's child objects by the cloud provider. Since your configuration does not include a foundation, the only things that happened might have been special cases defined in the documentation.  In order to make best use of the --force flag, you must write your configuration properly and validate your results in lower environments. "
        logWriter.writeLogVerbose("acm", logString)
    logString = "------------------ DONE WITH offFoundation() -------------------"
    logWriter.writeLogVerbose("acm", logString)
    changes_manifest.updateEndOfASystem('platform', systemInstanceName)
    if (test==True) and (typeOfTest=="workflow"):
      print("stub test q stuff goes here.")
    logString = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    logWriter.writeLogVerbose("acm", logString)
    logWriter.writeLogVerbose("acm", logString)
    logWriter.writeLogVerbose("acm", logString)
    logString = "+++++++++++++++ DONE WITH " + systemInstanceName + " SYSTEM. +++++++++++"
    logWriter.writeLogVerbose("acm", logString)
    logString = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    logWriter.writeLogVerbose("acm", logString)
    logWriter.writeLogVerbose("acm", logString)
    logWriter.writeLogVerbose("acm", logString)
  changes_manifest.updateEndOfPlatformRun('platform')

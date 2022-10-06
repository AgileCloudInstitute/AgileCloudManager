## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import os
import sys
from pathlib import Path 
import platform

from command_formatter import command_formatter

#The following variables will need to be returned as properties.
domain = ''
command = ''
keysDir = ''
sourceRepo = ''
repoBranch = ''
systemName = ''
serviceType = ''
serviceInstance = ''
test = False
testType = ''
inputVars = {}

def getAcmUserHome():
    if platform.system() == 'Windows':
      acmUserHome = os.path.expanduser("~")+'/acm/'
    elif platform.system() == 'Linux':
      acmUserHome = '/usr/acm/'

    if not os.path.exists(acmUserHome):
      os.makedirs(acmUserHome, exist_ok=True) 
    return acmUserHome

#The following function will set all the values for the returned properties
def processInputArgs(inputArgs):
    global domain
    global command
    global keysDir
    global sourceRepo
    global repoBranch
    global testType
    global test
    global systemName
    global serviceType
    global serviceInstance
    global inputVars
    cmdfrmtr = command_formatter()
    sourceKeys = str(Path.home())+cmdfrmtr.getSlashForOS()+'acmconfig'
    userCallingDir = str(os.path.abspath("."))+'\\'
    userCallingDir = cmdfrmtr.formatPathForOS(userCallingDir)
    path = Path(userCallingDir)
    app_parent_path = str(path.parent)+'\\'
    app_parent_path = cmdfrmtr.formatPathForOS(app_parent_path)
    #Get acmAdmin path
    acmAdmin = userCallingDir + cmdfrmtr.getSlashForOS() + 'acmAdmin'
    acmAdmin = cmdfrmtr.formatPathForOS(acmAdmin)
    acmConfig = userCallingDir + cmdfrmtr.getSlashForOS() + 'acmConfig'
    acmConfig = cmdfrmtr.formatPathForOS(acmConfig)

    acmUserHome = getAcmUserHome()

    dirOfYamlKeys = acmUserHome + '\\keys\\starter\\'
    dirOfYamlKeys = cmdfrmtr.formatPathForOS(dirOfYamlKeys)
    dirOfOutput = acmUserHome + '\\keys\\' 
    dirOfOutput = cmdfrmtr.formatPathForOS(dirOfOutput)
    varsPath = acmAdmin + cmdfrmtr.getSlashForOS() + 'vars'

    dynamicVarsPath = acmAdmin+'\\dynamicVars\\'
    dynamicVarsPath = cmdfrmtr.formatPathForOS(dynamicVarsPath)
    dirOfReleaseDefJsonParts = userCallingDir + "\\azure-building-blocks\\release-definitions\\json-fragments\\"
    dirOfReleaseDefJsonParts = cmdfrmtr.formatPathForOS(dirOfReleaseDefJsonParts)
    dirOfReleaseDefYaml = userCallingDir + "\\azure-building-blocks\\release-definitions\\yaml-definition-files\\"
    dirOfReleaseDefYaml = cmdfrmtr.formatPathForOS(dirOfReleaseDefYaml)
    yamlInfraConfigFileAndPath = ''
    keySource = 'keyFile'
    pub = 'invalid'
    sec = 'invalid' 
    #These next two /vars/vars/.. are temporary until we further revise the directory structure
    tfvarsFileAndPath = varsPath+"\\keys.tfvars"
    tfvarsFileAndPath = cmdfrmtr.formatPathForOS(tfvarsFileAndPath)
    tfBackendFileAndPath = varsPath+cmdfrmtr.getSlashForOS()+"backend.tfvars"
    tfBackendFileAndPath = cmdfrmtr.formatPathForOS(tfBackendFileAndPath)
    #Get logsPath
    if platform.system() == 'Windows':
      verboseLogFilePath = acmUserHome + cmdfrmtr.getSlashForOS() + 'logs'
      verboseLogFilePath = cmdfrmtr.formatPathForOS(verboseLogFilePath)
    elif platform.system() == 'Linux':
      verboseLogFilePath = '/var/log/acm/'
    ## Get directory structure
    #Get binariesPath
    if platform.system() == 'Windows':
      dependenciesBinariesPath = acmAdmin + cmdfrmtr.getSlashForOS() + 'binaries' + cmdfrmtr.getSlashForOS()
      dependenciesBinariesPath = cmdfrmtr.formatPathForOS(dependenciesBinariesPath)
    elif platform.system() == 'Linux':
      dependenciesBinariesPath = '/opt/acm/'
    dependenciesPath = app_parent_path + "config-outside-acm-path\\dependencies\\"
    dependenciesPath = cmdfrmtr.formatPathForOS(dependenciesPath)
    relativePathToInstances = "\\calls-to-modules\\instances\\"
    relativePathToInstances = cmdfrmtr.formatPathForOS(relativePathToInstances)
    if ('unittest' in inputArgs[0]):
      domain = 'unittest'
    elif ('unittest' not in inputArgs[0]):
      #First process the domain and the command
      if len(inputArgs) > 1:
        domain = inputArgs[1]
        command = inputArgs[2]
        if (domain != 'platform') and (domain != 'foundation') and (domain != 'services') and (domain != 'setup') and (domain != 'configure') and (domain != 'serviceType') and (domain != 'serviceInstance'):
          logString = "Error: You must specify a valid value for the first parameter.  Either platform, foundation, services, serviceType, serviceInstance, setup, or configure now, but other valid values may be added in future releases.  "
          print(logString)
          sys.exit(1)
      #Second, set any values conditionally based on flags entered by the user in the command line.  Add functionality here in future releases.
      if len(inputArgs) > 2:      #loop through the cli input, validate it, and return the set properties.
        for i in inputArgs[3:]:       # i is an item from inputArgs.
          if i.count("=") == 1:
            iParts = i.split("=")
            key = iParts[0]
            val = iParts[1]
            if key == "keysDir":  
              numSingles = cmdfrmtr.countSingleSlashesInString(val)  
              for single in range(numSingles):  
                val = cmdfrmtr.addSlashToString(val)  
              keysDir = val
            elif key == "sourceRepo":
              sourceRepo = val
            elif key == "repoBranch":
              repoBranch = val
            elif key == "test":  
              testType = val
              test = True
            elif key == "systemName":
              systemName = val
            elif key == "serviceType":
              serviceType = val
            elif key == "serviceInstance":
              serviceInstance = val
          else:
            logString = "Your input contained a malformed parameter: " + i
            print(logString)
            sys.exit(1)
      #Next, make sure that systemName has been specified if domain is foundation or services.
      if (domain == "foundation") or (domain == "services"):
        if systemName == '':
          logString = "ERROR: You must specify systemName when running foundation and services commands."
          quit(logString)
      keysDir = cmdfrmtr.formatPathForOS(keysDir)
      #Third, get any values ready for export as needed.
      if keySource == "keyFile":
        yamlInfraConfigFileAndPath = acmConfig +cmdfrmtr.getSlashForOS()+ 'acm.yaml'
    #Fourth, assemble the input variables into a dict
    inputVars =  {
      'yamlInfraConfigFileAndPath': yamlInfraConfigFileAndPath,
      'app_parent_path': app_parent_path,
      'acmAdminPath': acmAdmin,
      'acmConfigPath': acmConfig,
      'varsPath': varsPath,
      'dirOfYamlKeys': dirOfYamlKeys,
      'dirOfReleaseDefJsonParts': dirOfReleaseDefJsonParts,
      'dirOfReleaseDefYaml': dirOfReleaseDefYaml,
      'dirOfOutput': dirOfOutput,
      'nameOfYamlKeys_AWS_Network_File': 'generatedKeys.yaml',
      'tfvarsFileAndPath': tfvarsFileAndPath,
      'tfBackendFileAndPath': tfBackendFileAndPath,
      'verboseLogFilePath': verboseLogFilePath,
      'dependenciesBinariesPath': dependenciesBinariesPath,
      'userCallingDir': userCallingDir,
      'dependenciesPath': dependenciesPath,
      'dynamicVarsPath': dynamicVarsPath,
      'relativePathToInstances': relativePathToInstances,
      'keySource': keySource,
      'pub': pub,
      'sec': sec,
      'keysDir': keysDir,
      'sourceKeys': sourceKeys,
      'sourceRepo': sourceRepo,
      'repoBranch': repoBranch,
      "test": test,
      "testType": testType, 
      "systemName": systemName,
      'serviceType': serviceType,
      'serviceInstance': serviceInstance,
      'tfBkndAzureParams': {     'resGroupName': 'NA' }
    }
 
## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import os
import sys
from pathlib import Path 
import platform

import command_builder

#The following variables will need to be returned as properties.
domain = ''
command = ''
keysDir = ''
sourceRepo = ''
repoBranch = ''
test = False
testType = ''
inputVars = {}

def countSingleSlashesInString(inputString):
  singles = 0
  idx = 0
  for c in inputString:
    if (idx > 0) and (idx < (len(inputString)-1)):
      charBefore = inputString[idx-1]
      charAfter = inputString[idx+1]
      if c == "\\":
        if (charBefore != "\\") and (charAfter != "\\"):
          singles = singles + 1
    idx = idx+1
  return singles

def addSlashToString(inputString):
  idx = 0
  charBefore = ''
  charAfter = ''
  for c in inputString:
    if (idx > 0) and (idx < (len(inputString)-1)):
      charBefore = inputString[idx-1]
      charAfter = inputString[idx+1]
      if c == "\\":
        if (charBefore != "\\") and (charAfter != "\\"):
          fragmentBefore = inputString[0:idx]
          fragmentAfter = inputString[idx:len(inputString)]
          inputString = fragmentBefore + "\\" + fragmentAfter
    idx = idx+1
  last2 = inputString[-2:]
  if last2 != "\\\\":
    inputString = inputString + "\\\\"
  return inputString

#The following function will set all the values for the returned properties
def processInputArgs(inputArgs):
  global domain
  global command
  global keysDir
  global sourceRepo
  global repoBranch
  global test
  global testType

#  sourceKeys = os.environ.get("ACM_SOURCE_KEYS")
#  sourceKeys = os.environ.get("USER_HOME")
  sourceKeys = str(Path.home())+command_builder.getSlashForOS()+'acmconfig'
  userCallingDir = str(os.path.abspath("."))+'\\'
  userCallingDir = command_builder.formatPathForOS(userCallingDir)
  path = Path(userCallingDir)
  app_parent_path = str(path.parent)+'\\'
  app_parent_path = command_builder.formatPathForOS(app_parent_path)
  #Get acmAdmin path
  #acmAdmin = str(app_parent_path) + command_builder.getSlashForOS() + 'acmAdmin'
  acmAdmin = userCallingDir + command_builder.getSlashForOS() + 'acmAdmin'
  acmAdmin = command_builder.formatPathForOS(acmAdmin)
  acmConfig = userCallingDir + command_builder.getSlashForOS() + 'acmConfig'
  acmConfig = command_builder.formatPathForOS(acmConfig)

  if platform.system() == 'Windows':
    acmUserHome = os.path.expanduser("~")+'/acm/'
  elif platform.system() == 'Linux':
    acmUserHome = '/usr/acm/'

  if not os.path.exists(acmUserHome):
    os.makedirs(acmUserHome, exist_ok=True) 

  dirOfYamlKeys = acmUserHome + '\\keys\\starter\\'
  dirOfYamlKeys = command_builder.formatPathForOS(dirOfYamlKeys)
  dirOfOutput = acmUserHome + '\\keys\\' 
  dirOfOutput = command_builder.formatPathForOS(dirOfOutput)
  varsPath = acmAdmin + command_builder.getSlashForOS() + 'vars'

  dynamicVarsPath = acmAdmin+'\\dynamicVars\\'
  dynamicVarsPath = command_builder.formatPathForOS(dynamicVarsPath)
#  otherVarsPath = varsPath + '\\vars\\'
#  otherVarsPath = command_builder.formatPathForOS(otherVarsPath)
  dirOfReleaseDefJsonParts = userCallingDir + "\\azure-building-blocks\\release-definitions\\json-fragments\\"
  dirOfReleaseDefJsonParts = command_builder.formatPathForOS(dirOfReleaseDefJsonParts)
  dirOfReleaseDefYaml = userCallingDir + "\\azure-building-blocks\\release-definitions\\yaml-definition-files\\"
  dirOfReleaseDefYaml = command_builder.formatPathForOS(dirOfReleaseDefYaml)
  yamlInfraConfigFileAndPath = ''
  yamlPlatformConfigFileAndPath = ''
  pathToApplicationRoot = ''
  keySource = 'keyFile'
  pub = 'invalid'
  sec = 'invalid'
  #These next two /vars/vars/.. are temporary until we further revise the directory structure
  tfvarsFileAndPath = varsPath+"\\keys.tfvars"
  tfvarsFileAndPath = command_builder.formatPathForOS(tfvarsFileAndPath)
  tfBackendFileAndPath = varsPath+command_builder.getSlashForOS()+"backend.tfvars"
  tfBackendFileAndPath = command_builder.formatPathForOS(tfBackendFileAndPath)
  #Get logsPath
  if platform.system() == 'Windows':
    verboseLogFilePath = acmAdmin + command_builder.getSlashForOS() + 'logs'
    verboseLogFilePath = command_builder.formatPathForOS(verboseLogFilePath)
  elif platform.system() == 'Linux':
    verboseLogFilePath = '/var/log/acm/'
  ## Get directory structure
  #Get binariesPath
  if platform.system() == 'Windows':
    dependenciesBinariesPath = acmAdmin + command_builder.getSlashForOS() + 'binaries' + command_builder.getSlashForOS()
    dependenciesBinariesPath = command_builder.formatPathForOS(dependenciesBinariesPath)
  elif platform.system() == 'Linux':
    dependenciesBinariesPath = '/opt/acm/'
  dependenciesPath = app_parent_path + "config-outside-acm-path\\dependencies\\"
  dependenciesPath = command_builder.formatPathForOS(dependenciesPath)
  relativePathToInstances = "\\calls-to-modules\\instances\\"
  relativePathToInstances = command_builder.formatPathForOS(relativePathToInstances)

  print("len(inputArgs) is: ", len(inputArgs))
  #First process the domain and the command
  if len(inputArgs) > 1:
    domain = inputArgs[1]
    command = inputArgs[2]
    print("domain is: ... ", domain)
    print("command is: ... ", command)
    if (domain != 'platform') and (domain != 'foundation') and (domain != 'services') and (domain != 'setup') and (domain != 'configure'):
      logString = "Error: You must specify a valid value for the first parameter.  Either platform, foundation, services, setup, or configure now, but other valid values may be added in future releases.  "
      print(logString)
      sys.exit(1)
  #Second, set any values conditionally based on flags entered by the user in the command line.  Add functionality here in future releases.
  if len(inputArgs) > 2:      #loop through the cli input, validate it, and return the set properties.
    for i in inputArgs[3:]:       # i is an item from inputArgs.
      print("i is: ", i)
      if i.count("=") == 1:
        iParts = i.split("=")
        key = iParts[0]
        val = iParts[1]
        if key == "keysDir":  
          numSingles = countSingleSlashesInString(val)  
          for single in range(numSingles):  
            val = addSlashToString(val)  
          keysDir = val  
        elif key == "sourceRepo":
          sourceRepo = val
        elif key == "repoBranch":
          repoBranch = val
        elif key == "test":  
          testType = val
          test = True
      else:
        logString = "Your input contained a malformed parameter: " + i
        print(logString)
        sys.exit(1)
  keysDir = command_builder.formatPathForOS(keysDir)
  #Third, get any values ready for export as needed.
  if keySource == "keyFile":
    yamlInfraConfigFileAndPath = acmConfig +command_builder.getSlashForOS()+ 'systemConfig.yaml'
    yamlPlatformConfigFileAndPath = acmConfig +command_builder.getSlashForOS()+ 'platformConfig.yaml'
    pathToApplicationRoot = app_parent_path + '\\terraform-aws-building-blocks\\'
    pathToApplicationRoot = command_builder.formatPathForOS(pathToApplicationRoot)

  #Fourth, assemble the input variables into a dict, which will be a global variable
  global inputVars
  inputVars =  {
    'yamlInfraConfigFileAndPath': yamlInfraConfigFileAndPath,
    'yamlPlatformConfigFileAndPath': yamlPlatformConfigFileAndPath,
    'pathToApplicationRoot': pathToApplicationRoot,
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
    'tfBkndAzureParams': {     'resGroupName': 'NA' }
  }

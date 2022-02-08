## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import os
import sys
from pathlib import Path 

import command_builder

#The following variables will need to be returned as properties.
domain = ''
command = ''
keysDir = ''
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
  global test
  global testType

  userCallingDir = str(os.path.abspath("."))+'\\'
  userCallingDir = command_builder.formatPathForOS(userCallingDir)
  path = Path(userCallingDir)
  app_parent_path = str(path.parent)+'\\'
  app_parent_path = command_builder.formatPathForOS(app_parent_path)
  dirOfYamlKeys = app_parent_path+ '\\acmAdmin\\keys\\starter\\'
  dirOfYamlKeys = command_builder.formatPathForOS(dirOfYamlKeys)
  dirOfOutput = app_parent_path+ '\\acmAdmin\\keys\\' 
  dirOfOutput = command_builder.formatPathForOS(dirOfOutput)
  dynamicVarsPath = app_parent_path + '\\acmAdmin\\dynamicVars\\'
  dynamicVarsPath = command_builder.formatPathForOS(dynamicVarsPath)
  dirOfReleaseDefJsonParts = app_parent_path + "\\azure-building-blocks\\release-definitions\\json-fragments\\"
  dirOfReleaseDefJsonParts = command_builder.formatPathForOS(dirOfReleaseDefJsonParts)
  dirOfReleaseDefYaml = app_parent_path + "\\azure-building-blocks\\release-definitions\\yaml-definition-files\\"
  dirOfReleaseDefYaml = command_builder.formatPathForOS(dirOfReleaseDefYaml)
  yamlInfraConfigFileAndPath = ''
  yamlPlatformConfigFileAndPath = ''
  pathToApplicationRoot = ''
  keySource = 'keyFile'
  pub = 'invalid'
  sec = 'invalid'

  tfvarsFileAndPath = app_parent_path+'\\acmAdmin\\vars'+"\\keys.tfvars"
  tfvarsFileAndPath = command_builder.formatPathForOS(tfvarsFileAndPath)
  tfBackendFileAndPath = app_parent_path+'\\acmAdmin\\vars'+"\\backend.tfvars"
  tfBackendFileAndPath = command_builder.formatPathForOS(tfBackendFileAndPath)
  verboseLogFilePath = app_parent_path+ '\\acmAdmin\\logs\\'
  verboseLogFilePath = command_builder.formatPathForOS(verboseLogFilePath)
  dependenciesBinariesPath = app_parent_path + '\\acmAdmin\\binaries\\'
  dependenciesBinariesPath = command_builder.formatPathForOS(dependenciesBinariesPath)
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
    yamlInfraConfigFileAndPath = userCallingDir + 'systemConfig.yaml'
    yamlPlatformConfigFileAndPath = userCallingDir + 'platformConfig.yaml'
    pathToApplicationRoot = app_parent_path + '\\terraform-aws-building-blocks\\'
    pathToApplicationRoot = command_builder.formatPathForOS(pathToApplicationRoot)

  #Fourth, assemble the input variables into a dict, which will be a global variable
  global inputVars
  inputVars =  {
    'yamlInfraConfigFileAndPath': yamlInfraConfigFileAndPath,
    'yamlPlatformConfigFileAndPath': yamlPlatformConfigFileAndPath,
    'pathToApplicationRoot': pathToApplicationRoot,
    'app_parent_path': app_parent_path,
    'dirOfYamlKeys': dirOfYamlKeys,
    'dirOfReleaseDefJsonParts': dirOfReleaseDefJsonParts,
    'dirOfReleaseDefYaml': dirOfReleaseDefYaml,
    'dirOfOutput': dirOfOutput,
    'nameOfYamlKeys_IAM_File': 'iamUserKeys.yaml',
    'nameOfYamlKeys_AWS_Network_File': 'generatedKeys.yaml',
    'nameOfYamlKeys_Azure_AD_File': 'adUserKeys.yaml',
    'nameOfYamlKeys_Azure_Network_File': 'adUserKeys.yaml',
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
    "test": test,
    "testType": testType, 
    'tfBkndAzureParams': {     'resGroupName': 'NA' }
  }

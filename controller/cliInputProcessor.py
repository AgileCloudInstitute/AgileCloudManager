## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import os

#The following variables will need to be returned as properties.
domain = ''
command = ''

#The following function will set all the values for the returned properties
def processInputArgs(inputArgs):
  global domain
  global command
  app_parent_path = os.path.dirname(os.path.realpath("..\\")) + '\\'
  configAndSecretsPath = app_parent_path+"config-outside-acm-path\\"
  dirOfYamlFile = configAndSecretsPath + "vars\\yamlInputs\\"
  dirOfYamlKeys = configAndSecretsPath + "vars\\admin\\"
  dirOfReleaseDefJsonParts = app_parent_path + "azure-building-blocks\\release-definitions\\json-fragments\\"
  dirOfReleaseDefYaml = app_parent_path + "azure-building-blocks\\release-definitions\\yaml-definition-files\\"
  yamlInfraConfigFileAndPath = ''
  pathToApplicationRoot = ''
  keySource = 'keyFile'
  pub = 'invalid'
  sec = 'invalid'
  #First process the domain and the command
  if len(inputArgs) > 2:
    domain = inputArgs[1]
    command = inputArgs[2]
    if domain == 'admin':
      print('admin! ')
      print('command is: ', command)
    elif domain == 'foundation':
      print('foundation! ')
      print('command is: ', command)
    elif domain == 'system':
      print('system')
      print('command is: ', command)
    elif domain == 'project':
      print('project')
      print('command is: ', command)
    elif domain == 'pipeline':
      print('pipeline')
      print('command is: ', command)
    elif domain == 'setup':
      print('setup')
      print('command is: ', command)
    else:  
      quit("Error: You must specify a valid value for the first parameter.  Either admin, foundation, system, or setup now, but other valid values may be added in future releases.  ")
  #Second, set any values conditionally based on flags entered by the user in the command line.  Add functionality here in future releases.
  if len(inputArgs) > 3:      #loop through the cli input, validate it, and return the set properties.
    for i in inputArgs[3:]:       # i is an item from inputArgs.
      print("arg is: ", i)
  #Third, get any values ready for export as needed.
  if keySource == "keyFile":
    yamlInfraConfigFileAndPath = dirOfYamlFile + 'infrastructureConfig.yaml'
    pathToApplicationRoot = app_parent_path + '\\terraform-aws-building-blocks\\'
  #Fourth, assemble the input variables into a dict, which will be returned
  inputVars =  {
    'yamlInfraConfigFileAndPath': yamlInfraConfigFileAndPath,
    'pathToApplicationRoot': pathToApplicationRoot,
    'app_parent_path': app_parent_path,
    'configAndSecretsPath': configAndSecretsPath, 
    'dirOfYamlFile': configAndSecretsPath + "vars\\yamlInputs\\",
    'dirOfYamlKeys': dirOfYamlKeys,
    'dirOfReleaseDefJsonParts': dirOfReleaseDefJsonParts,
    'dirOfReleaseDefYaml': dirOfReleaseDefYaml,
    'nameOfYamlKeys_IAM_File': 'iamUserKeys.yaml',
    'nameOfYamlKeys_AWS_Network_File': 'generatedKeys.yaml',
    'nameOfYamlKeys_Azure_AD_File': 'adUserKeys.yaml',
    'nameOfYamlKeys_Azure_Network_File': 'generatedAzureKeys.yaml',
    'tfvarsFileAndPath': app_parent_path+"config-outside-acm-path\\vars\\VarsForTerraform\\keys.tfvars",
    'verboseLogFilePath': app_parent_path+"config-outside-acm-path\\logs\\",
    'dependenciesBinariesPath': app_parent_path + "config-outside-acm-path\\dependencies\\binaries\\",
    'dependenciesPath': app_parent_path + "config-outside-acm-path\\dependencies\\",
    'dynamicVarsPath': configAndSecretsPath + "dynamicvars",
    'relativePathToInstances': "\\calls-to-modules\\instances\\",
    'keySource': keySource,
    'pub': pub,
    'sec': sec,
    'tfBkndAzureParams': {     'resGroupName': 'NA' }
  }  
  return inputVars

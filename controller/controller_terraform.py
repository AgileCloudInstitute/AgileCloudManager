## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import fileinput 
from distutils.dir_util import copy_tree
from pathlib import Path
import yaml
import os 
import shutil
import json
import platform
import shutil
import sys

import command_runner
import command_builder
import config_fileprocessor
import controller_azdoproject
import controller_azureadmin
import logWriter
import config_cliprocessor

tfOutputDict = {}
foundationApply = True

def terraformCrudOperation(operation, systemInstanceName, keyDir, infraConfigFileAndPath, typeParent, typeName, parentInstanceName, typeGrandChild, instanceName):
  foundationInstanceName = config_fileprocessor.getFoundationInstanceName(infraConfigFileAndPath)
  cloud = config_fileprocessor.getCloudName(infraConfigFileAndPath)
  #1. Set variable values
  templateName = config_fileprocessor.getTemplateName(infraConfigFileAndPath, typeParent, typeName, None, instanceName, None)  
  dynamicVarsPath = config_cliprocessor.inputVars.get('dynamicVarsPath')
  oldTfStateName = getBackedUpStateFileName(dynamicVarsPath, foundationInstanceName, templateName, instanceName)
  userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
  relative_path_to_instances =  config_cliprocessor.inputVars.get('relativePathToInstances')
  path_to_application_root = ''
  repoName = templateName.split('/')[0]
#  print(repoName)
#  quit(templateName)
  if templateName.count('/') == 2:
    nameParts = templateName.split("/")
    if (len(nameParts[0]) > 1) and (len(nameParts[1]) >1) and (len(nameParts[2]) > 1):
      relative_path_to_instances = nameParts[0] + '\\' + nameParts[1] + relative_path_to_instances  
      template_Name = nameParts[2]  
      path_to_application_root = userCallingDir + nameParts[0] + "\\" + nameParts[1] + "\\"
      module_config_file_and_path = userCallingDir + nameParts[0] + '\\variableMaps\\' + template_Name + '.csv'
    else:
      logString = 'ERROR: templateName is not valid. '
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
  else:  
    logString = "Template name is not valid.  Must have only one /.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  relative_path_to_instances = command_builder.formatPathForOS(relative_path_to_instances)
  path_to_application_root = command_builder.formatPathForOS(path_to_application_root)
  module_config_file_and_path = command_builder.formatPathForOS(module_config_file_and_path)
  relativePathToInstance = relative_path_to_instances + template_Name + "\\"
  destinationCallParent = convertPathForOS(userCallingDir, relativePathToInstance)
  #2. Then second instantiate call to module
  destinationCallInstance = instantiateCallToModule(cloud, operation, keyDir, infraConfigFileAndPath, foundationInstanceName, parentInstanceName, typeName, module_config_file_and_path, repoName, instanceName, template_Name, oldTfStateName)
  if os.path.exists(destinationCallInstance) and os.path.isdir(destinationCallInstance):
    #3. Then third assemble and run command
    assembleAndRunCommand(cloud, systemInstanceName, keyDir, template_Name, operation, infraConfigFileAndPath, foundationInstanceName, parentInstanceName, instanceName, destinationCallInstance, typeName, module_config_file_and_path)
    logString = "The terraform command was assembled and run.  "
    logWriter.writeLogVerbose("acm", logString)
    if command_runner.terraformResult == "Destroyed": 
      logString = "Destroy operation succeeded.  "
      logWriter.writeLogVerbose("acm", logString)
    elif command_runner.terraformResult == "Applied": 
      if (typeParent == "systems") and (typeName == "projects") and (typeGrandChild is None) and (operation != "output"):
        logString = "Terraform operation succeeded for project.  But now about to import code into the repository.  "
        logWriter.writeLogVerbose("acm", logString)
        controller_azdoproject.importCodeIntoRepo(keyDir, typeName, instanceName, infraConfigFileAndPath, cloud)
      logString = "Apply operation succeeded.  "
      logWriter.writeLogVerbose("acm", logString)
    elif operation == "output":
      logString = "terraform output operation completed.  This code does not currently check for errors, so continuing.  If you find downstream errors, remember to check the terraform output as one possible cause."
      logWriter.writeLogVerbose("acm", logString)
    else:
      #quit("BREAKPOINT 1 11/26/2021")
      logString = "Terraform operation failed.  Quitting program here so you can debug the source of the problem.  "
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
    #4. Then fourth off each instance of the calls to the modules in local agent file system
    doCleanup = setDoCleanUp(operation)
    if(doCleanup):
      logString = "Inside conditional block of things to do if operation completed: ", operation
      logWriter.writeLogVerbose("acm", logString)
      key_source = config_cliprocessor.inputVars.get('keySource')
      tfvars_file_and_path = config_cliprocessor.inputVars.get('tfvarsFileAndPath') 
      ############################################################################################################################
      if (typeName == 'admin'): 
        controller_azureadmin.cleanUp(operation, infraConfigFileAndPath, keyDir, typeName, instanceName, destinationCallInstance, cloud)
      ############################################################################################################################
      print('...')
      print('...')
      print('...')
      print("destinationCallInstance is: ", destinationCallInstance)
      print("destinationCallParent is: ", destinationCallParent)
      print("foundationInstanceName is: ", foundationInstanceName)
      print("templateName is: ", templateName)
      print("instanceName is: ", instanceName)
      print("key_source is: ", key_source)
      print("tfvars_file_and_path is: ", tfvars_file_and_path)
      print('...')
      print('...')
      print('...')
      cleanupAfterOperation(destinationCallInstance, destinationCallParent, foundationInstanceName, templateName, instanceName, key_source, tfvars_file_and_path)
    else:  
      logString = "-------------------------------------------------------------------------------------------------------------------------------"
      logWriter.writeLogVerbose("acm", logString)
      logString = "ERROR: Failed to off this instance named: " + instanceName + ".  Halting program here so you can examine what went wrong and fix the problem before re-running the program. "
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
  else:  
    logString = "The instance specified as \"" + instanceName + "\" does not have any corresponding call to a module that might manage it.  Either it does not exist or it is outside the scope of this program.  Specifically, the following directory does not exist: " + destinationAutoScalingSubnetCallInstance + "  Therefore, we are not processing the request to remove the instance named: \"" + instanceName + "\""
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)

###############################

def assembleAndRunCommand(cloud, systemInstanceName, keyDir, template_Name, operation, yaml_infra_config_file_and_path, foundationInstanceName, parentInstanceName, instanceName, destinationCallInstance, typeName, module_config_file_and_path):
#  configAndSecretsPath = config_cliprocessor.inputVars.get('configAndSecretsPath')
#  dirOfConfig = configAndSecretsPath + "vars\\config\\" + cloud + "\\"
#  moduleConfigFileAndPath = module_config_file_and_path
  if typeName == 'networkFoundation':  
    print('typeName is: ', typeName)
    global foundationApply
    foundationApply = True
#    quit('J!m')
  commandToRun = 'invalid value must be reset below'
  tool = "terraform"
  org = config_fileprocessor.getFirstLevelValue(yaml_infra_config_file_and_path, "organization")
  binariesPath = config_cliprocessor.inputVars.get('dependenciesBinariesPath') 
  if operation == 'off':
    #Passing foundationInstanceName into getVarsFragment because we want to use the keys associated with the network foundation when we are attaching anything to the network foundation.
    varsFrag = command_builder.getVarsFragment(tool, keyDir, yaml_infra_config_file_and_path, module_config_file_and_path, cloud, instanceName, parentInstanceName, instanceName, org)
    commandToRun = binariesPath + "terraform destroy -auto-approve" + varsFrag
  elif operation == 'on':
    #Passing foundationInstanceName into getVarsFragment because we want to use the keys associated with the network foundation when we are attaching anything to the network foundation.
    varsFrag = command_builder.getVarsFragment(tool, keyDir, yaml_infra_config_file_and_path, module_config_file_and_path, cloud, instanceName, parentInstanceName, instanceName, org)
    commandToRun = binariesPath + "terraform apply -auto-approve " + varsFrag
#    quit('breakpoint in assembleAndRunCommand')
  elif operation == 'output':
    commandToRun = binariesPath + 'terraform output'
  else:
    logString = "Error: Invalid value for operation: " + operation
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
  logWriter.writeLogVerbose("acm", logString)
  logWriter.writeLogVerbose("acm", logString)
  logString = "commandToRun is: " + commandToRun
  logWriter.writeLogVerbose("acm", logString)
  logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
  logWriter.writeLogVerbose("acm", logString)
  logWriter.writeLogVerbose("acm", logString)
  logString = '... destinationCallInstance is: '+ destinationCallInstance
  logWriter.writeLogVerbose("acm", logString)

#  if operation != 'output':
#    quit('BREAKPOINT TO DEBUG SOURCE KEYS. ')
#  if systemInstanceName == "admin":
#    import traceback
#    traceback.print_stack()
  command_runner.runTerraformCommand(commandToRun, destinationCallInstance)
#  if operation == 'output':
#    for outputVar in tfOutputDict:
#      print(outputVar,' is: ', tfOutputDict.get(outputVar))
#    quit('After Output!!')
###############################

def changePointerLineInCallToModule(fileName, searchTerm, newPointerLine): 
  print('fileName is: ', fileName)
  with fileinput.FileInput(fileName, inplace = True) as f: 
    for line in f: 
      if searchTerm in line: 
        print(newPointerLine, end ='\n') 
      else: 
        print(line, end ='') 
  print('... searchTerm is: ', searchTerm)
#  quit('!')

def deleteWrongOSPointerLineInCallToModule(fileName, searchTerm): 
  print('fileName is: ', fileName)
#  quit('W!')
  with fileinput.FileInput(fileName, inplace = True) as f: 
    for line in f: 
      if searchTerm in line: 
        print('', end ='\n') 
      else: 
        print(line, end ='') 

def convertPathForOS(pathToApplicationRoot, relativePath):
  if platform.system() == 'Windows':
    if '/' in relativePath:
      relativePath = relativePath.replace("/", "\\\\")
    destinationCallParent = pathToApplicationRoot + relativePath
  else:
    if '\\' in relativePath:
      relativePath = relativePath.replace('\\', '/')
    destinationCallParent = pathToApplicationRoot + relativePath
  return destinationCallParent

def createCallDirectoryAndFile(sourceOfCallTemplate, destinationCallInstance, newPointerLineWindows, newPointerLineLinux, oldTfStateName, foundationInstanceName, templateName, instanceName):
  keySource = config_cliprocessor.inputVars.get('keySource')
  dynamicVarsPath = config_cliprocessor.inputVars.get('dynamicVarsPath')
  Path(destinationCallInstance).mkdir(parents=True, exist_ok=True)
  copy_tree(sourceOfCallTemplate, destinationCallInstance)
  fileName = destinationCallInstance + "main.tf"
  print('fileName is: ', fileName)
  if platform.system() == 'Windows':
    #WORK ITEM: change this 4 line windows block to reflect the two line linux version below it.
    searchTerm = "/modules/"
    deleteWrongOSPointerLineInCallToModule(fileName, searchTerm)
    searchTerm = "\\modules\\"
    changePointerLineInCallToModule(fileName, searchTerm, newPointerLineWindows)
  else: 
    searchTerm = ' source = '
    replacePointerLineInCallToModule(fileName, searchTerm, newPointerLineLinux)
#    searchTerm = "\\modules\\"
#    deleteWrongOSPointerLineInCallToModule(fileName, searchTerm)
#    searchTerm = "/modules/"
#    changePointerLineInCallToModule(fileName, searchTerm, newPointerLineLinux)
  if keySource != "keyVault":
    if(checkIfFileExists(oldTfStateName)):
      logString = "oldTfStateName file exists. Copying the backup tfstate file into this directory to use again."
      logWriter.writeLogVerbose("acm", logString)
      destStateFile = destinationCallInstance + "terraform.tfstate"
      shutil.copyfile(oldTfStateName, destStateFile)
    else:
      logString = "oldTfStateName files does NOT exist. "
      logWriter.writeLogVerbose("acm", logString)

def replacePointerLineInCallToModule(fileName, searchTerm, newPointerLine): 
  print('fileName is: ', fileName)
  with fileinput.FileInput(fileName, inplace = True) as f: 
    for line in f: 
      if searchTerm in line: 
        line = line.replace('\\','/')
        line = line.replace('//','/')
        lineInQuestion = line
        firstQuoteIndex = line.index('"',0)
        partBeforeQuote = line[0:firstQuoteIndex]
        partAfterQuote = line[firstQuoteIndex:]
        moduleStartIndex = partAfterQuote.index('m',0)
        partBeforeModule = partAfterQuote[0:moduleStartIndex]
        partStartingWithModule = partAfterQuote[moduleStartIndex:]
        replacementLine = partBeforeQuote+'"../../../../'+partStartingWithModule
        print(replacementLine, end ='\n') 
      else: 
        print(line, end ='') 
  print('lineInQuestion is: ', lineInQuestion)
  print('firstQuoteIndex is: ', firstQuoteIndex)
  print('partBeforeQuote is: ', partBeforeQuote)
  print('partAfterQuote is: ', partAfterQuote)
  print('moduleStartIndex is: ', moduleStartIndex)
  print('partBeforeModule is: ', partBeforeModule)
  print('partStartingWithModule is: ', partStartingWithModule)
  print('replacementLine is: ', replacementLine)
#  quit('no no no!')

def initializeTerraformBackend(cloud, operation, keyDir, yamlInfraFileAndPath, foundationInstanceName, parentInstanceName, typeName, moduleConfigFileAndPath, keyFile, destinationCallInstance, remoteBackend, instanceName):
#  quit("s")

  binariesPath = config_cliprocessor.inputVars.get('dependenciesBinariesPath') 
  kw = config_cliprocessor.inputVars.get('tfBkndAzureParams')
  keySource = config_cliprocessor.inputVars.get('keySource')

  print("... remoteBackend is: ", remoteBackend)

  if remoteBackend is True: 
    tool = "terraform"
    org = config_fileprocessor.getFirstLevelValue(yamlInfraFileAndPath, "organization")
    backendVars = command_builder.getBackendVarsFragment(tool, keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud, foundationInstanceName, parentInstanceName, destinationCallInstance, org, instanceName)
    initCommand= binariesPath + "terraform init -backend=true " + backendVars
  else:
    initCommand = binariesPath + 'terraform init '
  logString = "...................................................................................."
  logWriter.writeLogVerbose("acm", logString)
  logString = "initCommand is: " + initCommand
  logWriter.writeLogVerbose("acm", logString)
  logString = "...................................................................................."
  logWriter.writeLogVerbose("acm", logString)
#  quit("BREAKPOINT")
  command_runner.runTerraformCommand(initCommand, destinationCallInstance)	
  #Add error handling to validate that init command succeeded.

def instantiateCallToModule(cloud, operation, keyDir, yaml_infra_config_file_and_path, foundationInstanceName, parentInstanceName, typeName, module_config_file_and_path, repoName, instanceName, templateName, oldTfStateName):
  yamlConfigFileAndPath = yaml_infra_config_file_and_path
  foundationInstanceName = config_fileprocessor.getFoundationInstanceName(yamlConfigFileAndPath)
  if (foundationInstanceName is None) or (len(foundationInstanceName)==0):
    foundationInstanceName = "nof"
  relativePathTemplate = command_builder.getSlashForOS() + "calls-to-modules" + command_builder.getSlashForOS() + "templates" + command_builder.getSlashForOS() + templateName + command_builder.getSlashForOS()
  keySource = config_cliprocessor.inputVars.get('keySource')
  if templateName == 'network-foundation':
    relativePathInstance = command_builder.getSlashForOS() + "calls-to-modules" + command_builder.getSlashForOS() + "instances" + command_builder.getSlashForOS() + templateName + command_builder.getSlashForOS() +foundationInstanceName+"-" + templateName + command_builder.getSlashForOS()  
    keyFile = foundationInstanceName + "-" + templateName  
  else:
    relativePathInstance = command_builder.getSlashForOS() + "calls-to-modules" + command_builder.getSlashForOS() + "instances" + command_builder.getSlashForOS() + templateName + command_builder.getSlashForOS() +foundationInstanceName+"-"+instanceName+"-" + templateName + command_builder.getSlashForOS()
    keyFile = foundationInstanceName + "-" + instanceName + "-" + templateName  
  keyFile = command_builder.formatPathForOS(keyFile)

  userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')+command_builder.getSlashForOS()
  pathToTemplate = userCallingDir+repoName+command_builder.getSlashForOS()+'terraform'+command_builder.getSlashForOS()
  sourceOfCallTemplate = convertPathForOS(pathToTemplate, relativePathTemplate)
  destinationCallInstance = convertPathForOS(pathToTemplate, relativePathInstance)

  print('sourceOfCallTemplate is: ', sourceOfCallTemplate)
  print('relativePathTemplate is: ', relativePathTemplate)
  print('destinationCallInstance is: ', destinationCallInstance)
  print('userCallingDir is: ', userCallingDir)
  print('relativePathInstance is: ', relativePathInstance)
#  quit('T!')
  remoteBackend = False
  templateFileAndPath = sourceOfCallTemplate + "main.tf"
  if os.path.isfile(templateFileAndPath):
    with open(templateFileAndPath) as f:
      for line in f:
        if 'backend \"' in line:
          if line[0] != "#":
            remoteBackend = True
  print('templateFileAndPath is: ', templateFileAndPath)
#  quit('>')
  if remoteBackend == True:  
    oldTfStateName = "remoteBackend"
  if platform.system() == 'Windows':
    if len(destinationCallInstance) >135:
      logString = "destinationCallInstance path is too long at: " + destinationCallInstance
      logWriter.writeLogVerbose("acm", logString)
      logString = "ERROR: The path of the directory into which you are placing the call to the terraform module is greater than 135 characters and is thus too long.  Halting program with this meaningful message so that you can avoid receiving an unhelpful message from the program vendor.  Please shorten the length of the path and re-run.  You can either move your app higher up in the directory structure, or you can change your config by shortening the template names and instance names that are fed into this path definition. "
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
  p = Path(destinationCallInstance)
  if p.exists():
    logString = "The instance of the call to module already exists."
    logWriter.writeLogVerbose("acm", logString)
  else:
    dynamicVarsPath = config_cliprocessor.inputVars.get('dynamicVarsPath')
    newPointerLineWindows="  source = \"..\\\..\\\..\\\..\\\modules\\\\" + templateName + "\""
    newPointerLineLinux="  source = \"../../../../modules/" + templateName + "\""
    print('-- -- -- newPointerLineLinux is: ', newPointerLineLinux)
    createCallDirectoryAndFile(sourceOfCallTemplate, destinationCallInstance, newPointerLineWindows, newPointerLineLinux, oldTfStateName, foundationInstanceName, templateName, instanceName)
#  quit("r..")
  initializeTerraformBackend(cloud, operation, keyDir, yaml_infra_config_file_and_path, foundationInstanceName, parentInstanceName, typeName, module_config_file_and_path, keyFile, destinationCallInstance, remoteBackend, instanceName)
  return destinationCallInstance

def offInstanceOfCallToModule(locationOfCallInstance, parentDirOfCallInstance):
  if os.path.exists(locationOfCallInstance) and os.path.isdir(locationOfCallInstance):
    path = Path(locationOfCallInstance)
    shutil.rmtree(path)
  else:
    logString = "Given Directory doesn't exist: " + locationOfCallInstance
    logWriter.writeLogVerbose("acm", logString)
  if os.path.exists(parentDirOfCallInstance) and os.path.isdir(parentDirOfCallInstance):
    if not os.listdir(parentDirOfCallInstance):
      logString = "Directory is empty"
      logWriter.writeLogVerbose("acm", logString)
      path = Path(parentDirOfCallInstance)
      shutil.rmtree(path)
    else:    
      logString = "Parent directory is not empty, so we will keep it for now: " + parentDirOfCallInstance
      logWriter.writeLogVerbose("acm", logString)
  else:
    logString = "Given Directory doesn't exist: " + parentDirOfCallInstance
    logWriter.writeLogVerbose("acm", logString)

def getBackedUpStateFileName(absPath, foundationInstance, templateNm, instanceNm):
  template_name = templateNm.replace('/', '__')
  print(type(absPath))
  print(type(foundationInstance))
  print(type(templateNm))
  print(type(instanceNm))
  backedUpStateFileName = absPath + '\\terraform_tfstate_' + foundationInstance + '-' + template_name + '-' + instanceNm + '.backup'
  backedUpStateFileName = command_builder.formatPathForOS(backedUpStateFileName)
  return backedUpStateFileName

def checkIfFileExists(oldTfStateName):
  doesExist = False
  try:
    with open(oldTfStateName) as f:
      f.readlines()
      doesExist = True
  except IOError:
    doesExist = False
  return doesExist

def saveKeyFile(destinationCallInst, type_name, cloudprov, source_keys_file_and_path, dest_keys_file_and_path, org_name):  
  ### Save the newly-generated keys
  secKey = 'empty'
  #Make work item to set localBackend programmatically.  Here we are developing the remote backend feature, so we are setting this here for now.
  localBackend = False
  if localBackend:
    tfStateFile = destinationCallInst + 'terraform.tfstate'
    data = json.load(open(tfStateFile, 'r'))
    data_resources = data["resources"]
    for i in data_resources:
      if i["type"] == 'azuread_service_principal_password': 
        secKey = i['instances'][0]['attributes']['value']
  else:
    binariesPath = config_cliprocessor.inputVars.get('dependenciesBinariesPath') 
    print("............")
    myCommand = binariesPath + "terraform show --json"
    returnedData = command_runner.getShellJsonData(myCommand, destinationCallInst)
    returnedData = json.loads(returnedData)
    data_resources = returnedData["values"]["root_module"]["child_modules"][0]["resources"]
    passCount = 0
    for i in data_resources:
      if i["type"] == 'azuread_service_principal_password':
        secKey = i['values']['value']
        passCount += 1
    if passCount > 1:
      logString = "Error: too many instances of azuread_service_principal_password.  We currently support one instance per module.  If you need support for more, submit a feature request. "
      logWriter.writeLogVerbose("acm", logString)
      exit(1)
#  quit("BREAKPOINT to debug saveKeyFile()  ")
  if cloudprov == 'aws':
    saveAWSKeyFile(data_resources)
  elif cloudprov == 'azure':
    saveAzureKeyFile(secKey, source_keys_file_and_path, dest_keys_file_and_path, type_name, org_name)

def saveAWSKeyFile(data_resources): 
  for i in data_resources:
    if i["type"] == 'aws_iam_access_key': 
      pubKey = i['instances'][0]['attributes']['id']
      secKey = i['instances'][0]['attributes']['secret']
      #Next: Save the new IAM user's keys in a yaml file for use creating and offing infrastructure.  NOTE: save this to a secrets vault instead of a file if you are using a vault.
      dict_file = [{'keyPairs' : [{'name': 'demoKeyPair', '_public_access_key': pubKey, '_secret_access_key': secKey} ]}]
      yamlKeysNetworkFileAndPath = config_cliprocessor.inputVars.get('dirOfYamlKeys') + 'keys.yaml' #config_cliprocessor.inputVars.get('nameOfYamlKeys_AWS_Network_File')
      with open(yamlKeysNetworkFileAndPath, 'w') as file:
        documents = yaml.dump(dict_file, file)

def saveAzureKeyFile(secKey, src_yaml_keys_file_and_path, dest_yaml_keys_file_and_path, type_name, org_name):
  appId = command_runner.appId
  if appId.startswith('"') and appId.endswith('"'):
    appId = appId[1:-1]
  if 'empty' in secKey:
    logString = "Error: Failed to load Client Secret.  This might be resolved by re-running the admin module.  Halting program here so you can examine the problem. "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)
  if 'whatToSearchFor' in appId: #Change whatToSearchFor to an actual string once the error state is defined.  Just leaving this here now to show where and how to place this check.
    logString = "Error: Failed to load appId.  This might be resolved by re-running the admin module.  Halting program here so you can examine the problem. "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)
  myList = []
  keys = {}
  with open(src_yaml_keys_file_and_path) as f:
    for line in f:
      lineParts = line.split(":",1)
      keys[lineParts[0]] = lineParts[1].replace("\n","").strip('\"')
  for key in keys:
    if key == 'secretsType':
      itemStr = key + ": "+ 'generated'
      myList.append(itemStr)
    elif key == 'name':
      itemStr = key + ": "+ 'demoKeyPair'
      myList.append(itemStr)
    elif key == 'clientId': 
      itemStr = key + ": "+ appId
      myList.append(itemStr)
    elif key == 'clientSecret': 
      secKey = secKey.replace('"','')
      secKey = secKey.replace("'","")
      itemStr = key + ": "+ secKey
      myList.append(itemStr)
    else: 
      itemStr = key + ": "+ keys.get(key)
      myList.append(itemStr)
  dictVersion = {}
  for key_value in myList:
    key, value = key_value.split(': ', 1)
    dictVersion[key] = value
  with open(dest_yaml_keys_file_and_path, 'w') as file:
    documents = yaml.dump(dictVersion, file)

def setDoCleanUp(oper):
  cleanup = False
  if oper == 'on':
    if command_runner.terraformResult == "Applied": 
      cleanup = True
  elif oper == 'off':
    if command_runner.terraformResult == "Destroyed": 
      cleanup = True
  elif oper == 'output':
    #Add some check here to confirm that the output operation succeeded.
    cleanup = True
  return cleanup

def cleanupAfterOperation(destinationCallInstance, destinationCallParent, foundationInstanceName, templateName, instanceName, key_source, tfvars_file_and_path):
  dynamicVarsPath = config_cliprocessor.inputVars.get('dynamicVarsPath')
  print('dynamicVarsPath is: ', dynamicVarsPath)
  if key_source =="keyFile":
    #Now make a backup copy of the tfstate file.
    tfStateSrc = destinationCallInstance + 'terraform.tfstate'
    tfStateDest = getBackedUpStateFileName(dynamicVarsPath, foundationInstanceName, templateName, instanceName)
    if os.path.isfile(tfStateSrc):
      shutil.copy(tfStateSrc, tfStateDest)
  offInstanceOfCallToModule(destinationCallInstance, destinationCallParent)
#  quit('ok!')

  ###############################################################################
  ### Delete the tfvars file and the instance of the call to module
  ### Note we only want keys to be in external locations such as a vault
  ###############################################################################
  try:
    logString = "About to remove the tfvars file. "
    logWriter.writeLogVerbose("acm", logString)
  except OSError:
    pass



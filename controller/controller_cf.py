## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    
  
import json
import yaml
import sys
import time
import datetime
import subprocess
import platform
import os

import command_runner
import command_builder
import config_fileprocessor
import config_cliprocessor
import logWriter

def createStack(infraConfigFileAndPath, keyDir, caller, serviceType, instName):
  if platform.system() == 'Linux':
    configureSecrets(keyDir)
  ## STEP 1: Populate variables
  app_parent_path = config_cliprocessor.inputVars.get('app_parent_path')
  foundationInstanceName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'instanceName')
  region = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'region')
  outputDict = {}
  if caller == 'networkFoundation':
    typeParent = caller
    serviceType = 'networkFoundation'
    templateName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'templateName')
    stackName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'stackName')
  elif caller == 'serviceInstance':
    typeParent = 'systems'
    templateName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'templateName')
    stackName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'stackName')
    outputDict['ImageNameRoot'] = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'imageName')
  elif caller == 'image':
    typeParent = 'imageBuilds'
    templateName = config_fileprocessor.getImagePropertyValue(infraConfigFileAndPath, 'images', instName, 'templateName')
    stackName = config_fileprocessor.getImagePropertyValue(infraConfigFileAndPath, 'images', instName, 'stackName')
  organization = config_fileprocessor.getFirstLevelValue(infraConfigFileAndPath, 'organization')
  module_config_file_and_path = getModuleConfigFileAndPath(infraConfigFileAndPath, typeParent, serviceType, instName, app_parent_path)
  deployVarsFragment = command_builder.getCloudFormationVarsFragment(keyDir, infraConfigFileAndPath, module_config_file_and_path, foundationInstanceName, None, instName, organization, caller, serviceType, outputDict)
  cfTemplateFileAndPath = app_parent_path+templateName
  cfTemplateFileAndPath = command_builder.formatPathForOS(cfTemplateFileAndPath)
  ## STEP 2: Check to see if stack already exists
  checkExistCmd = 'aws cloudformation describe-stacks --stack-name '+stackName+ ' --region '+region
  logString = "checkExistCmd is: "+checkExistCmd
  logWriter.writeLogVerbose("acm", logString)
  if checkIfStackExists(checkExistCmd):
    createChangeSetCommand = 'aws cloudformation create-change-set --change-set-name my-change --stack-name '+stackName+' --template-body file://'+cfTemplateFileAndPath+' '+str(deployVarsFragment)+' --output text --query Id '
    logString = 'createChangeSetCommand is: '+ createChangeSetCommand
    logWriter.writeLogVerbose("acm", logString)
    jsonStatus = command_runner.getShellJsonResponse(createChangeSetCommand)
    logString = 'Initial response from stack command is: '+str(jsonStatus)
    logWriter.writeLogVerbose("acm", logString)
    describeChangesCmd = 'aws cloudformation describe-change-set --change-set-name '+str(jsonStatus)
    logString = 'describeChangesCmd is: '+ describeChangesCmd
    logWriter.writeLogVerbose("acm", logString)
    jsonStatus = command_runner.getShellJsonResponse(describeChangesCmd)
    logString = 'describeChangesCmd response is: ', str(jsonStatus)
    logWriter.writeLogVerbose("acm", logString)
    jsonStatus = yaml.safe_load(jsonStatus)
    respStatus = jsonStatus['Status']
    changeSetId = jsonStatus['ChangeSetId']
    logString = 'describeChangesCmd response Status is: ', str(respStatus)
    logWriter.writeLogVerbose("acm", logString)
    logString = 'changeSetId is: '+ changeSetId
    logWriter.writeLogVerbose("acm", logString)
    deleteChangeSetCmd = 'aws cloudformation delete-change-set --change-set-name '+str(changeSetId)
    logString = "deleteChangeSetCmd is: " + deleteChangeSetCmd
    logWriter.writeLogVerbose("acm", logString)
    jsonStatus = command_runner.getShellJsonResponse(deleteChangeSetCmd)
    logString = 'deleteChangeSetCmd response is: ', str(jsonStatus)
    logWriter.writeLogVerbose("acm", logString)
    if respStatus == 'FAILED':
      logString = 'WARNING: There are NO changes to make, so we are returning without creating or updating the stack. '
      logWriter.writeLogVerbose("acm", logString)
      return
    elif respStatus == 'CREATE_COMPLETE':
      cfDeployCommand = 'aws cloudformation update-stack --stack-name '+stackName+' --template-body file://'+cfTemplateFileAndPath+' '+str(deployVarsFragment)
      logString = 'Response from check existance of stack command is: True'
      logWriter.writeLogVerbose("acm", logString)
      logString = "cfDeployCommand is: "+cfDeployCommand
      logWriter.writeLogVerbose("acm", logString)
      jsonStatus = command_runner.getShellJsonResponse(cfDeployCommand)
      logString = 'Initial response from stack command is: ', str(jsonStatus)
      logWriter.writeLogVerbose("acm", logString)
      ## Check status of deployment repeatedly until deployment has completed.
      if not checkStatusOfStackCommand('update', stackName):
        logString = 'ERROR: Stack update command failed.'
        logWriter.writeLogVerbose("acm", logString)
        sys.exit(1)
    else:
      logString = "ERROR: The aws cloudformation describe-change-set command returned a value that was not either FAILED or CREATE_COMPLETE .  Halting the program so that you can debug the cause of the problem."
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
  else:
    cfDeployCommand = 'aws cloudformation create-stack --stack-name '+stackName+' --template-body file://'+cfTemplateFileAndPath+' '+str(deployVarsFragment)
    logString = 'Response from check existance of stack command is: False'
    logWriter.writeLogVerbose("acm", logString)
    logString = 'cfDeployCommand is: '+ cfDeployCommand
    logWriter.writeLogVerbose("acm", logString)
    jsonStatus = command_runner.getShellJsonResponse(cfDeployCommand)
    logString = 'Initial response from stack command is: '+ str(jsonStatus)
    logWriter.writeLogVerbose("acm", logString)
    ## Check status of deployment repeatedly until deployment has completed.
    if not checkStatusOfStackCommand('create', stackName):
      logString = 'ERROR: Stack create command failed.'
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
  destroySecrets()

def destroyStack(infraConfigFileAndPath, keyDir, caller, serviceType, instName):
  if platform.system() == 'Linux':
    configureSecrets(keyDir)
  ## STEP 1: Populate variables
  app_parent_path = config_cliprocessor.inputVars.get('app_parent_path')
#  foundationInstanceName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'instanceName')
  region = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'region')
  if caller == 'networkFoundation':
#    typeParent = caller
    serviceType = 'networkFoundation'
    templateName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'templateName')
    stackName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'stackName')
  elif caller == 'serviceInstance':
#    typeParent = 'systems'
    templateName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'templateName')
    stackName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'stackName')
  elif caller == 'image':
#    typeParent = 'imageBuilds'
    templateName = config_fileprocessor.getImagePropertyValue(infraConfigFileAndPath, 'images', instName, 'templateName')
    stackName = config_fileprocessor.getImagePropertyValue(infraConfigFileAndPath, 'images', instName, 'stackName')
#  organization = config_fileprocessor.getFirstLevelValue(infraConfigFileAndPath, 'organization')
#  module_config_file_and_path = getModuleConfigFileAndPath(infraConfigFileAndPath, typeParent, serviceType, instName, app_parent_path)
#  outputDict = {}

  thisStackId = getStackId(stackName)
  logString = 'thisStackId is: '+ thisStackId
  logWriter.writeLogVerbose("acm", logString)
  if thisStackId == 'none':
    logString = 'WARNING: No stacks with the name '+stackName+' are currently in the CREATE_COMPLETE state when this run is initiated.  We are therefore skipping the delete process for this stack and continuing the program flow to proceed with any downstream steps.  '
    logWriter.writeLogVerbose("acm", logString)
  else:
    ## STEP 2: Assemble and run deployment command
    cfTemplateFileAndPath = app_parent_path+templateName
    cfTemplateFileAndPath = command_builder.formatPathForOS(cfTemplateFileAndPath)
    cfDeployCommand = 'aws cloudformation delete-stack --stack-name '+stackName
    jsonStatus = command_runner.getShellJsonResponse(cfDeployCommand)
    logString = 'Initial response from stack command is: '+ str(jsonStatus)
    logWriter.writeLogVerbose("acm", logString)
    trackStackProgress(thisStackId, region)
  destroySecrets()

def listMatchingStacks(stackName, stackId):
  stackIdsList = []
  checkCmd = 'aws cloudformation list-stacks'
  jsonStatus = command_runner.getShellJsonResponse(checkCmd)
  responseData = yaml.safe_load(jsonStatus)
  for item in responseData['StackSummaries']:
    name = item['StackName']
    aStackId = item['StackId']
    if name == stackName:
      if stackId == aStackId:
        stackIdsList.append(aStackId)
  return stackIdsList

def trackStackProgress(stackId, region):
  thisStatus = 'empty'
  n=0
  while thisStatus!='DELETE_COMPLETE':
    checkCmd = 'aws cloudformation describe-stacks --stack-name '+stackId+ ' --region '+region
    jsonStatus = command_runner.getShellJsonResponse(checkCmd)
    responseData = yaml.safe_load(jsonStatus)
    for item in responseData['Stacks']:
      status = item['StackStatus']
      aStackId = item['StackId']
      if stackId == aStackId:
        thisStatus = status
        if status == 'DELETE_COMPLETE':
          logString = "Delete operation completed on stack."
          logWriter.writeLogVerbose("acm", logString)
          return
    n+=1
    if n>10:
      logString = "ERROR:  Quitting because operation failed to complete after " + str(n) + " attempts. "
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
    logString = "Operation still in process.  About to sleep 30 seconds before trying progress check number: " + str(n)
    logWriter.writeLogVerbose("acm", logString)
    time.sleep(30)
  return

def getStackId(stackName):
  idToReturn = 'none'
  checkCmd = 'aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE'
  jsonStatus = command_runner.getShellJsonResponse(checkCmd)
  responseData = yaml.safe_load(jsonStatus)
  for item in responseData['StackSummaries']:
    name = item['StackName']
    status = item['StackStatus']
    stackId = item['StackId']
    if (name == stackName) and (status == 'CREATE_COMPLETE'):
      logString = name+ ' : '+ status+ ' : '+ stackId
      logWriter.writeLogVerbose("acm", logString)
      idToReturn = stackId
  return idToReturn

def checkStatusOfStackCommand(operation, stackName):
  counter = 0
  status = 'NOT_STARTED'
  logicalResourceId = 'empty'
  if operation == 'create':
    successStatus = 'CREATE_COMPLETE'
  elif operation == 'update':
    successStatus = 'UPDATE_COMPLETE'
  elif operation == 'destroy':
    successStatus = 'DELETE_COMPLETE'
  failureStatus = 'ROLLBACK_COMPLETE'
  while (status != successStatus) or(status != failureStatus):
    cfStatusCommand = 'aws cloudformation describe-stack-events --stack-name '+stackName
    jsonStatus = command_runner.getShellJsonResponse(cfStatusCommand)
    responseYaml = yaml.safe_load(jsonStatus)
    for event in responseYaml['StackEvents']:
      for eventItem in event:
        if eventItem == 'ResourceType':
          if event[eventItem] == 'AWS::CloudFormation::Stack':
            logicalResourceId = event['LogicalResourceId']
            status = event['ResourceStatus']
            counter +=1
            logString = 'Matching event number: '+ str(counter)
            logWriter.writeLogVerbose("acm", logString)
            if (status == successStatus) and (logicalResourceId == stackName):
              logString = "... Stack Completed!"
              logWriter.writeLogVerbose("acm", logString)
              return True
            elif (status == failureStatus) and (logicalResourceId == stackName):
              logString = "... Stack failed with status ROLLBACK_COMPLETE !"
              logWriter.writeLogVerbose("acm", logString)
              return False
    #Wait before each re-try to allow remote process enough time to complete.
    time.sleep(15)
  return False

def checkIfStackExists(cmd,counter=0):
  #Consider moving this function to the AWS controller
  process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
  data = process.stdout
  err = process.stderr
  logString = "data string is: " + str(data)
  logWriter.writeLogVerbose("acm", logString)
  logString = "err is: " + str(err)
  logWriter.writeLogVerbose("acm", logString)
  logString = "process.returncode is: " + str(process.returncode)
  logWriter.writeLogVerbose("acm", logString)
  logString = "cmd is: " + cmd
  logWriter.writeLogVerbose("acm", logString)
  if process.returncode == 0:
    logString = str(data)
    logWriter.writeLogVerbose("shell", logString)
    return True
  elif (process.returncode == 254) or (process.returncode == '254'):
    return False
  else:
    if counter == 0:
      counter +=1 
      logString = "Sleeping 30 seconds bewfore running the command a second time in case a latency problem caused the first attempt to fail. "
      logWriter.writeLogVerbose('acm', logString)
      import time
      time.sleep(30)
      checkIfStackExists(cmd,counter)
    else:
      logString = "Error: " + str(err)
      logWriter.writeLogVerbose("shell", logString)
      logString = "Error: Return Code is: " + str(process.returncode)
      logWriter.writeLogVerbose("shell", logString)
      logString = "ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem."
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)

def getModuleConfigFileAndPath(infraConfigFileAndPath, typeParent, serviceType, instName, app_parent_path):
  templateName = config_fileprocessor.getTemplateName(infraConfigFileAndPath, typeParent, serviceType, None, instName, None)  
  if templateName.count('/') == 2:
    nameParts = templateName.split("/")
    if (len(nameParts[0]) > 1) and (len(nameParts[1]) >1) and (len(nameParts[2]) > 1):
      templateName = nameParts[2]  
      module_config_file_and_path = app_parent_path + nameParts[0] + '\\variableMaps\\' + templateName + '.csv'
    else:
      logString = 'ERROR: templateName is not valid. '
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
  else:  
    logString = 'templateName is: '+ templateName
    logWriter.writeLogVerbose("acm", logString)
    logString = "Template name is not valid.  Must have only one /.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  module_config_file_and_path = command_builder.formatPathForOS(module_config_file_and_path)
  return module_config_file_and_path

def configureSecrets(keyDir): 
  yamlKeysFileAndPath = config_fileprocessor.getYamlKeysFileAndPath(keyDir)
  AWSAccessKeyId = config_fileprocessor.getFirstLevelValue(yamlKeysFileAndPath, 'AWSAccessKeyId')
  AWSSecretKey = config_fileprocessor.getFirstLevelValue(yamlKeysFileAndPath, 'AWSSecretKey')
  outputDir = os.path.expanduser('~/.aws')
  os.mkdir(outputDir)
  fileName = outputDir+'/credentials'
  with open(fileName, 'w') as f:
    defaultLine = '[default]\n'
    f.write(defaultLine)
    idLine = 'aws_access_key_id='+AWSAccessKeyId+'\n'
    f.write(idLine)
    keyLine = 'aws_secret_access_key='+AWSSecretKey+'\n'
    f.write(keyLine)

def destroySecrets():
  filename = os.path.expanduser('~/.aws') + '/credentials'
  try:
    os.remove(filename)
  except OSError:
    pass

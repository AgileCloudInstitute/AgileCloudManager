## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import config_fileprocessor
import command_builder
import command_runner
import logWriter
import controller_arm

backendFile = ''

def createTfBackend(instName, infraConfigFileAndPath, keyDir, paramsDict):
  import config_keysassembler
  cloud = config_fileprocessor.getCloudName(infraConfigFileAndPath)
  yaml_keys_file_and_path = command_builder.getKeyFileAndPath(keyDir, 'systems', cloud)
  resourceGroupName = ''
  resourceGroupRegion = ''
  templateName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, "tfBackend", instName, "templateName")
  print("..... instName in createTfBackend() is: ", instName)
  backendType = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, "tfBackend", instName, "type")
  logString = "backendType is: " + backendType
  logWriter.writeLogVerbose("acm", logString)
  if backendType == 'azurerm':  
    config_keysassembler.writeTheVarsFile(instName, infraConfigFileAndPath, keyDir, cloud, None, "tfBackend", None, None)
    #Get the variable values
    resourceGroupName = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'resourceGroupName')
    resourceGroupRegion = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'resourceGroupRegion')
    subscriptionId = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'subscriptionId')
    clientId = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'clientId')
    clientSecret = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'clientSecret')
    tenantId = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'tenantId')
    orgName = config_fileprocessor.getFirstLevelValue(infraConfigFileAndPath, "organization")
    storageAccountName = instName.lower() + orgName.lower()
    #ADD VALIDATION TO CONFIRM THAT storageAccountName IS NOT LONGER THAN 24 CHARACTERS TO PREVENT DOWNSTREAM ERROR.
    outputDir = config_keysassembler.getOutputDir(instName)
    keysFile = outputDir + "keys.yaml"
    #Login to az cli
    #### #The following command gets the client logged in and able to operate on azure repositories.
    myCmd = "az login --service-principal -u " + clientId + " -p " + clientSecret + " --tenant " + tenantId
    command_runner.getShellJsonResponse(myCmd)
    logString = "Finished running login command."
    logWriter.writeLogVerbose("acm", logString)
    #set subscription
    setSubscriptionCmd = 'az account set --subscription ' + subscriptionId
    command_runner.getShellJsonResponse(setSubscriptionCmd)
    logString = "Finished running setSubscription command."
    logWriter.writeLogVerbose("acm", logString)
    #First create storage account
    createStorageAccountCommand = "az storage account create --name " + storageAccountName + " --resource-group " + resourceGroupName + " --location " + resourceGroupRegion + " --sku Standard_LRS   --encryption-services blob " 
    print('xxx createStorageAccountCommand is: ', createStorageAccountCommand)
    command_runner.runShellCommand(createStorageAccountCommand)  
    logString = "Finished running createStorageAccountCommand. "
    logWriter.writeLogVerbose("acm", logString)
    getAccountKeyCommand = "az storage account keys list --resource-group " + resourceGroupName + " --account-name " + storageAccountName + " --query [0].value -o tsv "
    accountKey = command_runner.getAccountKey(getAccountKeyCommand)  
    #Then create the 6 storage containers within the storage account to correspond with the sections in infrastructureConfig 
    # Adding .lower() to the string declarations as a reminder that the azure portal only seems to accept lower case.  If you remove .lower() , then the containers that have camel case names like networkFoundation will NOT be created.
    storageContainerName = 'networkFoundation'.lower()
    createStorageContainerCommand = "az storage container create -n " + storageContainerName + " --fail-on-exist --account-name " + storageAccountName + " --account-key " + accountKey  
    command_runner.getShellJsonResponse(createStorageContainerCommand)  
    with open(keysFile, "a+") as f:  # append mode
      f.write("container_name:\""+storageContainerName+"\"\n")
      f.write("tfBackendStorageAccessKey:\""+accountKey+"\"\n")
    storageContainerName = 'systems'.lower()
    createStorageContainerCommand = "az storage container create -n " + storageContainerName + " --fail-on-exist --account-name " + storageAccountName + " --account-key " + accountKey  
    command_runner.getShellJsonResponse(createStorageContainerCommand)  
  elif backendType == 'azurerm2': 
#  elif len(paramsDict) > 0:
    caller = paramsDict["caller"]
    serviceType = paramsDict["serviceType"]
    print("infraConfigFileAndPath is: ", infraConfigFileAndPath)
    print("keyDir is: ", keyDir)
    print('caller is: ', caller)
    print("serviceType is: ", serviceType)
    print("instName is: ", instName)
#    quit('hohoho!')

    controller_arm.createDeployment(infraConfigFileAndPath, keyDir, 'serviceInstance', serviceType, instName)
#...
    print('ab1')
    config_keysassembler.writeTheVarsFile(instName, infraConfigFileAndPath, keyDir, cloud, None, "tfBackend", None, None)
    #Get the variable values
    print('ab2')
#    resourceGroupName = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'resourceGroupName')
    resourceGroupRegion = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'resourceGroupRegion')
    subscriptionId = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'subscriptionId')
    clientId = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'clientId')
    clientSecret = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'clientSecret')
    tenantId = getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'tenantId')
    orgName = config_fileprocessor.getFirstLevelValue(infraConfigFileAndPath, "organization")
#...
    resourceGroupName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, "tfBackend", instName, "resourceGroupName")
    storageAccountName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, "tfBackend", instName, "storageAccountName")
    print("storageAccountName is: ", storageAccountName)
    print("resourceGroupName is: ", resourceGroupName)
    print("resourceGroupRegion is: ", resourceGroupRegion)
    print("subscriptionId is: ", subscriptionId)
    print("clientId is: ", clientId)
    print("clientSecret is: ", clientSecret)
    print("tenantId is: ", tenantId)
    print("orgName is: ", orgName)
#    quit(':::0:::')
#...
#    storageAccountName = instName.lower() + orgName.lower()
    #ADD VALIDATION TO CONFIRM THAT storageAccountName IS NOT LONGER THAN 24 CHARACTERS TO PREVENT DOWNSTREAM ERROR.
    outputDir = config_keysassembler.getOutputDir(instName)
    keysFile = outputDir + "keys.yaml"
    #Login to az cli
    #### #The following command gets the client logged in and able to operate on azure repositories.
    myCmd = "az login --service-principal -u " + clientId + " -p " + clientSecret + " --tenant " + tenantId
    command_runner.getShellJsonResponse(myCmd)
    logString = "Finished running login command."
    logWriter.writeLogVerbose("acm", logString)
    #set subscription
    setSubscriptionCmd = 'az account set --subscription ' + subscriptionId
    command_runner.getShellJsonResponse(setSubscriptionCmd)
    logString = "Finished running setSubscription command."
    logWriter.writeLogVerbose("acm", logString)
#    #First create storage account
#    createStorageAccountCommand = "az storage account create --name " + storageAccountName + " --resource-group " + resourceGroupName + " --location " + resourceGroupRegion + " --sku Standard_LRS   --encryption-services blob " 
#    print('xxx createStorageAccountCommand is: ', createStorageAccountCommand)
#    command_runner.runShellCommand(createStorageAccountCommand)  
#    logString = "Finished running createStorageAccountCommand. "
#    logWriter.writeLogVerbose("acm", logString)
    print('ab3')
    print("resourceGroupName is: ", resourceGroupName)
    print("storageAccountName is: ", storageAccountName)

    getAccountKeyCommand = "az storage account keys list --resource-group " + resourceGroupName + " --account-name " + storageAccountName + " --query [0].value -o tsv "
    print("getAccountKeyCommand is: ", getAccountKeyCommand)
    accountKey = command_runner.getAccountKey(getAccountKeyCommand)  
    print('ab4')

    #Then create the 6 storage containers within the storage account to correspond with the sections in infrastructureConfig 
    # Adding .lower() to the string declarations as a reminder that the azure portal only seems to accept lower case.  If you remove .lower() , then the containers that have camel case names like networkFoundation will NOT be created.
    storageContainerName = 'networkFoundation'.lower()
    print('accountKey is: ', accountKey)
#    quit('BREAKPOINT TO DEBUG TFBACKEND')
 #   createStorageContainerCommand = "az storage container create -n " + storageContainerName + " --fail-on-exist --account-name " + storageAccountName + " --account-key " + accountKey  
 #   command_runner.getShellJsonResponse(createStorageContainerCommand)  
    with open(keysFile, "a+") as f:  # append mode
      f.write("storage_account_name:"+storageAccountName+"\n")
      f.write("container_name:"+storageContainerName+"\n")
      f.write("tfBackendStorageAccessKey:"+accountKey+"\n")
#...

def getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, propName):
  varVal = ''
  rgNameCoords = config_fileprocessor.getPropertyCoordinatesFromCSV(infraConfigFileAndPath, templateName, propName)
  coordsParts = rgNameCoords.split("/")
  print('rgNameCoords is: ', rgNameCoords)
  print('coordsParts is: ', coordsParts)

  if coordsParts[0] == 'infrastructureConfig.yaml':
    if rgNameCoords.count('/') == 1:
      if coordsParts[1] == 'networkFoundation':
        varVal = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, coordsParts[1], propName)
    elif rgNameCoords.count('/') == 2:
      parentPart = coordsParts[1]
      childPart = coordsParts[2]
      if parentPart == 'systems':
        varVal = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, "tfBackend", instName, propName)
  elif coordsParts[0] in yaml_keys_file_and_path:
    varVal = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, propName)
  else:
    logString = "No match: ", coordsParts[1]
    logWriter.writeLogVerbose("acm", logString)
  print('yaml_keys_file_and_path is: ', yaml_keys_file_and_path)
  print('infraConfigFileAndPath is: ', infraConfigFileAndPath)
  print('instName is: ', instName)
  print('templateName is: ', templateName)
  print('propName is: ', propName)
  print('varVal is: ', varVal)
#  quit('gggggggggg')
  return varVal

def writeBackendFile(outputDir, storageAccountName, storageContainerName, subscriptionId, clientId, clientSecret, tenantId, resourceGroupName):
  global backendFile
  backendFile = outputDir + storageAccountName + "." + storageContainerName + ".backend.tfvars"
  with open(backendFile, 'w') as f:
    f.write("storage_account_name = \""+storageAccountName+"\"\n")
    f.write("container_name       = \""+storageContainerName+"\"\n")
    f.write("subscription_id      = \""+subscriptionId+"\"\n")
    f.write("client_id            = \""+clientId+"\"\n")
    f.write("client_secret        = \""+clientSecret+"\"\n")
    f.write("tenant_id            = \""+tenantId+"\"\n")
    f.write("resource_group_name  = \""+resourceGroupName+"\"\n")

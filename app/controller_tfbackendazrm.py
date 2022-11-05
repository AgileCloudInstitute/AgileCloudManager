## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

from config_fileprocessor import config_fileprocessor
from config_keysassembler import config_keysassembler
from log_writer import log_writer
from command_formatter import command_formatter
from command_runner import command_runner
from command_builder import command_builder
from controller_arm import controller_arm

import shutil

class controller_tfbackendazrm:

  backendFile = ''

  def __init__(self):  
    pass

  #@public
  def createTfBackend(self, systemConfig, instance, paramsDict):
    lw = log_writer()
    cfm = command_formatter()
    cb = command_builder()
    cka = config_keysassembler()

    keyDir = systemConfig.get("keysDir")
    cfp = config_fileprocessor()
    keyDir = cfp.getKeyDir(systemConfig)
    yaml_keys_file_and_path = keyDir+cfm.getSlashForOS()+"keys.yaml"
    yaml_global_config_file_and_path = cfm.getConfigFileAndPath(keyDir)
    resourceGroupName = ''
    backendType = instance.get("type")
    logString = "backendType is: " + backendType
    lw.writeLogVerbose("acm", logString)
    if backendType == 'azurerm': 
      serviceType = paramsDict["serviceType"]
      onlyFoundationOutput = False
      ca = controller_arm()
      ca.createDeployment(systemConfig, instance, 'serviceInstance', serviceType, onlyFoundationOutput)
      print("z done createDeployment(")
      cka.writeTheVarsFile(systemConfig, instance, "tfBackend", None, None)
      self.copyTheConfigFile(systemConfig, instance)

      #Get the variable values
      subscriptionId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'subscriptionId')
      print("subscriptionId is: ", subscriptionId)
      if (isinstance(subscriptionId, str)) and (len(subscriptionId)==0):
        print("switch")
        subscriptionId = cfp.getFirstLevelValue(yaml_global_config_file_and_path, 'subscriptionId')
        print("subscriptionId is: ", subscriptionId)

      clientId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
      print("clientId is: ", clientId)
      if (isinstance(clientId, str)) and (len(clientId)==0):
        print("switch")
        clientId = cfp.getFirstLevelValue(yaml_global_config_file_and_path, 'clientId')
        print("clientId is: ", clientId)

      clientSecret = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret')

      tenantId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
      print("tenantId is: ", tenantId)
      if (isinstance(tenantId, str)) and (len(tenantId)==0):
        print("switch")
        tenantId = cfp.getFirstLevelValue(yaml_global_config_file_and_path, 'tenantId')
        print("tenantId is: ", tenantId)

      resourceGroupName = instance.get("resourceGroupName")
      if (resourceGroupName.startswith("$config")) :
        resourceGroupName = cfp.getValueFromConfig(keyDir, resourceGroupName, "resourceGroupName")

      print('systemConfig.get("organization") is: ', systemConfig.get("organization"))
      if systemConfig.get("organization").startswith("$config"):
        if systemConfig.get("organization").count(".") == 0:
          varName = "organization"
        elif systemConfig.get("organization").count(".") == 1:
          varName = systemConfig.get("organization").split(".")[1]
        else:
          logString = "ERROR: Too many dots . in organization field of your system template."
          lw.writeLogVerbose("acm", logString)
          exit(1)
        orgName = cb.processGlobalConfig(systemConfig.get("organization"), varName, "arm", keyDir)
      else:
        orgName = (systemConfig.get("organization")).lower()

      #storageAccountName = (instance.get("instanceName")+systemConfig.get("organization")).lower()
      storageAccountName = (instance.get("instanceName")+orgName).lower()

      print("storageAccountName is: ", storageAccountName)
#      quit("...RRR@@@")

      if len(storageAccountName) > 24:
        logString = "ERROR: The storage account name "+storageAccountName+" has more than 24 characters, which exceeds the length allowed by Azure.  "
        lw.writeLogVerbose("acm", logString)
        exit(1)
      
      outputDir = cka.getOutputDir(instance.get("instanceName"))
      keysFile = outputDir + "keys.yaml"

      #Login to az cli
      #### #The following command gets the client logged in and able to operate on azure repositories.
      cr = command_runner()
      myCmd = "az login --service-principal -u " + clientId + " -p " + clientSecret + " --tenant " + tenantId
      logString = "myCmd is: "+"az login --service-principal -u *** -p *** --tenant ***"
      lw.writeLogVerbose("shell", logString)
      cr.getShellJsonResponse(myCmd)
      logString = "Finished running login command."
      lw.writeLogVerbose("acm", logString)

      #set subscription
      setSubscriptionCmd = 'az account set --subscription ' + subscriptionId
      logString = "setSubscriptionCmd is: az account set --subscription ***"
      lw.writeLogVerbose("shell", logString)
      cr.getShellJsonResponse(setSubscriptionCmd)
      logString = "Finished running setSubscription command."
      lw.writeLogVerbose("acm", logString)

      #Get the key to access the storage account later
      getAccountKeyCommand = "az storage account keys list --resource-group " + resourceGroupName + " --account-name " + storageAccountName + " --query [0].value -o tsv " 
      logString = "getAccountKeyCommand is: az storage account keys list --resource-group *** --account-name *** --query [0].value -o tsv " 
      lw.writeLogVerbose("acm", logString)
      accountKey = cr.getAccountKey(getAccountKeyCommand)  

      #Append keys.yaml with data required to access the storage account
      # Adding .lower() to the string declarations as a reminder that the azure portal only seems to accept lower case.  If you remove .lower() , then the containers that have camel case names like networkFoundation will NOT be created.
      storageContainerName = 'networkFoundation'.lower()
      with open(keysFile, "a+") as f:  # append mode
        f.write("storage_account_name:"+storageAccountName+"\n")
        f.write("container_name:"+storageContainerName+"\n")
        f.write("tfBackendStorageAccessKey:"+accountKey+"\n")

  #@public
  def copyTheConfigFile(self, systemConfig, instance):
    cfp = config_fileprocessor()
    cka = config_keysassembler()

    keyDir = cfp.getKeyDir(systemConfig)
    inputConfigFile = keyDir+"config.yaml"

    instName = instance.get("instanceName")
    outputDir = cka.getOutputDir(instName) 
    outputConfigFile = outputDir + "config.yaml"

    shutil.copyfile(inputConfigFile, outputConfigFile)

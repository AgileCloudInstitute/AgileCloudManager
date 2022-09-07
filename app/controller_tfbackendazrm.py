## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

from config_fileprocessor import config_fileprocessor
from config_keysassembler import config_keysassembler
from log_writer import log_writer
from command_formatter import command_formatter
from command_runner import command_runner
from controller_arm import controller_arm

class controller_tfbackendazrm:

  backendFile = ''

  def __init__(self):  
    pass

  #@public
  def createTfBackend(self, systemConfig, instance, paramsDict):
    lw = log_writer()
    cfm = command_formatter()
    cka = config_keysassembler()
    keyDir = systemConfig.get("keysDir")
    cfp = config_fileprocessor()
    keyDir = cfp.getKeyDir(systemConfig)
    yaml_keys_file_and_path = keyDir+cfm.getSlashForOS()+"keys.yaml"
    resourceGroupName = ''
    backendType = instance.get("type")
    logString = "backendType is: " + backendType
    lw.writeLogVerbose("acm", logString)
    if backendType == 'azurerm': 
      serviceType = paramsDict["serviceType"]
      onlyFoundationOutput = False
#      quit('BREAK TEST') 
      ca = controller_arm()
      ca.createDeployment(systemConfig, instance, 'serviceInstance', serviceType, onlyFoundationOutput)
      cka.writeTheVarsFile(systemConfig, instance, "tfBackend", None, None)
      #Get the variable values
      subscriptionId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'subscriptionId')
      clientId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
      clientSecret = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret')
      tenantId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
      resourceGroupName = instance.get("resourceGroupName")
      storageAccountName = (instance.get("instanceName")+systemConfig.get("organization")).lower()
      #ADD VALIDATION TO CONFIRM THAT storageAccountName IS NOT LONGER THAN 24 CHARACTERS TO PREVENT DOWNSTREAM ERROR.
      outputDir = cka.getOutputDir(instance.get("instanceName"))
      keysFile = outputDir + "keys.yaml"
      #Login to az cli
      #### #The following command gets the client logged in and able to operate on azure repositories.
      cr = command_runner()
      myCmd = "az login --service-principal -u " + clientId + " -p " + clientSecret + " --tenant " + tenantId
      cr.getShellJsonResponse(myCmd)
      logString = "Finished running login command."
      lw.writeLogVerbose("acm", logString)
      #set subscription
      setSubscriptionCmd = 'az account set --subscription ' + subscriptionId
      cr.getShellJsonResponse(setSubscriptionCmd)
      logString = "Finished running setSubscription command."
      lw.writeLogVerbose("acm", logString)
      getAccountKeyCommand = "az storage account keys list --resource-group " + resourceGroupName + " --account-name " + storageAccountName + " --query [0].value -o tsv "
      print('bbbnnn keysFile is: ', keysFile)
      logString = "getAccountKeyCommand is: "+ getAccountKeyCommand
      lw.writeLogVerbose("acm", logString)
      accountKey = cr.getAccountKey(getAccountKeyCommand)  
      #Then create the 6 storage containers within the storage account to correspond with the sections in infrastructureConfig 
      # Adding .lower() to the string declarations as a reminder that the azure portal only seems to accept lower case.  If you remove .lower() , then the containers that have camel case names like networkFoundation will NOT be created.
      storageContainerName = 'networkFoundation'.lower()
      with open(keysFile, "a+") as f:  # append mode
        f.write("storage_account_name:"+storageAccountName+"\n")
        f.write("container_name:"+storageContainerName+"\n")
        f.write("tfBackendStorageAccessKey:"+accountKey+"\n")
      print('keysFile is: ', keysFile)
      print('storage_account_name is: ', storageAccountName)
      print('accountKey is: ', accountKey)
      print('container_name is: ', storageContainerName)
#      quit("---vvv---zzz===aaa")

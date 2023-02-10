## Copyright 2023 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    
  
import json
import yaml
import sys
import time
import datetime
import os
import subprocess

from command_formatter import command_formatter
from config_fileprocessor import config_fileprocessor
from log_writer import log_writer

class controller_arm:

  foundationOutput = {}

  def __init__(self):  
    pass 

  #@public
  def createDeployment(self, systemConfig, instance, caller, serviceType, onlyFoundationOutput):
    import config_cliprocessor
    cf = command_formatter()
    lw = log_writer()
    outputDict = {}
    ## STEP 1: Populate variables
    cfp = config_fileprocessor()
    keyDir = cfp.getKeyDir(systemConfig)
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    yaml_keys_file_and_path = cf.getKeyFileAndPath(keyDir)
    yaml_global_config_file_and_path = cf.getConfigFileAndPath(keyDir)

    resourceGroupName = instance.get("resourceGroupName")
    if (resourceGroupName.startswith("$config")) :
      resourceGroupName = cfp.getValueFromConfig(keyDir, resourceGroupName, "resourceGroupName")

    resourceGroupRegion = instance.get("resourceGroupRegion")
    if resourceGroupRegion.startswith("$config"):
      resourceGroupRegion = cfp.getValueFromConfig(keyDir, resourceGroupRegion, "resourceGroupRegion")

    if caller == 'networkFoundation':
      typeParent = caller
      serviceType = 'networkFoundation'
      templateName = instance.get("templateName")
      deploymentName = instance.get("deploymentName")
      if deploymentName.startswith("$config"):
        deploymentName = cfp.getValueFromConfig(keyDir, deploymentName, "deploymentName")
    elif caller == 'serviceInstance':
      typeParent = 'systems'
      templateName = instance.get("templateName")
      deploymentName = instance.get("deploymentName")
      if deploymentName.startswith("$config"):
        deploymentName = cfp.getValueFromConfig(keyDir, deploymentName, "deploymentName")
      outputDict['typeParent'] = typeParent
      if "foundation" in systemConfig.keys():
        foundationResourceGroupName = systemConfig.get("foundation").get("resourceGroupName")
        if (foundationResourceGroupName.startswith("$config")) :
          foundationResourceGroupName = cfp.getValueFromConfig(keyDir, foundationResourceGroupName, "resourceGroupName")
        foundationDeploymentName = systemConfig.get("foundation").get("deploymentName")
        if foundationDeploymentName.startswith("$config"):
          foundationDeploymentName = cfp.getValueFromConfig(keyDir, foundationDeploymentName, "deploymentName")
        outputDict['resourceGroupName'] = foundationResourceGroupName
        outputDict['deploymentName'] = foundationDeploymentName
    subscriptionId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'subscriptionId')
    if (isinstance(subscriptionId, str)) and (len(subscriptionId)==0):
      subscriptionId = cfp.getFirstLevelValue(yaml_global_config_file_and_path, 'subscriptionId')

    clientId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
    if (isinstance(clientId, str)) and (len(clientId)==0):
      clientId = cfp.getFirstLevelValue(yaml_global_config_file_and_path, 'clientId')

    clientSecret = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret')

    tenantId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
    if (isinstance(tenantId, str)) and (len(tenantId)==0):
      tenantId = cfp.getFirstLevelValue(yaml_global_config_file_and_path, 'tenantId')

    ## STEP 2: Login to az cli and set subscription
    self.loginToAzAndSetSubscription(clientId, clientSecret,tenantId,subscriptionId)
    ## STEP 3: Create Resource Group 
    resourceGroupCmd = 'az group create --name ' + resourceGroupName + ' --location ' + resourceGroupRegion
    logString = 'resourceGroupCmd is: az group create --name *** --location ' + resourceGroupRegion
    lw.writeLogVerbose("az-cli", logString)
    self.getShellJsonResponse(resourceGroupCmd)
    logString = "Finished running create resource group command. "
    lw.writeLogVerbose("az-cli", logString)
    ## STEP 4: Get template and config variable mapping file
    templatePathAndFile = userCallingDir + templateName
    templatePathAndFile = cf.formatPathForOS(templatePathAndFile)
    templateName = self.getArmTemplateName(templateName, userCallingDir)
    templateName = cf.formatPathForOS(templateName)
    ## STEP 5: Assemble and run command to deploy ARM template
    self.assembleAndRunArmDeploymentCommand(systemConfig, serviceType, instance, templatePathAndFile, resourceGroupName, deploymentName, outputDict, onlyFoundationOutput)
    if not onlyFoundationOutput:
      ## STEP 6: If foundation, then create and deploy images, if images are present in config file
      if caller == 'networkFoundation':
        if "images" in instance.keys():
          self.configureAzureToDeployImages(templatePathAndFile)
          for imageInstance in instance.get("images"):
            templateName = imageInstance.get("templateName")
            deploymentName = imageInstance.get("deploymentName")
            if deploymentName.startswith("$config"):
              deploymentName = cfp.getValueFromConfig(keyDir, deploymentName, "deploymentName")
            ## STEP 4: Get template and config variable mapping file
            templatePathAndFile = userCallingDir + templateName
            templatePathAndFile = cf.formatPathForOS(templatePathAndFile)
            templateName = self.getArmTemplateName(templateName, userCallingDir)
            self.createImageTemplateAndDeployImage(systemConfig, serviceType, imageInstance, templatePathAndFile, deploymentName, subscriptionId, clientId)
        else:
          logString = "WARNING: This network foundation does not have any image builds associated with it.  If you intend not to build images in this network, then everything is fine.  But if you do want to build images with this network, then check your configuration and re-run this command.  "
          lw.writeLogVerbose("acm", logString)

  #@public
  def destroyDeployment(self, systemConfig, instance, caller):
    import config_cliprocessor
    cf = command_formatter()
    lw = log_writer()
    ## STEP 1: Populate variables
    cfp = config_fileprocessor()
    keyDir = cfp.getKeyDir(systemConfig)
    yaml_keys_file_and_path = cf.getKeyFileAndPath(keyDir) 
    yaml_global_config_file_and_path = cf.getConfigFileAndPath(keyDir)
    if (caller == 'networkFoundation') or (caller == 'serviceInstance'):
      resourceGroupName = instance.get('resourceGroupName')
      if (resourceGroupName.startswith("$config")) :
        resourceGroupName = cfp.getValueFromConfig(keyDir, resourceGroupName, "resourceGroupName")

      templateName = instance.get('emptyTemplateName')
      deploymentName = instance.get('deploymentName')
      if deploymentName.startswith("$config"):
        deploymentName = cfp.getValueFromConfig(keyDir, deploymentName, "deploymentName")

    subscriptionId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'subscriptionId')
    if (isinstance(subscriptionId, str)) and (len(subscriptionId)==0):
      subscriptionId = cfp.getFirstLevelValue(yaml_global_config_file_and_path, 'subscriptionId')

    clientId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
    clientId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
    if (isinstance(clientId, str)) and (len(clientId)==0):
      clientId = cfp.getFirstLevelValue(yaml_global_config_file_and_path, 'clientId')

    clientSecret = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret')
    tenantId = cfp.getFirstLevelValue(yaml_global_config_file_and_path, 'tenantId')

    if (isinstance(tenantId, str)) and (len(tenantId)==0):
      tenantId = cfp.getFirstLevelValue(yaml_global_config_file_and_path, 'tenantId')

    ## STEP 2: Login to az cli and set subscription
    self.loginToAzAndSetSubscription(clientId, clientSecret,tenantId,subscriptionId)
    resourceGroupCheckCmd = 'az group exists -n '+resourceGroupName
    logString = "resourceGroupCheckCmd is: az group exists -n *** "
    lw.writeLogVerbose("az-cli", logString)
    jsonStatus = self.getShellJsonResponse(resourceGroupCheckCmd)
    if ("false" in str(jsonStatus)) and (len(str(jsonStatus))==6):
      logString = "Resource Group named *** does not exist.  Therefore, we are skipping this destroy ARM template command based on the assumption that any in-scope resources were destroyed when the resource group was destroyed. Please make sure that the in-scope resources do not exist.  And please examine your workflow to understand how you reached this message. "
      lw.writeLogVerbose("az-cli", logString)
      return
    else:
      ## STEP 3: Get template and config variable mapping file
      templatePathAndFile = config_cliprocessor.inputVars.get('userCallingDir') + templateName
      templatePathAndFile = cf.formatPathForOS(templatePathAndFile)
      ## STEP 4: delete deployment
      destroyCmd = 'az deployment group create --name '+deploymentName+' --resource-group '+resourceGroupName+' --template-file '+templatePathAndFile+' --verbose '+' --mode complete'
      #logString = 'destroyCmd is: '+ 'az deployment group create --name *** --resource-group *** --template-file '+templatePathAndFile+' --verbose '+' --mode complete'
      logString = 'destroyCmd is: '+ destroyCmd
      lw.writeLogVerbose("az-cli", logString) 
      jsonStatus = self.getShellJsonResponse(destroyCmd)
      jsonStatus = json.loads(jsonStatus)
      state = jsonStatus['properties']['provisioningState']
      logString = 'provisioningState is: '+ state
      lw.writeLogVerbose("az-cli", logString)
      if state == 'Succeeded':
        logString = "Finished running deployment command in destroyDeployment()."
        lw.writeLogVerbose("az-cli", logString)
      else:
        logString = "ERROR: provisioningState for the deployment is NOT Succeeded. "
        lw.writeLogVerbose("az-cli", logString)
      #STEP 5: Now destroy the resource group
      destroyRgCpmmand = 'az group delete -y --name '+resourceGroupName
      logString = 'destroyRgCpmmand is: az group delete -y --name ***'
      lw.writeLogVerbose("az-cli", logString)
      jsonStatus = self.getShellJsonResponse(destroyRgCpmmand)

  #@private
  def configureAzureToDeployImages(self, templatePathAndFile):
    with open(templatePathAndFile, 'r') as f:
        data = json.load(f)
    resources = data['resources']
    for resource in resources:  
      if resource['type'] == 'Microsoft.VirtualMachineImages/imageTemplates':
        registerProviderVmiCmd = 'az provider register -n Microsoft.VirtualMachineImages'
        self.getShellJsonResponse(registerProviderVmiCmd)
        time.sleep(10)
        registerVmiCmd = 'az feature register --namespace Microsoft.VirtualMachineImages --name VirtualMachineTemplatePreview'
        responseState = self.getRegistered(registerVmiCmd)
        showVmiCmd = 'az feature show --namespace Microsoft.VirtualMachineImages --name VirtualMachineTemplatePreview'
        responseState = self.getRegistered(showVmiCmd)
        vmiCheck = self.checkRegistrationState('az provider show -n Microsoft.VirtualMachineImages -o json')
        if vmiCheck != 'Registered':
          regVmiCommand = 'az provider register -n Microsoft.VirtualMachineImages'
          responseState = self.getRegistered(regVmiCommand)
        kvCheck = self.checkRegistrationState('az provider show -n Microsoft.KeyVault -o json')
        if kvCheck != 'Registered':
          regKvCommand = 'az provider register -n Microsoft.Compute'
          responseState = self.getRegistered(regKvCommand)
        compCheck = self.checkRegistrationState('az provider show -n Microsoft.Compute -o json')
        if compCheck != 'Registered':
          regCompCommand ='az provider register -n Microsoft.KeyVault'
          responseState = self.getRegistered(regCompCommand)
        storageCheck = self.checkRegistrationState('az provider show -n Microsoft.Storage -o json')
        if storageCheck != 'Registered':
          regStorageCommand = 'az provider register -n Microsoft.Storage'
          responseState = self.getRegistered(regStorageCommand)
        networkCheck = self.checkRegistrationState('az provider show -n Microsoft.Network -o json')
        if networkCheck != 'Registered':
          regNetworkCommand = 'az provider register -n Microsoft.Network'
          responseState = self.getRegistered(regNetworkCommand)

  #@private
  def createImageTemplateAndDeployImage(self, systemConfig, serviceType, instance, templatePathAndFile, deploymentName, subscriptionId, clientId):
    lw = log_writer()
    import config_cliprocessor
    resourceGroupName = instance.get('resourceGroupName')
    if (resourceGroupName.startswith("$config")) :
      cfp = config_fileprocessor()
      keyDir = cfp.getKeyDir(systemConfig)
      resourceGroupName = cfp.getValueFromConfig(keyDir, resourceGroupName, "resourceGroupName")
    # create user assigned identity for image builder to access the storage account where the script is located
    dateTimeCode = str(datetime.datetime.now()).replace(' ','').replace('-','').replace(':','').replace('.','')
    identityName = 'imgbuilder_'+dateTimeCode
    idCreateCommand = 'az identity create -g ' +resourceGroupName+ ' -n ' +identityName
    logString = 'idCreateCommand is: az identity create -g *** -n ***'
    lw.writeLogVerbose("az-cli", logString)
    jsonResponse = self.getShellJsonResponse(idCreateCommand)
    jsonResponse = json.loads(jsonResponse)
    msiFullId = jsonResponse['id']
    servicePrincipalId = jsonResponse['principalId']
    #Create a role definition for the image builder
    imageRoleDefinitionName = "imagebuilder_"+dateTimeCode
    rolesDict = {
      "Name": imageRoleDefinitionName,
      "IsCustom": True,
      "Description": "Image Builder access to create resources for the image build",
      "Actions": [ "Microsoft.Compute/galleries/read", "Microsoft.Compute/galleries/images/read", "Microsoft.Compute/galleries/images/versions/read", "Microsoft.Compute/galleries/images/versions/write", "Microsoft.Compute/images/write", "Microsoft.Compute/images/read", "Microsoft.Compute/images/delete" ],
      "NotActions": [],
      "AssignableScopes": [ "/subscriptions/"+subscriptionId+"/resourceGroups/"+resourceGroupName ]
    }
    with open('ad-role.json', 'w', encoding='utf-8') as f:
      json.dump(rolesDict, f, ensure_ascii=False, indent=4)
    roleDefCreateCommand = 'az role definition create --subscription '+subscriptionId+' --role-definition @ad-role.json'
    logString = 'roleDefCreateCommand is: az role definition create --subscription *** --role-definition @ad-role.json'
    lw.writeLogVerbose("az-cli", logString)
    jsonResponse = self.getShellJsonResponse(roleDefCreateCommand)
    #Grant the role definition to the managed service identity
    imageRoleAssignmentCommand = 'az role assignment create --role '+imageRoleDefinitionName+' --scope /subscriptions/'+subscriptionId+'/resourceGroups/'+resourceGroupName+' --assignee-object-id '+servicePrincipalId+' --assignee-principal-type ServicePrincipal'
    logString = 'imageRoleAssignmentCommand is: az role assignment create --role *** --scope /subscriptions/***/resourceGroups/*** --assignee-object-id *** --assignee-principal-type ServicePrincipal'
    lw.writeLogVerbose("az-cli", logString)
    jsonResponse = self.getShellJsonResponse(imageRoleAssignmentCommand)
    imageRoleAssignmentCommand = 'az role assignment create --role '+imageRoleDefinitionName+' --scope /subscriptions/'+subscriptionId+'/resourceGroups/'+resourceGroupName+' --assignee-object-id '+clientId+' --assignee-principal-type ServicePrincipal'
    logString = 'imageRoleAssignmentCommand is: az role assignment create --role *** --scope /subscriptions/***/resourceGroups/*** --assignee-object-id *** --assignee-principal-type ServicePrincipal'
    lw.writeLogVerbose("az-cli", logString)
    jsonResponse = self.getShellJsonResponse(imageRoleAssignmentCommand)
    outputDict = {}
    outputDict['identityName'] = identityName
    outputDict['subscriptionId'] = subscriptionId
    outputDict['resourceGroupName'] = resourceGroupName
    outputDict['hasImageBuilds'] = True
    outputDict['dateTimeCode'] = dateTimeCode
    self.assembleAndRunArmDeploymentCommand(systemConfig, serviceType, instance, templatePathAndFile, resourceGroupName, deploymentName, outputDict, False)
    imageTemplateNameRoot = instance.get('imageName')
    if (imageTemplateNameRoot.startswith("$config")) :
      cfp = config_fileprocessor()
      keyDir = cfp.getKeyDir(systemConfig)
      imageTemplateNameRoot = cfp.getValueFromConfig(keyDir, imageTemplateNameRoot, "imageName")
    imageTemplateNameRoot = imageTemplateNameRoot+"_t_" 
    getImageTemplatesCmd = "az graph query -q \"Resources | where type =~ 'Microsoft.VirtualMachineImages/imageTemplates' and resourceGroup =~ '"+resourceGroupName+"' | project name, resourceGroup | sort by name asc\""
    logString = "getImageTemplatesCmd is: az graph query -q \"Resources | where type =~ 'Microsoft.VirtualMachineImages/imageTemplates' and resourceGroup =~ '***' | project name, resourceGroup | sort by name asc\""
    lw.writeLogVerbose("az-cli", logString)
    imgTemplatesJSON = self.getImageListShellJsonResponse(getImageTemplatesCmd, imageTemplateNameRoot)
    imageTemplateNamesList = []
    imgTemplatesJSON = yaml.safe_load(imgTemplatesJSON)  
    for imageTemplate in imgTemplatesJSON['data']:
      if imageTemplateNameRoot in imageTemplate['name']:
        imageTemplateNamesList.append(imageTemplate.get("name"))
    sortedImageTemplateList = list(sorted(imageTemplateNamesList))
    print('sortedImageTemplateList is: ', str(sortedImageTemplateList))
    print("len(sortedImageTemplateList) is: ", str(len(sortedImageTemplateList)))
    newestTemplateName = sortedImageTemplateList[-1]
    #Build the image from the template you just created.  
    buildImageCommand = 'az resource invoke-action --resource-group '+resourceGroupName+' --resource-type  Microsoft.VirtualMachineImages/imageTemplates -n '+newestTemplateName+' --action Run '
    logString = "buildImageCommand is: "+'az resource invoke-action --resource-group *** --resource-type  Microsoft.VirtualMachineImages/imageTemplates -n '+newestTemplateName+' --action Run '
    lw = log_writer()
    lw.writeLogVerbose("acm", logString)
    jsonResponse = self.getShellBuildImageResponse(buildImageCommand)
    roleFile = config_cliprocessor.inputVars.get('userCallingDir') + 'ad-role.json'
    try:
      os.remove(roleFile)
    except OSError:
      pass

  #@private
  def getRegistered(self, theCmd, counter=0):
    lw = log_writer()
    theState = 'NA'
    if (theState != 'Registered') and (counter <20):
      jsonStatus = self.getShellJsonResponse(theCmd)
      jsonStatus = json.loads(jsonStatus)
      theState = jsonStatus['properties']['state']
      logString = 'Attempt number ' + str(counter) + ' got response: ' + theState + ' from running command: '+theCmd
      lw.writeLogVerbose('acm', logString)
      registerProviderVmiCmd = 'az provider register -n Microsoft.VirtualMachineImages'
      self.getShellJsonResponse(registerProviderVmiCmd)
      if theState != 'Registered':
        counter +=1
        time.sleep(10)
        self.getRegistered(theCmd, counter)
    return theState

  #@private
  def checkRegistrationState(self, checkCmd):
    jsonStatus = json.loads(self.getShellJsonResponse(checkCmd))
    regState = jsonStatus['registrationState']
    return regState

  #@private
  def getArmTemplateName(self, templateName, userCallingDir):
    cf = command_formatter()
    lw = log_writer()
    templateName = userCallingDir+cf.getSlashForOS()+templateName
    templateName = cf.formatPathForOS(templateName)
    if os.path.isfile(templateName):
      pass
    else:  
      print('templateName is: ', templateName)
      logString = "Template name is not valid.  "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    return templateName

  #@private
  def assembleAndRunArmDeploymentCommand(self, systemConfig, serviceType, instance, templatePathAndFile, resourceGroupName, deploymentName, outputDict, onlyFoundationOutput):
    lw = log_writer()
    ## STEP 5: Assemble deployment command
    from command_builder import command_builder
    cb = command_builder()  
    deployVarsFragment = cb.getVarsFragment(systemConfig, serviceType, instance, None, 'arm', self, outputDict) 
    deployCmd = 'az deployment group create --name '+deploymentName+' --resource-group '+resourceGroupName+' --template-file '+templatePathAndFile+' --verbose '+deployVarsFragment
    logString = '--- deployCmd is: '+deployCmd
    lw.writeLogVerbose("az-cli", logString)
    ## STEP 6: Run Deployment command and check results
    jsonStatus = self.getShellJsonResponse(deployCmd)
    jsonStatus = json.loads(jsonStatus)
    state = jsonStatus['properties']['provisioningState']
    logString = 'provisioningState is: '+ state
    lw.writeLogVerbose("az-cli", logString)
    if serviceType == 'networkFoundation':
      outputs = jsonStatus['properties']['outputs']
      self.foundationOutput = outputs
    if state == 'Succeeded':
      logString = "Finished running deployment command in assembleAndRunArmDeploymentCommand()."
      lw.writeLogVerbose("az-cli", logString)
    else:
      logString = "ERROR: provisioningState for the deployment is NOT Succeeded. "
      lw.writeLogVerbose("az-cli", logString)

  #@private
  def loginToAzAndSetSubscription(self, clientId, clientSecret,tenantId,subscriptionId):
    lw = log_writer()
    #### #The following command gets the client logged in and able to operate on azure repositories.
    loginCmd = "az login --service-principal -u " + clientId + " -p " + clientSecret + " --tenant " + tenantId
    logString = "loginCmd is: az login --service-principal -u *** -p *** --tenant ***"
    lw.writeLogVerbose('az-cli', logString)
    self.getShellJsonResponse(loginCmd)
    logString = "Finished running login command."
    lw.writeLogVerbose("az-cli", logString)
    setSubscriptionCommand = 'az account set --subscription '+subscriptionId
    logString = 'setSubscriptionCommand is: az account set --subscription ***'
    lw.writeLogVerbose("az-cli", logString)
    self.getShellJsonResponse(setSubscriptionCommand)
    logString = 'Finished setting subscription to ***'
    lw.writeLogVerbose("az-cli", logString)

  #@private
  def getShellJsonResponse(self, cmd,counter=0):
    lw = log_writer()
    process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
    data = process.stdout
    err = process.stderr
    logString = "data string is: " + data
    lw.writeLogVerbose("acm", logString)
    logString = "err is: " + str(err)
    lw.writeLogVerbose("acm", logString)
    logString = "process.returncode is: " + str(process.returncode)
    lw.writeLogVerbose("acm", logString)
    #These next 6 lines added to help diagnose azure latency problem with empty results and exit code 0
    logString = "type(data) is: "+str(type(data))
    lw.writeLogVerbose("acm", logString)
    logString = "type(list(data)) is: "+str(type(list(data)))
    lw.writeLogVerbose("acm", logString)
    logString = "len(list(data)) is: "+ str(len(list(data)))
    lw.writeLogVerbose("acm", logString)
    if process.returncode == 0:
      #These next 20 lines added to help diagnose and handle azure latency problem with empty results and exit code 0
      if ("az resource list --resource-group" in cmd) and ("--resource-type Microsoft.Compute/images" in cmd) and (len(str(data).replace(" ","")) == 3):
        if counter < 31:
          logString = "Sleeping 30 seconds before running the command a second time in case a latency problem caused the attempt to fail. "
          lw.writeLogVerbose('acm', logString)
          counter +=1 
          logString = "Attempt "+str(counter)+ " out of 30. "
          lw.writeLogVerbose('acm', logString)
          import time
          time.sleep(30)
          data = self.getShellJsonResponse(cmd,counter)
          return data
        else:  
          logString = "Error: " + str(err)
          lw.writeLogVerbose("shell", logString)
          logString = "Error: Return Code is: " + str(process.returncode)
          lw.writeLogVerbose("shell", logString)
          logString = "ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
      else:
        logString = str(data)
        lw.writeLogVerbose("shell", logString)
        decodedData = data
        return decodedData
    else:
      if counter < 31:
        logString = "Sleeping 30 seconds before running the command another time in case a latency problem caused the attempt to fail. "
        lw.writeLogVerbose('acm', logString)
        counter +=1 
        logString = "Attempt "+str(counter)+ " out of 30. "
        lw.writeLogVerbose('acm', logString)
        import time
        time.sleep(30)
        data = self.getShellJsonResponse(cmd,counter)
        return data
      else:  
        if "(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found." in str(err):
          logString = "WARNING: "+"(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found."
          lw.writeLogVerbose('shell', logString)
          logString = "Continuing because this error message is often benign.  If you encounter downstream problems resulting from this, please report your use case so that we can examine the cause. "
          lw.writeLogVerbose('acm', logString)
          return decodedData
        else:
          logString = "Error: " + str(err)
          lw.writeLogVerbose("shell", logString)
          logString = "Error: Return Code is: " + str(process.returncode)
          lw.writeLogVerbose("shell", logString)
          logString = "ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)

  #@public
  def getImageListShellJsonResponse(self, cmd, imageNameRoot, counter=0):
    lw = log_writer()
    process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
    data = process.stdout
    err = process.stderr
    logString = "data string is: " + data
    lw.writeLogVerbose("acm", logString)
    logString = "err is: " + str(err)
    lw.writeLogVerbose("acm", logString)
    logString = "process.returncode is: " + str(process.returncode)
    lw.writeLogVerbose("acm", logString)
    
    #These next 6 lines added to help diagnose and handle azure latency problem with empty results and exit code 0
    logString = "type(data) is: "+str(type(data))
    lw.writeLogVerbose("acm", logString)
    logString = "type(list(data)) is: "+str(type(list(data)))
    lw.writeLogVerbose("acm", logString)
    logString = "str(data).replace(" ","") is: "+str(data).replace(" ","")
    lw.writeLogVerbose("acm", logString)
    logString = "len(str(data).replace(" ","")) is: "+str(len(str(data).replace(" ","")))
    lw.writeLogVerbose("acm", logString)
    logString = "counter is: "+str(counter)
    lw.writeLogVerbose("acm", logString)

    if process.returncode == 0:
      if counter < 16:
        imageNamesList = []
        imgsJSON = yaml.safe_load(data)  
        for image in imgsJSON['data']:
          if imageNameRoot in image['name']:
            imageNamesList.append(image.get("name"))
        sortedImageList = list(sorted(imageNamesList))
        logString = "List of matching images found so far is: " + str(sortedImageList)
        lw.writeLogVerbose("acm", logString)
        if len(sortedImageList) >0:
          return data
        else:
          logString = "Sleeping 30 seconds before running the command a second time in case a latency problem is causing a delay in image creation. "
          lw.writeLogVerbose('acm', logString)
          counter +=1 
          logString = "Attempt "+str(counter)+ " out of 15. "
          lw.writeLogVerbose('acm', logString)
          import time
          time.sleep(30)
          data = self.getImageListShellJsonResponse(cmd, imageNameRoot, counter)
          return data
      else:  
        logString = "Error: " + str(err)
        lw.writeLogVerbose("shell", logString)
        logString = "Error: Return Code is: " + str(process.returncode)
        lw.writeLogVerbose("shell", logString)
        logString = "ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem."
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    else:
      if counter < 16:
        logString = "Sleeping 30 seconds before running the command a second time in case a latency problem caused the attempt to fail. "
        lw.writeLogVerbose('acm', logString)
        counter +=1 
        logString = "Attempt "+str(counter)+ " out of 15. "
        lw.writeLogVerbose('acm', logString)
        import time
        time.sleep(30)
        data = self.getImageListShellJsonResponse(cmd, imageNameRoot, counter)
        return data 
      else:   
        if "(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found." in str(err):
          logString = "WARNING: "+"(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found."
          lw.writeLogVerbose('shell')
          logString = "Continuing because this error message is often benign.  If you encounter downstream problems resulting from this, please report your use case so that we can examine the cause. "
          lw.writeLogVerbose('acm', logString)
          return data
        else:
          logString = "Error: " + str(err)
          lw.writeLogVerbose("shell", logString)
          logString = "Error: Return Code is: " + str(process.returncode)
          lw.writeLogVerbose("shell", logString)
          logString = "ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)

  #@private
  def getShellBuildImageResponse(self, cmd,counter=0):
    lw = log_writer()
    process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
    data = process.stdout
    err = process.stderr
    logString = "data string is: " + data
    lw.writeLogVerbose("acm", logString)
    logString = "err is: " + str(err)
    lw.writeLogVerbose("acm", logString)
    logString = "process.returncode is: " + str(process.returncode)
    lw.writeLogVerbose("acm", logString)
    #These next 6 lines added to help diagnose azure latency problem with empty results and exit code 0
    logString = "type(data) is: "+str(type(data))
    lw.writeLogVerbose("acm", logString)
    logString = "type(list(data)) is: "+str(type(list(data)))
    lw.writeLogVerbose("acm", logString)
    logString = "len(list(data)) is: "+ str(len(list(data)))
    lw.writeLogVerbose("acm", logString)
    if process.returncode == 0:
      logString = str(data)
      lw.writeLogVerbose("shell", logString)
      decodedData = data
      return decodedData
    else:
      if counter < 51:
        logString = "Sleeping 30 seconds before running the command another time in case a latency problem caused the attempt to fail. "
        lw.writeLogVerbose('acm', logString)
        counter +=1 
        logString = "Attempt "+str(counter)+ " out of 50. "
        lw.writeLogVerbose('acm', logString)
        import time
        time.sleep(30)
        data = self.getShellBuildImageResponse(cmd,counter)
        return data
      else:  
        if "(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found." in str(err):
          logString = "WARNING: "+"(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found."
          lw.writeLogVerbose('shell', logString)
          logString = "Continuing because this error message is often benign.  If you encounter downstream problems resulting from this, please report your use case so that we can examine the cause. "
          lw.writeLogVerbose('acm', logString)
          return decodedData
        else:
          logString = "Error: " + str(err)
          lw.writeLogVerbose("shell", logString)
          logString = "Error: Return Code is: " + str(process.returncode)
          lw.writeLogVerbose("shell", logString)
          logString = "ERROR: Failed to return Json response from invocation of `az resource invoke-action` command.  Halting the program so that you can debug the cause of the problem."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)

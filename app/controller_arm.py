## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    
  
import json
import yaml
import sys
import time
import datetime
import os
import subprocess

from command_formatter import command_formatter
from config_fileprocessor import config_fileprocessor
import config_cliprocessor
from log_writer import log_writer

class controller_arm:

  foundationOutput = {}

  def __init__(self):  
    pass
 
  #@public
  def createDeployment(self, systemConfig, instance, caller, serviceType, onlyFoundationOutput):
    cf = command_formatter()
    lw = log_writer()
    outputDict = {}
    ## STEP 1: Populate variables
    cfp = config_fileprocessor()
    keyDir = cfp.getKeyDir(systemConfig)
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    yaml_keys_file_and_path = cf.getKeyFileAndPath(keyDir)
    print("keyDir is: ", keyDir)
    print("userCallingDir is: ", userCallingDir)
    print("yaml_keys_file_and_path is: ", yaml_keys_file_and_path)
#    quit('<---c--->')
    if caller == 'networkFoundation':
      typeParent = caller
      serviceType = 'networkFoundation'
      resourceGroupName = instance.get("resourceGroupName")
      resourceGroupRegion = instance.get("resourceGroupRegion")
      templateName = instance.get("templateName")
      deploymentName = instance.get("deploymentName")
    elif caller == 'serviceInstance':
      typeParent = 'systems'
      resourceGroupName = instance.get("resourceGroupName")
      resourceGroupRegion = instance.get("resourceGroupRegion")
      templateName = instance.get("templateName")
      deploymentName = instance.get("deploymentName")
      outputDict['typeParent'] = typeParent
      if "foundation" in systemConfig.keys():
        foundationResourceGroupName = systemConfig.get("foundation").get("resourceGroupName")
        foundationDeploymentName = systemConfig.get("foundation").get("deploymentName")
        outputDict['resourceGroupName'] = foundationResourceGroupName
        outputDict['deploymentName'] = foundationDeploymentName
    subscriptionId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'subscriptionId')
    clientId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
    clientSecret = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret')
    tenantId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
    ## STEP 2: Login to az cli and set subscription
    self.loginToAzAndSetSubscription(clientId, clientSecret,tenantId,subscriptionId)
    ## STEP 3: Create Resource Group
    resourceGroupCmd = 'az group create --name ' + resourceGroupName + ' --location ' + resourceGroupRegion
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
    cf = command_formatter()
    lw = log_writer()
    ## STEP 1: Populate variables
    cfp = config_fileprocessor()
    keyDir = cfp.getKeyDir(systemConfig)
    yaml_keys_file_and_path = cf.getKeyFileAndPath(keyDir)
    if caller == 'networkFoundation':
      resourceGroupName = instance.get('resourceGroupName')
      templateName = instance.get('emptyTemplateName')
      deploymentName = instance.get('deploymentName')
    elif caller == 'serviceInstance':
      resourceGroupName = instance.get("resourceGroupName")
      templateName = instance.get("emptyTemplateName")
      deploymentName = instance.get("deploymentName")
    subscriptionId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'subscriptionId')
    clientId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
    clientSecret = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret')
    tenantId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
#start test move from above step 3 below
    ## STEP 2: Login to az cli and set subscription
    self.loginToAzAndSetSubscription(clientId, clientSecret,tenantId,subscriptionId)
#end test move from above step 3 below
    resourceGroupCheckCmd = 'az group exists -n '+resourceGroupName
    logString = "resourceGroupCheckCmd is: "+resourceGroupCheckCmd
    lw.writeLogVerbose("az-cli", logString)
    jsonStatus = self.getShellJsonResponse(resourceGroupCheckCmd)
    if ("false" in str(jsonStatus)) and (len(str(jsonStatus))==6):
      logString = "Resource Group named "+resourceGroupName+" does not exist.  Therefore, we are skipping this destroy ARM template command based on the assumption that any in-scope resources were destroyed when the resource group was destroyed. Please make sure that the in-scope resources do not exist.  And please examine your workflow to understand how you reached this message. "
      lw.writeLogVerbose("az-cli", logString)
      return
    else:
      ## STEP 3: Get template and config variable mapping file
      templatePathAndFile = config_cliprocessor.inputVars.get('userCallingDir') + templateName
      templatePathAndFile = cf.formatPathForOS(templatePathAndFile)
      ## STEP 4: delete deployment
      destroyCmd = 'az deployment group create --name '+deploymentName+' --resource-group '+resourceGroupName+' --template-file '+templatePathAndFile+' --verbose '+' --mode complete'
      logString = 'destroyCmd is: '+ destroyCmd
      lw.writeLogVerbose("az-cli", logString)
      jsonStatus = self.getShellJsonResponse(destroyCmd)
      jsonStatus = json.loads(jsonStatus)
      state = jsonStatus['properties']['provisioningState']
      logString = 'provisioningState is: '+ state
      lw.writeLogVerbose("az-cli", logString)
      if state == 'Succeeded':
        logString = "Finished running deployment command."
        lw.writeLogVerbose("az-cli", logString)
      else:
        logString = "ERROR: provisioningState for the deployment is NOT Succeeded. "
        lw.writeLogVerbose("az-cli", logString)
      #STEP 5: Now destroy the resource group
      destroyRgCpmmand = 'az group delete -y --name '+resourceGroupName
      logString = 'destroyRgCpmmand is: '+ destroyRgCpmmand
      lw.writeLogVerbose("az-cli", logString)
      jsonStatus = self.getShellJsonResponse(destroyRgCpmmand)

  #@private
  def configureAzureToDeployImages(self, templatePathAndFile):
    with open(templatePathAndFile, 'r') as f:
        data = json.load(f)
#    data = json.load(open(templatePathAndFile, 'r'))
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
    resourceGroupName = instance.get('resourceGroupName')
    # create user assigned identity for image builder to access the storage account where the script is located
    dateTimeCode = str(datetime.datetime.now()).replace(' ','').replace('-','').replace(':','').replace('.','')
    identityName = 'imgbuilder_'+dateTimeCode
    idCreateCommand = 'az identity create -g ' +resourceGroupName+ ' -n ' +identityName
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
    jsonResponse = self.getShellJsonResponse(roleDefCreateCommand)
    #Grant the role definition to the managed service identity
    imageRoleAssignmentCommand = 'az role assignment create --assignee '+msiFullId+' --role '+imageRoleDefinitionName+' --scope /subscriptions/'+subscriptionId+'/resourceGroups/'+resourceGroupName
    imageRoleAssignmentCommand = 'az role assignment create --role '+imageRoleDefinitionName+' --scope /subscriptions/'+subscriptionId+'/resourceGroups/'+resourceGroupName+' --assignee-object-id '+servicePrincipalId+' --assignee-principal-type ServicePrincipal'
    jsonResponse = self.getShellJsonResponse(imageRoleAssignmentCommand)
    imageRoleAssignmentCommand = 'az role assignment create --role '+imageRoleDefinitionName+' --scope /subscriptions/'+subscriptionId+'/resourceGroups/'+resourceGroupName+' --assignee-object-id '+clientId+' --assignee-principal-type ServicePrincipal'
    jsonResponse = self.getShellJsonResponse(imageRoleAssignmentCommand)
    outputDict = {}
    outputDict['identityName'] = identityName
    outputDict['subscriptionId'] = subscriptionId
    outputDict['resourceGroupName'] = resourceGroupName
    outputDict['hasImageBuilds'] = True
    outputDict['dateTimeCode'] = dateTimeCode
    self.assembleAndRunArmDeploymentCommand(systemConfig, serviceType, instance, templatePathAndFile, resourceGroupName, deploymentName, outputDict, False)
    imageTemplateNameRoot = instance.get('instanceName')
    getImageTemplatesCmd = 'az resource list --resource-group '+resourceGroupName+' --resource-type Microsoft.VirtualMachineImages/imageTemplates '
    imgTemplatesJSON = self.getShellJsonResponse(getImageTemplatesCmd)
    print('str(imgTemplatesJSON) is: ', imgTemplatesJSON)
    imageTemplateNamesList = []
    imgTemplatesJSON = yaml.safe_load(imgTemplatesJSON)  
    for imageTemplate in imgTemplatesJSON:
      print('-------------------------------------------------------')
      print("imageTemplate is: ", imageTemplate)
      print('imageTemplateNameRoot is: ', imageTemplateNameRoot)
      if imageTemplateNameRoot in imageTemplate['name']:
        imageTemplateNamesList.append(imageTemplate.get("name"))
    sortedImageTemplateList = list(sorted(imageTemplateNamesList))
#    print('sortedImageTemplateList is: ', str(sortedImageTemplateList))    
#    quit('chimp!')
    newestTemplateName = sortedImageTemplateList[-1]
    #Build the image from the template you just created.  
    buildImageCommand = 'az resource invoke-action --resource-group '+resourceGroupName+' --resource-type  Microsoft.VirtualMachineImages/imageTemplates -n '+newestTemplateName+' --action Run '
    jsonResponse = self.getShellJsonResponse(buildImageCommand)
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
      registerProviderVmiCmd = 'az provider register -n Microsoft.VirtualMachineImages' # --name VirtualMachineTemplatePreview'
      self.getShellJsonResponse(registerProviderVmiCmd)
      if theState != 'Registered':
        counter +=1
        time.sleep(10)
        self.getRegistered(theCmd, counter)
    return theState

  #@private
  def getUnRegistered(self, theCmd, counter=0):
    lw = log_writer()
    theState = 'NA'
    if (theState != 'Unregistered') and (counter <20):
      jsonStatus = json.loads(self.getShellJsonResponse(theCmd))
      theState = jsonStatus['properties']['state']
      logString = 'Attempt number ' + str(counter) + ' got response: ' + theState + ' from running command: '+theCmd
      lw.writeLogVerbose('acm', logString)
      if theState != 'Unregistered':
        counter +=1
        time.sleep(10)
        self.getUnRegistered(theCmd, counter)
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
    print("--- deployVarsFragment is: ", deployVarsFragment)
    deployCmd = 'az deployment group create --name '+deploymentName+' --resource-group '+resourceGroupName+' --template-file '+templatePathAndFile+' --verbose '+deployVarsFragment
    logString = '--- deployCmd is: '+ deployCmd
    lw.writeLogVerbose("az-cli", logString)
    ## STEP 6: Run Deployment command and check results
    jsonStatus = self.getShellJsonResponse(deployCmd)
    print('jsonStatus is: ', jsonStatus)
    jsonStatus = json.loads(jsonStatus)
    state = jsonStatus['properties']['provisioningState']
    logString = 'provisioningState is: '+ state
    lw.writeLogVerbose("az-cli", logString)
    if serviceType == 'networkFoundation':
      outputs = jsonStatus['properties']['outputs']
      self.foundationOutput = outputs
      print('outputs is: ', str(outputs))
      for thisOutput in outputs:
        print('thisOutput is: ', str(thisOutput))
        print('outputs[thisOutput]["value"] is: ', str(outputs[thisOutput]['value']))

#    if onlyFoundationOutput:
#      quit('giraffe!')
    if state == 'Succeeded':
      logString = "Finished running deployment command."
      lw.writeLogVerbose("az-cli", logString)
    else:
      logString = "ERROR: provisioningState for the deployment is NOT Succeeded. "
      lw.writeLogVerbose("az-cli", logString)

  #@private
  def loginToAzAndSetSubscription(self, clientId, clientSecret,tenantId,subscriptionId):
    lw = log_writer()
    #### #The following command gets the client logged in and able to operate on azure repositories.
    loginCmd = "az login --service-principal -u " + clientId + " -p " + clientSecret + " --tenant " + tenantId
    self.getShellJsonResponse(loginCmd)
    logString = "Finished running login command."
    lw.writeLogVerbose("az-cli", logString)
    setSubscriptionCommand = 'az account set --subscription '+subscriptionId
    self.getShellJsonResponse(setSubscriptionCommand)
    logString = 'Finished setting subscription to '+str(subscriptionId)
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
    logString = "cmd is: " + cmd
    lw.writeLogVerbose("acm", logString)
    if process.returncode == 0:
      logString = str(data)
      lw.writeLogVerbose("shell", logString)
      decodedData = data #.decode('utf-8')
      return decodedData
    else:
      if counter < 11:
        counter +=1 
        logString = "Sleeping 30 seconds before running the command a second time in case a latency problem caused the attempt to fail. "
        lw.writeLogVerbose('acm', logString)
        logString = "Attempt "+str(counter)+ " out of 10. "
        lw.writeLogVerbose('acm', logString)
        import time
        time.sleep(30)
        data = self.getShellJsonResponse(cmd,counter)
        return data
      else:  
        if "(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found." in str(err):
          logString = "WARNING: "+"(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found."
          lw.writeLogVerbose('shell')
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

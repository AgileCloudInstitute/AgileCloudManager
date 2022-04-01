## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    
  
import json
import sys
import time
import datetime

import command_runner
import command_builder
import config_fileprocessor
import config_cliprocessor
import logWriter

## USE THIS FOR BUILDING IMAGES: https://github.com/Azure/azvmimagebuilder/tree/main/quickquickstarts/0_Creating_a_Custom_Linux_Managed_Image

def createDeployment(infraConfigFileAndPath, keyDir, caller, serviceType, instName):
  outputDict = {}
  ## STEP 1: Populate variables
  app_parent_path = config_cliprocessor.inputVars.get('app_parent_path')
  yaml_keys_file_and_path = command_builder.getKeyFileAndPath(keyDir, 'systems', 'azure')
  foundationInstanceName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'instanceName')
  if caller == 'networkFoundation':
    typeParent = caller
    serviceType = 'networkFoundation'
    resourceGroupName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'resourceGroupName')
    resourceGroupRegion = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'resourceGroupRegion')
    templateName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'templateName')
#    parameterFile = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'parameterFile')
    deploymentName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'deploymentName')
  elif caller == 'serviceInstance':
    typeParent = 'systems'
    resourceGroupName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'resourceGroupName')
    resourceGroupRegion = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'resourceGroupRegion')
    templateName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'templateName')
#    parameterFile = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'parameterFile')
    deploymentName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'deploymentName')
    foundationResourceGroupName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'resourceGroupName')
    foundationDeploymentName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'deploymentName')
    outputDict['typeParent'] = typeParent
    outputDict['resourceGroupName'] = foundationResourceGroupName
    outputDict['deploymentName'] = foundationDeploymentName
  organization = config_fileprocessor.getFirstLevelValue(infraConfigFileAndPath, 'organization')
  subscriptionId = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'subscriptionId')
  clientId = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
  clientSecret = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret')
  tenantId = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')

  ## STEP 2: Login to az cli and set subscription
  loginToAzAndSetSubscription(clientId, clientSecret,tenantId,subscriptionId)

  ## STEP 3: Create Resource Group
  resourceGroupCmd = 'az group create --name ' + resourceGroupName + ' --location ' + resourceGroupRegion
  print('resourceGroupCmd is: ', resourceGroupCmd)
  command_runner.getShellJsonResponse(resourceGroupCmd)
  logString = "Finished running create resource group command. "
  logWriter.writeLogVerbose("az-cli", logString)

  ## STEP 4: Get template and config variable mapping file
  templatePathAndFile = app_parent_path + templateName
  templatePathAndFile = command_builder.formatPathForOS(templatePathAndFile)
  templateName, module_config_file_and_path = getArmTemplateName(infraConfigFileAndPath, typeParent, serviceType, instName, app_parent_path)
  print('templateName is: ', templateName)
  print('templatePathAndFile is: ', templatePathAndFile)
  print('module_config_file_and_path is: ',module_config_file_and_path)
  print('app_parent_path is: ',app_parent_path)
  ## STEP 5: Assemble and run command to deploy ARM template
  assembleAndRunArmDeploymentCommand(module_config_file_and_path, keyDir, infraConfigFileAndPath, instName, organization, deploymentName, resourceGroupName, templatePathAndFile, outputDict)

  ## STEP 6: If foundation, then create and deploy images, if images are present in config file
  if caller == 'networkFoundation':
    hasImageBuilds = config_fileprocessor.checkTopLevelType(infraConfigFileAndPath, 'imageBuilds')
    if hasImageBuilds:
      typesToFilterImagesFrom = config_fileprocessor.listTypesInImageBuilds(infraConfigFileAndPath)
      for imageTypeName in typesToFilterImagesFrom:
        if imageTypeName == "images":
          configureAzureToDeployImages(templatePathAndFile)
          instanceNames = config_fileprocessor.getImageInstanceNames(infraConfigFileAndPath, imageTypeName)
          for instName in instanceNames:
            print('image instance is: ', instName)
            templateName = config_fileprocessor.getImageTemplateName(infraConfigFileAndPath, 'images', instName)
            deploymentName = config_fileprocessor.getImagePropertyValue(infraConfigFileAndPath, 'images', instName, 'deploymentName')
            ## STEP 4: Get template and config variable mapping file
            templatePathAndFile = app_parent_path + templateName
            templatePathAndFile = command_builder.formatPathForOS(templatePathAndFile)
            print('abc123 templatePathAndFile: ', templatePathAndFile)
            print('templateName is: ', templateName)
            print('deploymentName is: ', deploymentName)
            templateName, module_config_file_and_path = getArmTemplateName(infraConfigFileAndPath, 'imageBuilds', 'images', instName, app_parent_path)
            print('revised templateName is: ', templateName)
            print('module_config_file_and_path is: ', module_config_file_and_path)
#            quit('Test output variables.')
            createImageTemplateAndDeployImage(resourceGroupName,subscriptionId, instName, module_config_file_and_path, keyDir, infraConfigFileAndPath, foundationInstanceName, organization, deploymentName, templatePathAndFile, clientId)
        else:
          logString = "WARNING: This network foundation does not have any image builds associated with it.  If you intend not to build images in this network, then everything is fine.  But if you do want to build images with this network, then check your configuration and re-run this command.  "
          logWriter.writeLogVerbose("acm", logString)
#    quit("BREAKPOINT TO DEBUG ARM IMAGE TEMPLATE DEPLOYMENT")


def destroyDeployment(systemInstanceName, keyDir, infraConfigFileAndPath, caller, serviceType, instName):
  ## STEP 1: Populate variables
  cloud = config_fileprocessor.getCloudName(infraConfigFileAndPath)
  yaml_keys_file_and_path = command_builder.getKeyFileAndPath(keyDir, 'systems', cloud)
  if caller == 'networkFoundation':
    resourceGroupName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'resourceGroupName')
    templateName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'emptyTemplateName')
    deploymentName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'deploymentName')
  elif caller == 'serviceInstance':
    resourceGroupName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'resourceGroupName')
    templateName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'emptyTemplateName')
    deploymentName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'deploymentName')
  subscriptionId = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'subscriptionId')
  clientId = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
  clientSecret = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret')
  tenantId = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')

  ## STEP 2: Login to az cli and set subscription
  loginToAzAndSetSubscription(clientId, clientSecret,tenantId,subscriptionId)

  ## STEP 3: Get template and config variable mapping file
  templatePathAndFile = config_cliprocessor.inputVars.get('app_parent_path') + templateName
  templatePathAndFile = command_builder.formatPathForOS(templatePathAndFile)

  ## STEP 4: delete deployment
  destroyCmd = 'az deployment group create --name '+deploymentName+' --resource-group '+resourceGroupName+' --template-file '+templatePathAndFile+' --verbose '+' --mode complete'
  logString = 'destroyCmd is: '+ destroyCmd
  logWriter.writeLogVerbose("az-cli", logString)
  jsonStatus = command_runner.getShellJsonResponse(destroyCmd)
  print('jsonStatus is: ', jsonStatus)
  jsonStatus = json.loads(jsonStatus)
  state = jsonStatus['properties']['provisioningState']
  logString = 'provisioningState is: '+ state
  logWriter.writeLogVerbose("az-cli", logString)
  if state == 'Succeeded':
    logString = "Finished running deployment command."
    logWriter.writeLogVerbose("az-cli", logString)
  else:
    logString = "ERROR: provisioningState for the deployment is NOT Succeeded. "
    logWriter.writeLogVerbose("az-cli", logString)

  #STEP 5: Now destroy the resource group
  destroyRgCpmmand = 'az group delete -y --name '+resourceGroupName
  logString = 'destroyRgCpmmand is: '+ destroyRgCpmmand
  logWriter.writeLogVerbose("az-cli", logString)
  jsonStatus = command_runner.getShellJsonResponse(destroyRgCpmmand)
  print('jsonStatus is: ', jsonStatus)

def configureAzureToDeployImages(templatePathAndFile):
  data = json.load(open(templatePathAndFile, 'r'))
  resources = data['resources']
  for resource in resources:  
    if resource['type'] == 'Microsoft.VirtualMachineImages/imageTemplates':
      registerProviderVmiCmd = 'az provider register -n Microsoft.VirtualMachineImages'
      command_runner.getShellJsonResponse(registerProviderVmiCmd)
      time.sleep(10)
      registerVmiCmd = 'az feature register --namespace Microsoft.VirtualMachineImages --name VirtualMachineTemplatePreview'
      responseState = getRegistered(registerVmiCmd)
      print('1 responseState is: ', responseState)
      showVmiCmd = 'az feature show --namespace Microsoft.VirtualMachineImages --name VirtualMachineTemplatePreview'
      responseState = getRegistered(showVmiCmd)
      print('2 responseState is: ', responseState)
##THE FOLLOWING 4 LINES WERE THROWING AN ERROR, SO WE COMMENT THEM OUT TO DEVELOP AROUND THEM.  
#      showKvCmd = 'az feature show --namespace Microsoft.KeyVault --name VirtualMachineTemplatePreview'
#      responseState = getRegistered(showKvCmd)
#      print('3 responseState is: ', responseState)
#      print('showKvCmd response is: ', jsonStatus)
      vmiCheck = checkRegistrationState('az provider show -n Microsoft.VirtualMachineImages -o json')
      print('vmiCheck is: ', vmiCheck)
      if vmiCheck != 'Registered':
        regVmiCommand = 'az provider register -n Microsoft.VirtualMachineImages'
        responseState = getRegistered(regVmiCommand)

      kvCheck = checkRegistrationState('az provider show -n Microsoft.KeyVault -o json')
      print('kvCheck is: ', kvCheck)
      if kvCheck != 'Registered':
        regKvCommand = 'az provider register -n Microsoft.Compute'
        responseState = getRegistered(regKvCommand)

      compCheck = checkRegistrationState('az provider show -n Microsoft.Compute -o json')
      print('compCheck is: ', compCheck)
      if compCheck != 'Registered':
        regCompCommand ='az provider register -n Microsoft.KeyVault'
        responseState = getRegistered(regCompCommand)

      storageCheck = checkRegistrationState('az provider show -n Microsoft.Storage -o json')
      print('storageCheck is: ', storageCheck)
      if storageCheck != 'Registered':
        regStorageCommand = 'az provider register -n Microsoft.Storage'
        responseState = getRegistered(regStorageCommand)

      networkCheck = checkRegistrationState('az provider show -n Microsoft.Network -o json')
      print('networkCheck is: ', networkCheck)
      if networkCheck != 'Registered':
        regNetworkCommand = 'az provider register -n Microsoft.Network'
        responseState = getRegistered(regNetworkCommand)
#      outputDict['imgBuilderId'] == :
      print('... type of resource is: ', resource['type'])


def createImageTemplateAndDeployImage(resourceGroupName,subscriptionId, instName, module_config_file_and_path, keyDir, infraConfigFileAndPath, foundationInstanceName, organization, deploymentName, templatePathAndFile, clientId):
  # create user assigned identity for image builder to access the storage account where the script is located
  dateTimeCode = str(datetime.datetime.now()).replace(' ','').replace('-','').replace(':','').replace('.','')
  identityName = 'imgbuilder_'+dateTimeCode
  idCreateCommand = 'az identity create -g ' +resourceGroupName+ ' -n ' +identityName
  jsonResponse = command_runner.getShellJsonResponse(idCreateCommand)
  print('Identity Name Json reponse is: ', str(jsonResponse))
  jsonResponse = json.loads(jsonResponse)
#  msiClientId = jsonResponse['clientId']
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
  jsonResponse = command_runner.getShellJsonResponse(roleDefCreateCommand)
  print('Response from role definition creation is: ', str(jsonResponse))

  #Grant the role definition to the managed service identity
  imageRoleAssignmentCommand = 'az role assignment create --assignee '+msiFullId+' --role '+imageRoleDefinitionName+' --scope /subscriptions/'+subscriptionId+'/resourceGroups/'+resourceGroupName
  imageRoleAssignmentCommand = 'az role assignment create --role '+imageRoleDefinitionName+' --scope /subscriptions/'+subscriptionId+'/resourceGroups/'+resourceGroupName+' --assignee-object-id '+servicePrincipalId+' --assignee-principal-type ServicePrincipal'
  jsonResponse = command_runner.getShellJsonResponse(imageRoleAssignmentCommand)
  print('Response from role assignment command is: ', str(jsonResponse))

## 4 March 2022. Next 3 lines are a temporary test
  imageRoleAssignmentCommand = 'az role assignment create --role '+imageRoleDefinitionName+' --scope /subscriptions/'+subscriptionId+'/resourceGroups/'+resourceGroupName+' --assignee-object-id '+clientId+' --assignee-principal-type ServicePrincipal'
  jsonResponse = command_runner.getShellJsonResponse(imageRoleAssignmentCommand)
  print('Response from 2nd role assignment command is: ', str(jsonResponse))
#  quit('March 4')
  outputDict = {}
  outputDict['identityName'] = identityName
  outputDict['subscriptionId'] = subscriptionId
  outputDict['resourceGroupName'] = resourceGroupName
  outputDict['hasImageBuilds'] = True
  outputDict['dateTimeCode'] = dateTimeCode
  assembleAndRunArmDeploymentCommand(module_config_file_and_path, keyDir, infraConfigFileAndPath, instName, organization, deploymentName, resourceGroupName, templatePathAndFile, outputDict)

  #Build the image from the template you just created.  
  imageTemplateName = config_fileprocessor.getSecondLevelProperty(infraConfigFileAndPath, 'imageBuilds', 'images', instName, 'imageTemplateName')
  imageTemplateName = imageTemplateName+'_'+dateTimeCode
  print('x imageTemplateName is: ', imageTemplateName)
  buildImageCommand = 'az resource invoke-action --resource-group '+resourceGroupName+' --resource-type  Microsoft.VirtualMachineImages/imageTemplates -n '+imageTemplateName+' --action Run '
  jsonResponse = command_runner.getShellJsonResponse(buildImageCommand)
  print('Response from image build process is: ', str(jsonResponse))
  ##THE REST OF THIS FUNCTION IS JUST A TEST TO SEE IF A VM CAN BE CREATED FROM THE IMAGE



def getRegistered(theCmd, counter=0):
  theState = 'NA'
  if (theState != 'Registered') and (counter <20):
    jsonStatus = command_runner.getShellJsonResponse(theCmd)
    print('jsonStatus is: ', str(jsonStatus))
    jsonStatus = json.loads(jsonStatus)
    print('jsonStatus is: ', jsonStatus)
    print('jsonStatus["properties"] is: ', jsonStatus["properties"])

    theState = jsonStatus['properties']['state']
    logString = 'Attempt number ' + str(counter) + ' got response: ' + theState + ' from running command: '+theCmd
    logWriter.writeLogVerbose('acm', logString)
    registerProviderVmiCmd = 'az provider register -n Microsoft.VirtualMachineImages' # --name VirtualMachineTemplatePreview'
    command_runner.getShellJsonResponse(registerProviderVmiCmd)
    if theState != 'Registered':
      counter +=1
      time.sleep(10)
      getRegistered(theCmd, counter)
  return theState

def getUnRegistered(theCmd, counter=0):
  theState = 'NA'
  if (theState != 'Unregistered') and (counter <20):
    jsonStatus = json.loads(command_runner.getShellJsonResponse(theCmd))
    print('jsonStatus is: ', jsonStatus)
    print('jsonStatus["properties"] is: ', jsonStatus["properties"])

    theState = jsonStatus['properties']['state']
    logString = 'Attempt number ' + str(counter) + ' got response: ' + theState + ' from running command: '+theCmd
    logWriter.writeLogVerbose('acm', logString)
    if theState != 'Unregistered':
      counter +=1
      time.sleep(10)
      getUnRegistered(theCmd, counter)
  return theState

def checkRegistrationState(checkCmd):
  print('checkCmd is: ', checkCmd)
  jsonStatus = json.loads(command_runner.getShellJsonResponse(checkCmd))
#  print('jsonStatus is: ', jsonStatus)
  regState = jsonStatus['registrationState']
  print('regState is: ', regState)
  return regState

def getArmTemplateName(infraConfigFileAndPath, typeParent, serviceType, instName, app_parent_path):
#..
  print('......................................................')
  print('infraConfigFileAndPath is: ', infraConfigFileAndPath)
  print('typeParent is: ', typeParent)
  print('serviceType is: ', serviceType)
  print('instName is: ', instName)
  print('app_parent_path is: ', app_parent_path)
  print('......................................................')
#..
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
    print('templateName is: ', templateName)
    logString = "Template name is not valid.  Must have only one /.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  return templateName, module_config_file_and_path

def assembleAndRunArmDeploymentCommand(module_config_file_and_path, keyDir, infraConfigFileAndPath, foundationInstanceName, organization, deploymentName, resourceGroupName, templatePathAndFile, outputDict):
  ## STEP 5: Assemble deployment command
  print('module_config_file_and_path', module_config_file_and_path)
  deployVarsFragment = command_builder.getArmVarsFragment(keyDir, infraConfigFileAndPath, module_config_file_and_path, foundationInstanceName, None, foundationInstanceName, organization, outputDict)
  print("deployVarsFragment is: ", deployVarsFragment)
  deployCmd = 'az deployment group create --name '+deploymentName+' --resource-group '+resourceGroupName+' --template-file '+templatePathAndFile+' --verbose '+deployVarsFragment
  logString = 'deployCmd is: '+ deployCmd
  logWriter.writeLogVerbose("az-cli", logString)
#  quit('!Yeehaw!...')
  ## STEP 6: Run Deployment command and check results
  jsonStatus = command_runner.getShellJsonResponse(deployCmd)
  print('jsonStatus is: ', jsonStatus)
  jsonStatus = json.loads(jsonStatus)
  state = jsonStatus['properties']['provisioningState']
  logString = 'provisioningState is: '+ state
  logWriter.writeLogVerbose("az-cli", logString)
  if state == 'Succeeded':
    logString = "Finished running deployment command."
    logWriter.writeLogVerbose("az-cli", logString)
  else:
    logString = "ERROR: provisioningState for the deployment is NOT Succeeded. "
    logWriter.writeLogVerbose("az-cli", logString)

def loginToAzAndSetSubscription(clientId, clientSecret,tenantId,subscriptionId):
  #### #The following command gets the client logged in and able to operate on azure repositories.
  loginCmd = "az login --service-principal -u " + clientId + " -p " + clientSecret + " --tenant " + tenantId
  command_runner.getShellJsonResponse(loginCmd)
  logString = "Finished running login command."
  logWriter.writeLogVerbose("az-cli", logString)
  setSubscriptionCommand = 'az account set --subscription '+subscriptionId
  command_runner.getShellJsonResponse(setSubscriptionCommand)
  logString = 'Finished setting subscription to '+str(subscriptionId)
  logWriter.writeLogVerbose("az-cli", logString)

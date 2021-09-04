## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import yaml
import os 
import shutil
import json
import platform
import shutil
import pathlib

import commandRunner
import commandBuilder
import configReader
import callInstanceManager
import releaseDefConstructor
import logWriter

buildRepoListOfTuples = []

def onFoundation(command, **inputVars):
  typeName = 'networkFoundation'
  yamlInfraConfigFileAndPath = inputVars.get('yamlInfraConfigFileAndPath')
  foundationInstanceName = configReader.getFoundationInstanceName(yamlInfraConfigFileAndPath)
  instanceNames = [foundationInstanceName]
  operation = command
  terraformCrudOperation(operation, 'none', typeName, None, None, instanceNames, **inputVars)
  if commandRunner.terraformResult == "Applied": 
    hasImageBuilds = configReader.checkTopLevelType(yamlInfraConfigFileAndPath, 'imageBuilds')
    print("hasImageBuilds is: ", hasImageBuilds)
    if hasImageBuilds:
      app_parent_path = os.path.dirname(os.path.realpath("..\\")) + '\\'
      operation = 'on'
      typesInImageBuilder = ['subnetForBuilds']
      print("-----------------------------------------------------------------------------")
      result = 'Failed'
      for typeName in typesInImageBuilder:
        instanceNames = configReader.getImageInstanceNames(yamlInfraConfigFileAndPath, typeName)
        terraformCrudOperation(operation, 'imageBuilds', typeName, None, None, instanceNames, **inputVars)
        localMsg = "done with -- " + typeName + " -----------------------------------------------------------------------------"
        print(localMsg)
        if commandRunner.terraformResult == "Applied": 
          print("-----------------------------------------------------------------------------")
          result = "Success"
        else:
          result = 'Failed'
          quit("Terraform operation failed.  Quitting program here so you can debug the source of the problem.  ")
      if result == 'Success':
        ###Next Build The Images
        imageSpecs = configReader.getImageSpecs(yamlInfraConfigFileAndPath)
        print("-----------------------------------------------------------------------------")
        typesToFilterImagesFrom = configReader.listTypesInImageBuilds(yamlInfraConfigFileAndPath)
        for imageTypeName in typesToFilterImagesFrom:
          if imageTypeName == "images":
            instanceNames = configReader.getImageInstanceNames(yamlInfraConfigFileAndPath, imageTypeName)
            operation = 'build'
            packerCrudOperation(operation, imageTypeName, instanceNames, **inputVars)
            if commandRunner.success_packer == 'true':
              localMsg = "done with -- " + imageTypeName + " -----------------------------------------------------------------------------"
              print(localMsg)
            else:
              quit("Failed Packer Build.  Stopping program so you can diagnose the problem. ")
        print("-----------------------------------------------------------------------------")
      #Now off the packer subnet and the security group rule.
      operation = 'off'
      result = 'Failed'
      for typeName in typesInImageBuilder:
        #FIX THE PROBLEM CAUSED BY THE NEXT 4 LINES IN WHICH THE sshAdmin RULE IS ADDED LATER ALSO.  WE NEED TO BLOCK SSH ACCESS IN LAUNCHED INSTANCES.  INSTEAD, WE JUST DELETE DEFECTIVE INSTANCES AND CREATE NEW ONES TO KEEP THE INSTANCES MORE SECURE. 
        if typeName == "securityGroupRules":
          instanceNames = ["sshAdmin"]
        else: 
          instanceNames = configReader.getImageInstanceNames(yamlInfraConfigFileAndPath, typeName)
        terraformCrudOperation(operation, 'imageBuilds', typeName, None, None, instanceNames, **inputVars)
        localMsg = "done with -- " + typeName + " -----------------------------------------------------------------------------"
        print(localMsg)
        if commandRunner.terraformResult == "Destroyed": 
          result = "Success"
        else:
          result = 'Failed'
          quit("Terraform operation failed.  Quitting program here so you can debug the source of the problem.  ")
      if result == 'Success':
        print("Finished deleting the temporary resources that Packer needed to build images.  ")
    else:
      print("WARNING: This network foundation does not have any image builds associated with it.  If you intend not to build images in this network, then everything is fine.  But if you do want to build images with this network, then check your configuration and re-run this command.  ")

def offFoundation(**inputVars):
  typeName = 'networkFoundation'
  yamlInfraConfigFileAndPath = inputVars.get('yamlInfraConfigFileAndPath')
  foundationInstanceName = configReader.getFoundationInstanceName(yamlInfraConfigFileAndPath)
  instanceNames = [foundationInstanceName]
  operation = 'output'
  terraformCrudOperation(operation, 'none', typeName, None, None, instanceNames, **inputVars)
  print("---------------------------------------------------------------------------------------------------------------")
  operation = 'off'
  #add code to confirm that output operation succeeded.
  #Also, if output showed there is no network foundation, then skip the rest of the off operations because there would be nothing to off in that case.
  #ADD LOGIC HERE TO PREPARE BEFORE DELETING THE FOUNDATION 
  ##########################################################################################
  ### off the Network Foundation and the Instance of the Call To The Foundation Module
  ##########################################################################################
  typeName = 'networkFoundation'
  foundationInstanceName = configReader.getFoundationInstanceName(yamlInfraConfigFileAndPath)
  instanceNames = [foundationInstanceName]
  operation = 'off'
  terraformCrudOperation(operation, 'none', typeName, None, None, instanceNames, **inputVars) 
  if commandRunner.terraformResult == "Destroyed": 
    print("off operation succeeded.  Now inside Python conditional block to do only after the off operation has succeeded. ")

#..............................................................................................................................................
def getTfBackendPropVal(yaml_keys_file_and_path, instName, templateName, propName, **inputVars):
  varVal = ''
  yamlInfraConfigFileAndPath = inputVars.get('yamlInfraConfigFileAndPath')
  rgNameCoords = configReader.getPropertyCoordinatesFromCSV(templateName, propName, **inputVars)
  print("propName is: ", propName)
  coordsParts = rgNameCoords.split("/")
  print("coordsParts is: ", coordsParts)
  if coordsParts[0] == 'infrastructureConfig.yaml':
    if rgNameCoords.count('/') == 1:
      if coordsParts[1] == 'networkFoundation':
        varVal = configReader.getTopLevelProperty(yamlInfraConfigFileAndPath, coordsParts[1], propName)
    elif rgNameCoords.count('/') == 2:
      parentPart = coordsParts[1]
      childPart = coordsParts[2]
      if parentPart == 'systems':
        varVal = configReader.getSystemPropertyValue(yamlInfraConfigFileAndPath, "tfBackend", instName, propName)
  elif coordsParts[0] in yaml_keys_file_and_path:
    print("coordsParts[0] key is: ", coordsParts[0])
    varVal = configReader.getFirstLevelValue(yaml_keys_file_and_path, propName)
#>    quit("stopping to debug secret.  ")
  else:
    print("No match: ", coordsParts[1])
  return varVal
#..............................................................................................................................................
#...................................................................................
def writeBackendFile(storageAccountName, storageContainerName, subscriptionId, clientId, clientSecret, tenantId, resourceGroupName):
  tfBackendConfigDir = "C:\\projects\\acm\\shared\\keys\\"
  backendFile = tfBackendConfigDir + "module." + storageContainerName + ".backend.tfvars"
  with open(backendFile, 'w') as f:
    f.write("storage_account_name = \""+storageAccountName+"\"\n")
    f.write("container_name       = \""+storageContainerName+"\"\n")
    f.write("subscription_id      = \""+subscriptionId+"\"\n")
    f.write("client_id            = \""+clientId+"\"\n")
    f.write("client_secret        = \""+clientSecret+"\"\n")
    f.write("tenant_id            = \""+tenantId+"\"\n")
    f.write("resource_group_name  = \""+resourceGroupName+"\"\n")
#...................................................................................


def onSystem(command, **inputVars):
  typeName = 'networkFoundation'
  yamlInfraConfigFileAndPath = inputVars.get('yamlInfraConfigFileAndPath')
  foundationInstanceName = configReader.getFoundationInstanceName(yamlInfraConfigFileAndPath)
  instanceNames = [foundationInstanceName]
  operation = 'output'
  terraformCrudOperation(operation, 'none', typeName, None, None, instanceNames, **inputVars)
  print("---------------------------------------------------------------------------------------------------------------")
  operation = 'on'
  ##############################################################################
  ### Copy the template into a new instance of a call to the vm module
  ##############################################################################
  typesToCreate = configReader.listTypesInSystem(yamlInfraConfigFileAndPath)
  
  isTfBackend = False
  for systemType in typesToCreate:
    if "tfBackend" in systemType:
      isTfBackend = True
    
  if isTfBackend == True:
    for systemType in typesToCreate:
      if "tfBackend" not in systemType:
        typesToCreate.remove(systemType)
    #https://docs.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage?tabs=azure-cli
    #https://docs.microsoft.com/en-us/cli/azure/storage/account?view=azure-cli-latest#az_storage_account_create
    #https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account
    #https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_container
    #https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_blob
    yamlInfraConfigFileAndPath = inputVars.get('yamlInfraConfigFileAndPath')
    cloud = configReader.getCloudName(yamlInfraConfigFileAndPath)
    yaml_keys_file_and_path = commandBuilder.getKeyFileAndPath('systems', cloud, **inputVars)
    
    resourceGroupName = ''
    resourceGroupRegion = ''
    
    instanceNames = configReader.getSystemInstanceNames(yamlInfraConfigFileAndPath, "tfBackend")
    print("instanceNames is: ", instanceNames)
    for instName in instanceNames:
      templateName = configReader.getSystemPropertyValue(yamlInfraConfigFileAndPath, "tfBackend", instName, "templateName")
      print("templateName is: ", templateName)
      backendType = configReader.getSystemPropertyValue(yamlInfraConfigFileAndPath, "tfBackend", instName, "type")
      print("backendType is: ", backendType)
    
      if backendType == 'azurerm':  
        #Get the variable values
        resourceGroupName = getTfBackendPropVal(yaml_keys_file_and_path, instName, templateName, 'resourceGroupName', **inputVars)
        resourceGroupRegion = getTfBackendPropVal(yaml_keys_file_and_path, instName, templateName, 'resourceGroupRegion', **inputVars)
        storageAccountName = getTfBackendPropVal(yaml_keys_file_and_path, instName, templateName, 'storageAccountName', **inputVars)
        subscriptionId = getTfBackendPropVal(yaml_keys_file_and_path, instName, templateName, 'subscriptionId', **inputVars)
        clientId = getTfBackendPropVal(yaml_keys_file_and_path, instName, templateName, 'clientId', **inputVars)
        clientSecret = getTfBackendPropVal(yaml_keys_file_and_path, instName, templateName, 'clientSecret', **inputVars)
        tenantId = getTfBackendPropVal(yaml_keys_file_and_path, instName, templateName, 'tenantId', **inputVars)
        if clientSecret[0] == '-':
          clientSecret = '\'' + clientSecret + '\''
    
        #Login to az cli
        #### #The following command gets the client logged in and able to operate on azure repositories.
        myCmd = "az login --service-principal -u " + clientId + " -p " + clientSecret + " --tenant " + tenantId
        print("myCmd is: ", myCmd)
        commandRunner.getShellJsonResponse(myCmd)
        print("Finished running login command.")
    
        #First create storage account
        #https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-cli
        createStorageAccountCommand = "az storage account create --name " + storageAccountName + " --resource-group " + resourceGroupName + " --location " + resourceGroupRegion + " --sku Standard_LRS   --encryption-services blob " 
        print("createStorageAccountCommand is: ", createStorageAccountCommand)
        commandRunner.runShellCommand(createStorageAccountCommand)  
        print("Finished running createStorageAccountCommand. ")
    
        getAccountKeyCommand = "az storage account keys list --resource-group " + resourceGroupName + " --account-name " + storageAccountName + " --query [0].value -o tsv "  
        print("getAccountKeyCommand is: ", getAccountKeyCommand)  
        accountKey = commandRunner.getAccountKey(getAccountKeyCommand)  
    
        #Then create the 6 storage containers within the storage account to correspond with the sections in infrastructureConfig 
        # Adding .lower() to the string declarations as a reminder that the azure portal only seems to accept lower case.  If you remove .lower() , then the containers that have camel case names like networkFoundation will NOT be created.
        storageContainerName = 'networkFoundation'.lower()
        createStorageContainerCommand = "az storage container create -n " + storageContainerName + " --fail-on-exist --account-name " + storageAccountName + " --account-key " + accountKey  
        commandRunner.getShellJsonResponse(createStorageContainerCommand)  
        writeBackendFile(storageAccountName, storageContainerName, subscriptionId, clientId, clientSecret, tenantId, resourceGroupName)
    
        storageContainerName = 'systems'.lower()
        createStorageContainerCommand = "az storage container create -n " + storageContainerName + " --fail-on-exist --account-name " + storageAccountName + " --account-key " + accountKey  
        commandRunner.getShellJsonResponse(createStorageContainerCommand)  
        writeBackendFile(storageAccountName, storageContainerName, subscriptionId, clientId, clientSecret, tenantId, resourceGroupName)
    
        #add error handling for all of the above steps
    
  else:
    #System is NOT a terraform backend, or at least is not one defined through az-cli, so we will proceed with building the system with terraform
    typeParent = 'systems'
    print("-----------------------------------------------------------------------------")
    for typeName in typesToCreate:
      if (typeName != "networkFoundation") and (typeName != "subnetForBuilds") and (typeName != "images"):
        instanceNames = configReader.getSystemInstanceNames(yamlInfraConfigFileAndPath, typeName)
        print("typesToCreate is: ", typesToCreate)
        print("instanceNames is: ", instanceNames)
#>>        quit("breakpoint in systems. ")
        terraformCrudOperation(operation, typeParent, typeName, None, None, instanceNames, **inputVars)
        localMsg = "done with -- " + typeName + " -----------------------------------------------------------------------------"
        print(localMsg)


def offSystem(**inputVars):
  yamlInfraConfigFileAndPath = inputVars.get('yamlInfraConfigFileAndPath')

  typesToDestroy = configReader.listTypesInSystem(yamlInfraConfigFileAndPath)

  isTfBackend = False
  for systemType in typesToDestroy:
    if "tfBackend" in systemType:
      isTfBackend = True
  print("isTfBackend is: ", isTfBackend)
    
  if isTfBackend == True:
    quit("Halting program because we are leaving the destruction of terraform backends to be a manual step in the UI portal in order to protect your data. ")
  else: 
    typeName = 'networkFoundation'
    foundationInstanceName = configReader.getFoundationInstanceName(yamlInfraConfigFileAndPath)
    instanceNames = [foundationInstanceName]
    operation = 'output'
    terraformCrudOperation(operation, 'none', typeName, None, None, instanceNames, **inputVars)
    print("---------------------------------------------------------------------------------------------------------------")
    operation = 'off'
    #add code to confirm that output operation succeeded.
    #Also, if output showed there is no network foundation, then skip the rest of the off operations because there would be nothing to off in that case.
    typeParent = 'systems'
    for typeName in typesToDestroy:
      if typeName != "networkFoundation" and (typeName != "subnetForBuilds") and (typeName != "images"):
        instanceNames = configReader.getSystemInstanceNames(yamlInfraConfigFileAndPath, typeName)
        terraformCrudOperation(operation, typeParent, typeName, None, None, instanceNames, **inputVars)
        localMsg = "done with -- " + typeName + " -----------------------------------------------------------------------------"
        print(localMsg)
        if commandRunner.terraformResult == "Destroyed": 
          print("off operation succeeded.  Now inside Python conditional block to do only after the off operation has succeeded. ")
        else:
          quit("Error: off operation failed.  ")

def onProject(command, **inputVars):
  yamlInfraConfigFileAndPath = inputVars.get('yamlInfraConfigFileAndPath')
  projectResult = 'Failed'
  operation = 'on'
  typeParent = 'projectManagement'
  cloud = configReader.getCloudName(yamlInfraConfigFileAndPath)
  if len(cloud) < 2:
    quit("ERROR: cloud name not valid.  Add better validation checking to the code. ")
  if cloud == 'azure':
    mycloud = 'ok'
  else:
    quit("Project management tools other than Azure Devops are planned for future releases.  Until then, cloud must be set to azure for projectManagement block items.  ")
  app_parent_path = inputVars.get('app_parent_path')
  projectInstanceNames = configReader.getProjectManagementInstanceNames(yamlInfraConfigFileAndPath, 'projects', None)
  for projName in projectInstanceNames:
    projNames = [projName]
    terraformCrudOperation(operation, typeParent, 'projects', None, None, projNames, **inputVars)
    if commandRunner.terraformResult == "Applied": 
      print("Project creation operation succeeded.  Now inside Python conditional block to do only after the on operation has succeeded. ")
      print("-----------------------------------------------------------------------------")
      projectResult = "Success"
      localMsg = "done with " + projName + "project.  But now going to add any code repos and builds specified for this project. ----------------------------------------"
      print(localMsg)
      yaml_keys_file_and_path = commandBuilder.getKeyFileAndPath(typeParent, cloud, **inputVars)
      organization = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgServiceURL')
      subscriptionId = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'subscriptionId')
      clientId = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
      clientSecret = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret') 
      tenantId = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
      #### #The following command gets the client logged in and able to operate on azure repositories.
      loginCmd = "az login --service-principal -u " + clientId + " --tenant " + tenantId + " -p \"" + clientSecret + "\""
      commandRunner.runShellCommand(loginCmd)
      pid = commandRunner.azuredevops_project_id
      pid = pid.replace('"', '')
      scTemplateFile = "C:\\projects\\acm\\Jun2021_r\\config-outside-acm-path\\vars\\VarsForTerraform\\azdo_service_endpoint_othergit.json"
      if len(pid) > 2:
        azPat = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgPAT')
        azdoLoginCmd= "ECHO " + azPat + " | " + "az devops login --organization "+organization + " --debug "
        commandRunner.runShellCommand(azdoLoginCmd)
        gitUsername = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'gitUsername')
        gitPass = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'gitPass')
      else: 
        quit("Unable to read a valid project id.  Halting program so you can identify the source of the problem before proceeding. ")
      codeInstanceNames = configReader.getCodeInstanceNames(yamlInfraConfigFileAndPath, projName)
      for codeInstance in codeInstanceNames:
        serviceEndPointName = '_' + codeInstance
        gitSourceUrl = configReader.getThirdLevelProperty(yamlInfraConfigFileAndPath, typeParent, 'projects', projName, 'code', codeInstance, "sourceRepo")
        endpointTemplate = app_parent_path + configReader.getThirdLevelProperty(yamlInfraConfigFileAndPath, typeParent, 'projects', projName, 'code', codeInstance, 'endpointTemplate')
        if platform.system() == "Windows":
          endpointTemplate = endpointTemplate.replace('/','\\')
        else:
          endpointTemplate.replace('\\','/')
        with open(endpointTemplate, 'r') as f:
          template = json.load(f)
        template['name'] = serviceEndPointName
        template['url'] = gitSourceUrl
        template['authorization']['parameters']['username'] = gitUsername
        template['authorization']['parameters']['password'] = gitPass
        template['serviceEndpointProjectReferences'][0]['projectReference']['id'] = pid
        template['serviceEndpointProjectReferences'][0]['projectReference']['name'] = projName
        template['serviceEndpointProjectReferences'][0]['name'] = serviceEndPointName
        orgName = organization.rsplit('/')[3]
        rcode, rJson = commandRunner.createAzdoServiceEndpointApiRequest(template, orgName, azPat)
        ##Add handling for the next line based on the value of rcode
        endPtId = rJson['id']
      terraformCrudOperation(operation, typeParent, 'projects', projName, 'projects/code', codeInstanceNames, **inputVars)
      codeResult = 'Failed'
      if commandRunner.terraformResult == "Applied": 
        codeResult = "Success"
        azPat = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgPAT')
        for codeInstanceName in codeInstanceNames:
          typeChild = "projects"
          grandChildType = "code"
          gitSourceUrl = configReader.getThirdLevelProperty(yamlInfraConfigFileAndPath, typeParent, typeChild, projName, grandChildType, codeInstanceName, "sourceRepo")
          if len(endPtId) > 2:  
            myCmd = "az repos import create --git-source-url " + gitSourceUrl + " --repository " + codeInstanceName + " --git-service-endpoint-id  " + endPtId + " --organization " + organization + " --project " + projName + " --requires-authorization "
          else:
            myCmd = "az repos import create --git-source-url " + gitSourceUrl + " --repository " + codeInstanceName + " --organization " + organization + " --project " + projName
          try:
            myResponse = commandRunner.getShellJsonResponse(myCmd)
            jsonOutput = json.loads(myResponse)
            allSteps = jsonOutput['detailedStatus']['allSteps']
            currentStep = jsonOutput['detailedStatus']['currentStep']
            if len(allSteps) == currentStep:
              status = jsonOutput['status']
              if status == 'completed':
                azdoLogoutCmd= "ECHO " + azPat + " | " + "az devops logout --organization "+organization 
                commandRunner.runShellCommand(azdoLogoutCmd)
              else:
                quit("Halting prograsm because repository was not imported successfully.  Please review your logs to identify what happened so that this can be re-run successfully.  ")
          except Exception as e:
            print("WARNING: Failed to import repository.  Continuing gracefully in case you already imported this repository and are simply re-running this module.  But please check to confirm that the repository has been imported previously.  ")
            print("-----  ERROR message is: -----")
            print(e)
      else:
        quit("Terraform operation failed.  Quitting program here so you can debug the source of the problem.  ")
    else:
      projectResult = 'Failed'
      quit("Terraform project operation failed.  Quitting program here so you can debug the source of the problem.  ")
  if (projectResult == 'Success') and (codeResult == 'Success'):
    print("Finished creating projects and code repositories.  ")

def offProject(**inputVars):
  yamlInfraConfigFileAndPath = inputVars.get('yamlInfraConfigFileAndPath')
  result = 'Failed'
  operation = 'off'
  typeParent = 'projectManagement'
  cloud = configReader.getCloudName(yamlInfraConfigFileAndPath)
  if len(cloud) < 2:
    quit("ERROR: cloud name not valid.  Add better validation checking to the code. ")
  if cloud == 'azure':
    mycloud = 'ok'
  else:
    quit("Project management tools other than Azure Devops are planned for future releases.  Until then, cloud must be set to azure for projectManagement block items.  ")
  projectInstanceNames = configReader.getProjectManagementInstanceNames(yamlInfraConfigFileAndPath, 'projects', None)
  for projName in projectInstanceNames:
    codeInstanceNames = configReader.getCodeInstanceNames(yamlInfraConfigFileAndPath, projName)
    terraformCrudOperation(operation, typeParent, 'projects', projName, 'projects/code', codeInstanceNames, **inputVars)
    codeResult = 'Failed'
    if commandRunner.terraformResult == "Destroyed": 
      codeResult = "Success"
    else:
      codeResult = 'Failed'
    projNames = [projName]
    terraformCrudOperation(operation, typeParent, 'projects', None, None, projNames, **inputVars)
    if commandRunner.terraformResult == "Destroyed": 
      result = "Success"
    else:
      result = 'Failed'
      quit("Terraform operation failed.  Quitting program here so you can debug the source of the problem.  ")
    localMsg = "Done with " + projName + " project. ----------------------------------------"
    print(localMsg)
  if result == 'Success':
    print("off operation succeeded.  Now inside Python conditional block to do only after the off operation has succeeded. ")
  else:
    quit("Error: off operation failed.  ")

def onPipeline(command, **inputVars):
  yamlInfraConfigFileAndPath = inputVars.get('yamlInfraConfigFileAndPath')
  operation = 'on'  
  releaseDefInstanceNames = configReader.getReleaseDefinitionInstanceNames(yamlInfraConfigFileAndPath, 'releaseDefinitions')  
  for iName in releaseDefInstanceNames:  
    projName = configReader.getSecondLevelProperty(yamlInfraConfigFileAndPath, 'releaseDefinition', 'releaseDefinitions', iName, 'projectName')  
    operation = "output"  
    projectInstanceNames = [projName] 
    terraformCrudOperation(operation, 'projectManagement', 'projects', None, None, projectInstanceNames, **inputVars)
    #Get the following 2:
    azuredevops_project_id = commandRunner.azuredevops_project_id
    azuredevops_service_connection_id = commandRunner.azuredevops_service_connection_id
    sourceRepos = configReader.getThirdLevelList(yamlInfraConfigFileAndPath, 'releaseDefinition', 'releaseDefinitions', iName, 'repositories', 'instanceName')  
    #Next: get code instance names
    typeParent = 'projectManagement'
    typeName = 'projects/code'
    cloud = configReader.getCloudName(yamlInfraConfigFileAndPath)
    if len(cloud) < 2:
      quit("ERROR: cloud name not valid.  Add better validation checking to the code. ")
    if cloud == 'azure':
      yaml_keys_file_and_path = commandBuilder.getKeyFileAndPath(typeName, cloud, **inputVars)
      clientId = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
      clientSecret = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret') 
      tenantId = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
      #### #The following command gets the client logged in and able to operate on azure repositories.
      myCmd = "az login --service-principal -u " + clientId + " -p " + clientSecret + " --tenant " + tenantId
      commandRunner.runShellCommand(myCmd)
      instanceNames = configReader.getProjectManagementInstanceNames(yamlInfraConfigFileAndPath, typeName, 'yes')
      print("instanceNames are: ", instanceNames)
      #NOTE: ESTABLISH RULES FOR A SCHEMA INCLUDING RELATIONSHIP BETWEEN PROJECTS, code, AND RELEASE DEFINITIONS, AND THEN FILTER INSTANCE NAMES TO ONLY RETURN INSTANCES THAT MATCH SCHEMA RULES.  
      operation = 'output'
      codeInstanceNames = configReader.getCodeInstanceNames(yamlInfraConfigFileAndPath, projName)
      terraformCrudOperation(operation, typeParent, 'projects', projName, typeName, codeInstanceNames, **inputVars)
      localMsg = "done with -- " + typeName + " -----------------------------------------------------------------------------"
      print(localMsg)
      orgServiceURL = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgServiceURL')
      if orgServiceURL[len(orgServiceURL)-1] != '/':
        orgServiceURL = orgServiceURL + '/'
      organization = orgServiceURL.rsplit('/')[3]
      azPat = configReader.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgPAT')
      azuredevops_project_id = azuredevops_project_id.replace('"','')
      queue_name = "Default"
      poolQueueId = commandRunner.getPoolQueueIdApiRequest(organization, azuredevops_project_id, queue_name, azPat)
      dirOfReleaseDefJsonParts = inputVars.get('dirOfReleaseDefJsonParts')
      #////////////////////////////////////////////////////////////////////////////////////////////////////////
      #// Step Three: Convert YAML definition to JSON data
      #////////////////////////////////////////////////////////////////////////////////////////////////////////
      yamlDir = inputVars.get('dirOfReleaseDefYaml')
      YamlReleaseDefFile = configReader.getSecondLevelProperty(yamlInfraConfigFileAndPath, 'releaseDefinition', 'releaseDefinitions', iName, 'YamlDefinitionFileName')  
      yamlFile = yamlDir + YamlReleaseDefFile
      deployPhaseTemplateFile = dirOfReleaseDefJsonParts + 'deployPhaseTemplate.json'
      environmentTemplateFile = dirOfReleaseDefJsonParts + 'environmentTemplate.json'
      releaseDefConstructorTemplateFile = dirOfReleaseDefJsonParts + 'releaseDefConstructorTemplate.json'
      artifactsTemplateFile = dirOfReleaseDefJsonParts + 'artifactsTemplate.json'
      vaultName = configReader.getSecondLevelProperty(yamlInfraConfigFileAndPath, 'releaseDefinition', 'releaseDefinitions', iName, 'vaultName')  
      releaseDefData = releaseDefConstructor.getReleaseDefData(yamlFile, dirOfReleaseDefJsonParts, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, artifactsTemplateFile, poolQueueId, azuredevops_project_id, orgServiceURL, projName, buildRepoListOfTuples, vaultName, azuredevops_service_connection_id)
      print("--------------------------------------------------------")
      print("revised releaseDefData is: ", releaseDefData)
      print("--------------------------------------------------------")
      #//////////////////////////////////////////////////////////////////////////////////////////////
      #// Step Four: Create Release Definition By Making API Call.
      #//////////////////////////////////////////////////////////////////////////////////////////////
      rCode = releaseDefConstructor.createReleaseDefinitionApiRequest(releaseDefData, organization, azuredevops_project_id, azPat)
      print("response code from create release definition API call is: ", rCode)
    else:
      quit("Halting program because currently Azure DevOps is the only tool supported for release definitions.  ")


def offPipeline(**inputVars):
  print("---------------------------------------------------------------------------------------------------------------")
  print("Release Pipelines need to be destroyed manually inside the UI portal.  We are leaving Release destruction as a manual task to ensure the security of your release logs. ")


def onTfBackend(**inputVars):
  print("delete this function because the commands moved to a new conditional block inside onSystem. ")

def offTfBackend(**inputVars):
  print("---------------------------------------------------------------------------------------------------------------")
  print("Backends for terraform need to be destroyed manually inside the UI portal.  We are leaving backend destruction as a manual task to ensure the security of your logs. ")


def terraformCrudOperation(operation, typeParent, typeName, parentInstanceName, typeGrandChild, instanceNames, **inputVars):
  yaml_infra_config_file_and_path = inputVars.get('yamlInfraConfigFileAndPath')
  foundationInstanceName = configReader.getFoundationInstanceName(yaml_infra_config_file_and_path)
  cloud = configReader.getCloudName(yaml_infra_config_file_and_path)
  if len(cloud) < 2:
    quit("ERROR: cloud name not valid.  Add better validation checking to the code. ")
  global buildRepoListOfTuples
  print("instanceNames is: ", instanceNames)
  for instanceName in instanceNames: 
    #1. First assemble the variables
    if typeGrandChild != None:
      if typeGrandChild == 'projects/code':
        typeGC = typeGrandChild.split('/')[1]
        templateName = configReader.getTemplateName(yaml_infra_config_file_and_path, typeParent, typeName, typeGC, parentInstanceName, instanceName)  
    else:
      templateName = configReader.getTemplateName(yaml_infra_config_file_and_path, typeParent, typeName, None, instanceName, None)  
    dynamicVarsPath = inputVars.get('dynamicVarsPath')
    oldTfStateName = callInstanceManager.getBackedUpStateFileName(dynamicVarsPath, foundationInstanceName, templateName, instanceName)
    app_parent_path = inputVars.get('app_parent_path')
    relative_path_to_instances =  inputVars.get('relativePathToInstances')
    path_to_application_root = ''
    print("templateName is: ", templateName)
    if templateName.count('/') == 2:
      nameParts = templateName.split("/")
      if (len(nameParts[0]) > 1) and (len(nameParts[1]) >1) and (len(nameParts[2]) > 1):
        relative_path_to_instances = nameParts[0] + '\\' + nameParts[1] + relative_path_to_instances  
        template_Name = nameParts[2]  
        path_to_application_root = app_parent_path + nameParts[0] + "\\" + nameParts[1] + "\\"
        module_config_file_and_path = app_parent_path + nameParts[0] + '\\variableMaps\\' + template_Name + '.csv'
      else:
        quit('ERROR: templateName is not valid. ')
    else:  
      quit("Template name is not valid.  Must have only one /.  ")
    relativePathToInstance = relative_path_to_instances + template_Name + "\\"
    destinationCallParent = callInstanceManager.convertPathForOS(app_parent_path, relativePathToInstance)
    #2. Then second instantiate call to module
    destinationCallInstance = callInstanceManager.instantiateCallToModule(path_to_application_root, instanceName, template_Name, oldTfStateName, **inputVars)

#    print("module_config_file_and_path is: ", module_config_file_and_path)
#    if typeParent == 'systems':
#      quit("whoa nelly!")

    if os.path.exists(destinationCallInstance) and os.path.isdir(destinationCallInstance):
      #3. Then third assemble and run command
      callInstanceManager.assembleAndRunCommand(cloud, template_Name, operation, yaml_infra_config_file_and_path, foundationInstanceName, parentInstanceName, instanceName, destinationCallInstance, typeName, module_config_file_and_path, **inputVars)
      if typeGrandChild != None:
        if typeGrandChild == 'projects/code' and (operation == 'output'):
          buildRepoListOfTuples.append(((commandRunner.azuredevops_build_definition_id).replace('"', ''), (commandRunner.azuredevops_git_repository_name).replace('"', '')))
      #4. Then fourth off each instance of the calls to the modules in local agent file system
      doCleanup = callInstanceManager.setDoCleanUp(operation)
      if(doCleanup):
        print("Inside conditional block of things to do if operation completed: ", operation)
        print("templateName inside terraformCrudOperation succeed block is: ", templateName)
        key_source = inputVars.get('keySource')
        tfvars_file_and_path = inputVars.get('tfvarsFileAndPath') 
        ############################################################################################################################
        if (typeName == 'admin') and (operation == 'on') and (commandRunner.terraformResult == "Applied"): 
          org = configReader.getFirstLevelValue(yaml_infra_config_file_and_path, "organization")
          source_keys_file_and_path = commandBuilder.getKeyFileAndPath(typeName, cloud, **inputVars)

          dest_keys_file_and_path = commandBuilder.getKeyFileLocation(instanceName, cloud, **inputVars)
          print("dest_keys_file_and_path is: ", dest_keys_file_and_path)
          print("About to saveKeyFile. ")

#          quit("stopping to debug.")
          callInstanceManager.saveKeyFile(destinationCallInstance, instanceName, cloud, source_keys_file_and_path, dest_keys_file_and_path, org, **inputVars)
#          quit("stopping to debug.")
#...............................
        if (typeName == 'admin') and (operation == 'off') and (commandRunner.terraformResult == "Destroyed"): 
          org = configReader.getFirstLevelValue(yaml_infra_config_file_and_path, "organization")
#          source_keys_file_and_path = commandBuilder.getKeyFileAndPath(typeName, cloud, **inputVars)
          dest_keys_file_and_path = commandBuilder.getKeyFileLocation(instanceName, cloud, **inputVars)
          filePathParts = dest_keys_file_and_path.split("\\")
          keyFileName = filePathParts[-1]
          pathOnly = dest_keys_file_and_path.replace(keyFileName, '')
          print("dest_keys_file_and_path is: ", dest_keys_file_and_path)
          print("keyFileName is: ", keyFileName)
          print("pathOnly", pathOnly)
          print("About to deleteKeyFile. ")

          path = pathlib.Path(pathOnly)
          shutil.rmtree(path)
#          quit("stopping to debug.")
#///          callInstanceManager.saveKeyFile(destinationCallInstance, instanceName, cloud, source_keys_file_and_path, dest_keys_file_and_path, org, **inputVars)
#          quit("stopping to debug.")

#...............................
        ############################################################################################################################
        callInstanceManager.cleanupAfterOperation(destinationCallInstance, destinationCallParent, dynamicVarsPath, foundationInstanceName, templateName, instanceName, key_source, tfvars_file_and_path)
      else:  
        print("-------------------------------------------------------------------------------------------------------------------------------")
        msgStr = "ERROR: Failed to off this instance named: " + instanceName + ".  Halting program here so you can examine what went wrong and fix the problem before re-running the program. "
        quit(msgStr)
    else:  
      msgStr = "The instance specified as \"" + instanceName + "\" does not have any corresponding call to a module that might manage it.  Either it does not exist or it is outside the scope of this program.  Specifically, the following directory does not exist: " + destinationAutoScalingSubnetCallInstance + "  Therefore, we are not processing the request to remove the instance named: \"" + instanceName + "\""
      quit(msgStr)


  if typeGrandChild != None:
    if typeGrandChild == 'code' and (operation == 'output'):
      print("end buildRepoListOfTuples is: ", buildRepoListOfTuples)


def packerCrudOperation(operation, typeName, instanceNames, **inputVars):
  yaml_infra_config_file_and_path = inputVars.get('yamlInfraConfigFileAndPath')
  foundationInstanceName = configReader.getFoundationInstanceName(yaml_infra_config_file_and_path)
  cloud = configReader.getCloudName(yaml_infra_config_file_and_path)
  app_parent_path = inputVars.get('app_parent_path')
  module_config_file_and_path = ''
  print("module_config_file_and_path is: ", module_config_file_and_path)
  if len(cloud) < 2:
    quit("ERROR: cloud name not valid.  Add better validation checking to the code. ")
  for instanceName in instanceNames: 
    #1. First assemble the variables
    templateName = configReader.getImageTemplateName(yaml_infra_config_file_and_path, typeName, instanceName)  
    template_config_file_name = 'empty'
    if templateName.count('/') == 2:
      nameParts = templateName.split("/")
      if (len(nameParts[0]) > 1) and (len(nameParts[1]) >1) and (len(nameParts[2]) > 1):
        relative_path_to_instances = nameParts[0] + '\\' + nameParts[1]
        template_Name = nameParts[2]  
        path_to_application_root = app_parent_path + nameParts[0] + "\\" + nameParts[1] + "\\"
        module_config_file_and_path = app_parent_path + nameParts[0] + '\\variableMaps\\' + template_Name + '.csv'
        template_config_file_name = app_parent_path + nameParts[0] + '\\packer\\' + template_Name + '.json'
        startup_script_file_and_path = app_parent_path + nameParts[0] + '\\scripts\\' + 'fileName'
      else:
        quit('ERROR: templateName is not valid. ')
    else:  
      quit("Template name is not valid.  Must have only one /.  ")
    yaml_keys_file_and_path = commandBuilder.getKeyFileAndPath(typeName, cloud, **inputVars)
    print("module_config_file_and_path is: ", module_config_file_and_path)
    print("startup_script_file_and_path is: ", startup_script_file_and_path)
    #3. Then third assemble and run command
    callInstanceManager.assembleAndRunPackerCommand(cloud, templateName, operation, yaml_infra_config_file_and_path, yaml_keys_file_and_path, foundationInstanceName, instanceName, typeName, module_config_file_and_path, template_config_file_name, startup_script_file_and_path, **inputVars)

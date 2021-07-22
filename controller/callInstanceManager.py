## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import fileinput 
import os 
import platform
from distutils.dir_util import copy_tree
from pathlib import Path
import shutil
import json
import yaml

import commandBuilder
import commandRunner
import configReader

def changePointerLineInCallToModule(fileName, searchTerm, newPointerLine): 
  with fileinput.FileInput(fileName, inplace = True) as f: 
    for line in f: 
      if searchTerm in line: 
        print(newPointerLine, end ='\n') 
      else: 
        print(line, end ='') 

def deleteWrongOSPointerLineInCallToNodule(fileName, searchTerm): 
  with fileinput.FileInput(fileName, inplace = True) as f: 
    for line in f: 
      if searchTerm in line: 
        print('', end ='\n') 
      else: 
        print(line, end ='') 

def createBackendConfigFileTerraform(dir_to_use_net, **params): 
  resource_group_name = params.get('resGroupName')
  storage_account_name_terraform_backend = params.get('storageAccountNameTerraformBackend')
  storage_container_name = params.get('storContainerName')
  terra_key_file_name = params.get('keyFileTF')
  resourceGroupNameLine="    resource_group_name  = \""+resource_group_name+"\"\n"	
  storageAccountNameTerraformBackendLine="    storage_account_name = \""+storage_account_name_terraform_backend+"\"\n"	
  storageContainerNameLine="    container_name       = \""+storage_container_name+"\"\n"	
  terraBackendKeyLine="    key                  = \""+terra_key_file_name+"\"\n"	
  tfFileNameAndPath=dir_to_use_net+"/terraform.tf" 
  f = open(tfFileNameAndPath, "w")	
  f.write("terraform {\n")	
  f.write("  backend \"azurerm\" {\n")	
  f.write(resourceGroupNameLine)	
  f.write(storageAccountNameTerraformBackendLine)	
  f.write(storageContainerNameLine)	
  f.write(terraBackendKeyLine)	
  f.write("  }\n")	
  f.write("}\n")	
  f.close()	

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

def createCallDirectoryAndFile(sourceOfCallTemplate, destinationCallInstance, newPointerLineWindows, newPointerLineLinux, oldTfStateName, keySource, dynamicVarsPath, foundationInstanceName, templateName, instanceName):
  Path(destinationCallInstance).mkdir(parents=True, exist_ok=True)
  copy_tree(sourceOfCallTemplate, destinationCallInstance)
  fileName = destinationCallInstance + "main.tf"
  if platform.system() == 'Windows':
    searchTerm = "/modules/"
    deleteWrongOSPointerLineInCallToNodule(fileName, searchTerm)
    searchTerm = "\\modules\\"
    changePointerLineInCallToModule(fileName, searchTerm, newPointerLineWindows)
  else: 
    searchTerm = "\\modules\\"
    deleteWrongOSPointerLineInCallToNodule(fileName, searchTerm)
    searchTerm = "/modules/"
    changePointerLineInCallToModule(fileName, searchTerm, newPointerLineLinux)
  if keySource != "keyVault":
    if(checkIfFileExists(oldTfStateName)):
      print("oldTfStateName file exists. Copying the backup tfstate file into this directory to use again.")
      destStateFile = destinationCallInstance + "terraform.tfstate"
      print("destStateFile is: ", destStateFile)
      shutil.copyfile(oldTfStateName, destStateFile)
    else:
      print("oldTfStateName files does NOT exist. ")

def initializeTerraformBackend(keyFile, destinationCallInstance, **inputVars):
  binariesPath = inputVars.get('dependenciesBinariesPath') 
  kw = inputVars.get('tfBkndAzureParams')
  keySource = inputVars.get('keySource')

  if keySource == "keyVault":
    kw['keyFileTF']  =  keyFile 
    demoStorageKey = kw["storageKey"]
    createBackendConfigFileTerraform(destinationCallInstance, **kw) 
    initCommand= binariesPath + "terraform init -backend=true -backend-config=\"access_key="+demoStorageKey+"\""  	
  else:
    initCommand = binariesPath + 'terraform init '
  commandRunner.runTerraformCommand(initCommand, destinationCallInstance )	
  #Add error handling to validate that init command succeeded.

def instantiateCallToModule(path_To_ApplicationRoot, instanceName, templateName, oldTfStateName, **invars):
  yamlConfigFileAndPath = invars.get('yamlInfraConfigFileAndPath')
  foundationInstanceName = configReader.getFoundationInstanceName(yamlConfigFileAndPath)
  relativePathTemplate = "\\calls-to-modules\\templates\\" + templateName + "\\"
  keySource = invars.get('keySource')
  if templateName == 'network-foundation':
    relativePathInstance = "\\calls-to-modules\\instances\\" + templateName + "\\"+foundationInstanceName+"-" + templateName + "\\"  
    keyFile = foundationInstanceName + "-" + templateName  
  else:
    relativePathInstance = "\\calls-to-modules\\instances\\" + templateName + "\\"+foundationInstanceName+"-"+instanceName+"-" + templateName + "\\"  
    keyFile = foundationInstanceName + "-" + instanceName + "-" + templateName  
  sourceOfCallTemplate = convertPathForOS(path_To_ApplicationRoot, relativePathTemplate)
  destinationCallInstance = convertPathForOS(path_To_ApplicationRoot, relativePathInstance)
  p = Path(destinationCallInstance)
  if p.exists():
    print("The instance of the call to module already exists.")
  else:
    dynamicVarsPath = invars.get('dynamicVarsPath')
    newPointerLineWindows="  source = \"..\\\..\\\..\\\..\\\modules\\\\" + templateName + "\""
    newPointerLineLinux="  source = \"../../../../modules/" + templateName + "\""
    createCallDirectoryAndFile(sourceOfCallTemplate, destinationCallInstance, newPointerLineWindows, newPointerLineLinux, oldTfStateName, keySource, dynamicVarsPath, foundationInstanceName, templateName, instanceName)
  initializeTerraformBackend(keyFile, destinationCallInstance, **invars)
  return destinationCallInstance

def offInstanceOfCallToModule(locationOfCallInstance, parentDirOfCallInstance):
  if os.path.exists(locationOfCallInstance) and os.path.isdir(locationOfCallInstance):
    path = Path(locationOfCallInstance)
    shutil.rmtree(path)
  else:
    print("Given Directory doesn't exist: ", locationOfCallInstance)
  if os.path.exists(parentDirOfCallInstance) and os.path.isdir(parentDirOfCallInstance):
    if not os.listdir(parentDirOfCallInstance):
      print("Directory is empty")
      path = Path(parentDirOfCallInstance)
      shutil.rmtree(path)
    else:    
      print("Parent directory is not empty, so we will keep it for now: ", parentDirOfCallInstance)
  else:
    print("Given Directory doesn't exist: ", parentDirOfCallInstance)

def getBackedUpStateFileName(absPath, foundationInstance, templateNm, instanceNm):
  template_name = templateNm.replace('/', '__')
  backedUpStateFileName = absPath + '\\terraform_tfstate_' + foundationInstance + '-' + template_name + '-' + instanceNm + '.backup'
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

def saveKeyFile(destinationCallInst, cloudprov, yaml_keys_file_and_path, **inVars):  
  ### Save the newly-generated keys
  tfStateFile = destinationCallInst + 'terraform.tfstate'
  data = json.load(open(tfStateFile, 'r'))
  if cloudprov == 'aws':
    saveAWSKeyFile(data["resources"], **inVars)
  elif cloudprov == 'azure':
    saveAzureKeyFile(data["resources"], yaml_keys_file_and_path, **inVars)

def saveAWSKeyFile(data_resources, **input_vars): 
  for i in data_resources:
    if i["type"] == 'aws_iam_access_key': 
      pubKey = i['instances'][0]['attributes']['id']
      secKey = i['instances'][0]['attributes']['secret']
      #Next: Save the new IAM user's keys in a yaml file for use creating and offing infrastructure.  NOTE: save this to a secrets vault instead of a file if you are using a vault.
      dict_file = [{'keyPairs' : [{'name': 'demoKeyPair', '_public_access_key': pubKey, '_secret_access_key': secKey} ]}]
      yamlKeysNetworkFileAndPath = input_vars.get('dirOfYamlKeys') + input_vars.get('nameOfYamlKeys_AWS_Network_File')
      with open(yamlKeysNetworkFileAndPath, 'w') as file:
        documents = yaml.dump(dict_file, file)

def saveAzureKeyFile(data_resources, src_yaml_keys_file_and_path, **input_vars):
  appId = commandRunner.appId
  secKey = 'empty'
  for i in data_resources:
    if i["type"] == 'azuread_service_principal_password': 
      secKey = i['instances'][0]['attributes']['value']
      if appId.startswith('"') and appId.endswith('"'):
        appId = appId[1:-1]
  myList = []
  with open(src_yaml_keys_file_and_path, 'r') as file:
    keys = yaml.safe_load(file)
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
        itemStr = key + ": "+ secKey
        myList.append(itemStr)
      else: 
        itemStr = key + ": "+ keys.get(key)
        myList.append(itemStr)
  dictVersion = {}
  for key_value in myList:
    key, value = key_value.split(': ', 1)
    dictVersion[key] = value
  yamlKeysNetworkFileAndPath = input_vars.get('dirOfYamlKeys') + input_vars.get('nameOfYamlKeys_Azure_Network_File')
  with open(yamlKeysNetworkFileAndPath, 'w') as file:
    documents = yaml.dump(dictVersion, file)

def assembleAndRunCommand(cloud, template_Name, operation, yaml_infra_config_file_and_path, yaml_keys_file_and_path, foundationInstanceName, parentInstanceName, instanceName, destinationCallInstance, typeName, module_config_file_and_path, **inputVars):
  configAndSecretsPath = inputVars.get('configAndSecretsPath')
  dirOfConfig = configAndSecretsPath + "vars\\config\\" + cloud + "\\"
  moduleConfigFileAndPath = module_config_file_and_path
  commandToRun = 'invalid value must be reset below'
  tool = "terraform"

  binariesPath = inputVars.get('dependenciesBinariesPath') 

  if operation == 'off':
    #Passing foundationInstanceName into getVarsFragment because we want to use the keys associated with the network foundation when we are attaching anything to the network foundation.
    varsFrag = commandBuilder.getVarsFragment(tool, yaml_infra_config_file_and_path, moduleConfigFileAndPath, yaml_keys_file_and_path, foundationInstanceName, parentInstanceName, instanceName, **inputVars)
    commandToRun = binariesPath + "terraform destroy -auto-approve" + varsFrag
  elif operation == 'on':
    #Passing foundationInstanceName into getVarsFragment because we want to use the keys associated with the network foundation when we are attaching anything to the network foundation.
    varsFrag = commandBuilder.getVarsFragment(tool, yaml_infra_config_file_and_path, moduleConfigFileAndPath, yaml_keys_file_and_path, foundationInstanceName, parentInstanceName, instanceName, **inputVars)
    commandToRun = binariesPath + "terraform apply -auto-approve -parallelism=1 " + varsFrag
#    print("instanceName is: ", instanceName)
#    if instanceName == 'azdoAgents':
#      print("commandToRun is: ", commandToRun)
#      quit("DEBUG POINT")
  elif operation == 'output':
    commandToRun = binariesPath + 'terraform output'
  else:
    quit("Error: Invalid value for operation: ", operation)
  print("commandToRun is: ", commandToRun)
  commandRunner.runTerraformCommand(commandToRun, destinationCallInstance)  
  if (typeName == 'admin') and (operation == 'on') and (commandRunner.terraformResult == "Applied"): 
    print("About to saveKeyFile. ")
    saveKeyFile(destinationCallInstance, cloud, yaml_keys_file_and_path, **inputVars)

def setDoCleanUp(oper):
  cleanup = False
  if oper == 'on':
    if commandRunner.terraformResult == "Applied": 
      cleanup = True
  elif oper == 'off':
    if commandRunner.terraformResult == "Destroyed": 
      cleanup = True
  elif oper == 'output':
    #Add some check here to confirm that the output operation succeeded.
    cleanup = True
  return cleanup

def cleanupAfterOperation(destinationCallInstance, destinationCallParent, dynamicVarsPath, foundationInstanceName, templateName, instanceName, key_source, tfvars_file_and_path):
  if key_source =="keyFile":
    #Now make a backup copy of the tfstate file.
    tfStateSrc = destinationCallInstance + 'terraform.tfstate'
    tfStateDest = getBackedUpStateFileName(dynamicVarsPath, foundationInstanceName, templateName, instanceName)
    if os.path.isfile(tfStateSrc):
      shutil.copy(tfStateSrc, tfStateDest)
  offInstanceOfCallToModule(destinationCallInstance, destinationCallParent)
  ###############################################################################
  ### Delete the tfvars file and the instance of the call to module
  ### Note we only want keys to be in external locations such as a vault
  ###############################################################################
  try:
    print("About to remove the tfvars file. ")
#    os.remove(tfvars_file_and_path)
  except OSError:
    pass

def assembleAndRunPackerCommand(cloud, template_Name, operation, yaml_infra_config_file_and_path, yaml_keys_file_and_path, foundationInstanceName, instanceName, typeName, moduleConfigFileAndPath, template_config_file_name, startup_script_file_and_path, **inputVars):
  commandToRun = 'invalid value must be reset below'
  tool = "packer"
  imageRepoDir = configReader.getImageRepoDir(yaml_infra_config_file_and_path, template_Name)
  binariesPath = inputVars.get('dependenciesBinariesPath') 

  if operation == 'build':
    #Passing foundationInstanceName into getVarsFragment because we want to use the keys associated with the network foundation when we are attaching anything to the network foundation.
    varsFrag = commandBuilder.getVarsFragment(tool, yaml_infra_config_file_and_path, moduleConfigFileAndPath, yaml_keys_file_and_path, foundationInstanceName, None, instanceName, **inputVars)
    #commandToRun = "packer build -debug " + varsFrag + " " + template_config_file_name
    commandToRun = binariesPath + "packer build " + varsFrag + " " + template_config_file_name
  else:
    quit("Error: Invalid value for operation: ", operation)
  print("commandToRun is: ", commandToRun)
  print("''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''")
  print("imageRepoDir is: ", imageRepoDir)
  print("''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''")
  print("yaml_infra_config_file_and_path is: ", yaml_infra_config_file_and_path)
  print("moduleConfigFileAndPath is: ", moduleConfigFileAndPath)
  print("yaml_keys_file_and_path is: ", yaml_keys_file_and_path)
  #quit("Hi Ho Silver")
  commandRunner.runPackerCommand(commandToRun, imageRepoDir, **inputVars)
  if commandRunner.success_packer == "false":
    print("commandRunner.success_packer is false")
    quit("Halting program inside assembleAndRunPackerCommand() so that you can debug the error that should be stated above in the output.  ")

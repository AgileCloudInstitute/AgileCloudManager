## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import json
import yaml
import re
import sys  
import requests
import os
import base64

import config_fileprocessor
import command_runner
import command_builder
import controller_terraform
import logWriter
import config_cliprocessor

def onPipeline(command, systemInstanceName, iName, infraConfigFileAndPath, keyDir):
  projName = config_fileprocessor.getSecondLevelProperty(infraConfigFileAndPath, 'systems', 'releaseDefinitions', iName, 'projectName')  
  operation = "output"
  controller_terraform.terraformCrudOperation(operation, systemInstanceName, keyDir, infraConfigFileAndPath, 'systems', 'projects', None, None, projName)
  #Get the following 2:
  azuredevops_project_id = command_runner.azuredevops_project_id
  azuredevops_service_connection_id = command_runner.azuredevops_service_connection_id
  #Next: get code instance names
  typeParent = 'systems'
  typeName = 'projects'
  cloud = config_fileprocessor.getCloudName(infraConfigFileAndPath)
  if len(cloud) < 2:
    logString = "ERROR: cloud name not valid.  Add better validation checking to the code. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  if cloud == 'azure':
    yaml_keys_file_and_path = command_builder.getKeyFileAndPath(keyDir, typeName, cloud)
    clientId = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
    clientSecret = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret') 
    tenantId = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
    #### #The following command gets the client logged in and able to operate on azure repositories.
    myCmd = "az login --service-principal -u " + clientId + " -p " + clientSecret + " --tenant " + tenantId
    command_runner.runShellCommand(myCmd)
    codeInstanceNames = config_fileprocessor.getSystemInstanceNames(infraConfigFileAndPath, 'projects')
    #NOTE: ESTABLISH RULES FOR A SCHEMA INCLUDING RELATIONSHIP BETWEEN PROJECTS, code, AND RELEASE DEFINITIONS, AND THEN FILTER INSTANCE NAMES TO ONLY RETURN INSTANCES THAT MATCH SCHEMA RULES.  
    operation = 'output'
    for codeInstanceName in codeInstanceNames:
      controller_terraform.terraformCrudOperation(operation, systemInstanceName, keyDir, infraConfigFileAndPath, typeParent, 'projects', projName, typeName, codeInstanceName)
    logString = "done with -- " + typeName + " -----------------------------------------------------------------------------"
    logWriter.writeLogVerbose("acm", logString)
    orgServiceURL = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgServiceURL')
    orgServiceURL = orgServiceURL.replace('"','')
    orgServiceURL = orgServiceURL.replace("'","")
    if orgServiceURL[len(orgServiceURL)-1] != '/':
      orgServiceURL = orgServiceURL + '/'
    organization = orgServiceURL.rsplit('/')[3]
    azPat = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgPAT')
    azPat = azPat.replace('"','')
    azPat = azPat.replace("'","")
    azuredevops_project_id = azuredevops_project_id.replace('"','')
    queue_name = "Default"
    poolQueueId = command_runner.getPoolQueueIdApiRequest(organization, azuredevops_project_id, queue_name, azPat)
    dirOfReleaseDefJsonParts = config_cliprocessor.inputVars.get('dirOfReleaseDefJsonParts')
    #////////////////////////////////////////////////////////////////////////////////////////////////////////
    #// Step Three: Convert YAML definition to JSON data
    #////////////////////////////////////////////////////////////////////////////////////////////////////////
    yamlDir = config_cliprocessor.inputVars.get('dirOfReleaseDefYaml')
    YamlReleaseDefFile = config_fileprocessor.getSecondLevelProperty(infraConfigFileAndPath, 'systems', 'releaseDefinitions', iName, 'YamlDefinitionFileName')  
    yamlFile = yamlDir + YamlReleaseDefFile
    deployPhaseTemplateFile = dirOfReleaseDefJsonParts + 'deployPhaseTemplate.json'
    environmentTemplateFile = dirOfReleaseDefJsonParts + 'environmentTemplate.json'
    releaseDefConstructorTemplateFile = dirOfReleaseDefJsonParts + 'releaseDefConstructorTemplate.json'
    artifactsTemplateFile = dirOfReleaseDefJsonParts + 'artifactsTemplate.json'
    vaultName = config_fileprocessor.getSecondLevelProperty(infraConfigFileAndPath, 'systems', 'releaseDefinitions', iName, 'vaultName')  
    try:
      releaseDefData = getReleaseDefData(yamlFile, dirOfReleaseDefJsonParts, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, artifactsTemplateFile, poolQueueId, azuredevops_project_id, orgServiceURL, projName, vaultName, azuredevops_service_connection_id)
    except Exception as e:
      logString = "ERROR: The following exception was thrown while calling getReleaseDefData(...):  "
      logWriter.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      logWriter.writeLogVerbose("acm", logString)
      exit(1)
    logString = "--------------------------------------------------------"
    logWriter.writeLogVerbose("acm", logString)
    logString = "revised releaseDefData is: "
    logWriter.writeLogVerbose("acm", logString)
    try:
      logString = releaseDefData
      logWriter.writeLogVerbose("acm", logString)
    except Exception as e:
      logString = "ERROR: The following exception was thrown while trying to write releaseDefData to the log:  "
      logWriter.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      logWriter.writeLogVerbose("acm", logString)
      exit(1)
    logString = "--------------------------------------------------------"
    logWriter.writeLogVerbose("acm", logString)
    #//////////////////////////////////////////////////////////////////////////////////////////////
    #// Step Four: Create Release Definition By Making API Call.
    #//////////////////////////////////////////////////////////////////////////////////////////////
#--this next line is where it is breaking
    try: 
      rCode = createReleaseDefinitionApiRequest(releaseDefData, organization, azuredevops_project_id, azPat)
    except Exception as e:
      logString = "ERROR: The following exception was thrown by createReleaseDefinitionApiRequest(...):  "
      logWriter.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      logWriter.writeLogVerbose("acm", logString)
      exit(1)
    logString = "response code from create release definition API call is: "
    logWriter.writeLogVerbose("acm", logString)
    try:
      logString = str(rCode)
      logWriter.writeLogVerbose("acm", logString)
    except Exception as e:
      logString = "ERROR: The following exception was thrown while trying to write response code from the create release definition API call to the log:  "
      logWriter.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      logWriter.writeLogVerbose("acm", logString)
      exit(1)
  else:
    logString = "Halting program because currently Azure DevOps is the only tool supported for release definitions.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  
def getPythonTaskData(task_idx, dirOfReleaseDefJsonParts, task):  
  pythonTaskTemplateFile = dirOfReleaseDefJsonParts + 'pythonTaskTemplate.json'  
  pythonTaskData = json.load(open(pythonTaskTemplateFile, 'r'))  
  for task_item in task:  
    if re.match("name", task_item):  
      pythonTaskData['name'] = task.get(task_item)
    if re.match("type", task_item):  
      if re.match("Python", task.get(task_item)): 
        pythonTaskData['taskId'] = '6392f95f-7e76-4a18-b3c7-7f078d2f7700'
    if re.match("scriptPath", task_item):  
      pythonTaskData['inputs']['scriptPath'] = task.get(task_item)
    if re.match("arguments", task_item):  
      pythonTaskData['inputs']['arguments'] = task.get(task_item)
  return pythonTaskData

def getKeyVaultTaskData(key_vault_name, dirOfReleaseDefJsonParts, key_vault_service_connection_id):  
  keyVaultTaskTemplateFile = dirOfReleaseDefJsonParts + 'keyVaultTaskTemplate.json'
  keyVaultTaskData = json.load(open(keyVaultTaskTemplateFile, 'r'))  
  key_vault_service_connection_id = key_vault_service_connection_id.strip('\"')
  keyVaultTaskData['name'] = "Azure Key Vault: " + key_vault_name
  keyVaultTaskData['inputs']['ConnectedServiceName'] = key_vault_service_connection_id
  keyVaultTaskData['inputs']['KeyVaultName'] = key_vault_name
  return keyVaultTaskData

def getWorkflowTasksList(workflowTasksList, dirOfReleaseDefJsonParts, key_vault_name, key_vault_service_connection_id):
  taskDataList = []
  if len(key_vault_name) > 3:
    taskData = getKeyVaultTaskData(key_vault_name, dirOfReleaseDefJsonParts, key_vault_service_connection_id)
    taskDataList.append(taskData)
  for task_idx, task in enumerate(workflowTasksList):
    if task['type'] == 'Python':
      taskData = getPythonTaskData(task_idx, dirOfReleaseDefJsonParts, task)
      taskDataList.append(taskData)
  return taskDataList

def getDeploymentInput(poolQueueId, dirOfReleaseDefJsonParts, deploymentInput):  
  #This will later need to receive the user-supplied YAML fragment as input when the params are changed to allow the YAML to specify artifacts, etc.  
  depInputTemplateFile = dirOfReleaseDefJsonParts + 'deploymentInputTemplate.json'  
  depInputData = json.load(open(depInputTemplateFile, 'r'))  
  downloadInputsList = []  
  for dInput in deploymentInput:  
    for dep_item in dInput:
      if re.match("artifactsDownloadInput", dep_item):  
        artifactsList = dInput.get(dep_item)  
        for artifact in artifactsList:  
          artifactDownloadInputTemplateFile = dirOfReleaseDefJsonParts + 'downloadInputArtifactTemplate.json'  
          artifactData = json.load(open(artifactDownloadInputTemplateFile, 'r'))  
          for artifact_item in artifact:
            if re.match("alias", artifact_item):  
              artifactData['alias'] = artifact.get(artifact_item)  
          downloadInputsList.append(artifactData)  
        dinputsData = {"downloadInputs": []}
        dinputsData['downloadInputs'] = downloadInputsList
  depInputData['artifactsDownloadInput'] = dinputsData
  depInputData['queueId'] = poolQueueId
  return depInputData
  
def getDeploymentPhaseData(phase_idx, dirOfReleaseDefJsonParts, deployPhase, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id):
  deployPhaseData = json.load(open(deployPhaseTemplateFile, 'r'))
  #Now iterate the YAML input
  for depPhase_item in deployPhase:  
    if re.match("name", depPhase_item):  
      deployPhaseData['name'] = deployPhase.get(depPhase_item)
    if re.match("deploymentInput", depPhase_item):  
      depInput = getDeploymentInput(poolQueueId, dirOfReleaseDefJsonParts, deployPhase.get(depPhase_item))  
      deployPhaseData['deploymentInput'] = depInput  
    if re.match("workflowTasks", depPhase_item):  
      taskDataList = getWorkflowTasksList(deployPhase.get(depPhase_item), dirOfReleaseDefJsonParts, key_vault_name, key_vault_service_connection_id)
      deployPhaseData['workflowTasks'] = taskDataList
  return deployPhaseData

def getEnvironmentData(env_idx, dirOfReleaseDefJsonParts, environment, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id):
  environmentData = json.load(open(environmentTemplateFile, 'r'))
  for env_item in environment:  
    if re.match("name", env_item):  
      environmentData['name'] = environment.get(env_item)  
    if re.match("deployPhases", env_item):  
      deployPhaseList = environment.get(env_item)  
      deployPhaseDataList = []  
      for phase_idx, deployPhase in enumerate(deployPhaseList):  
        deployPhaseData = getDeploymentPhaseData(phase_idx, dirOfReleaseDefJsonParts, deployPhase, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id)  
        deployPhaseDataList.append(deployPhaseData)
      environmentData['deployPhases'] = deployPhaseDataList 
  stageIdx = env_idx+1
  environmentData['rank'] = stageIdx
  return environmentData

def getEnvironmentsDataList(environmentsList, dirOfReleaseDefJsonParts, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id):
  environmentsDataList = []
  for env_idx, environment in enumerate(environmentsList):
    environmentData = getEnvironmentData(env_idx, dirOfReleaseDefJsonParts, environment, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id)
    environmentsDataList.append(environmentData)
  return environmentsDataList

def getVariablesData(variablesYAML):
  idx = 1
  varJsonListItems = ""
  for varsList in variablesYAML:
    lastIndex = len(varsList)
    for var in varsList:
      varJSON = " \""+ var + "\":{ \"value\":\""+varsList.get(var)+"\"}"
      varJsonListItems = varJsonListItems + varJSON
      #The following check assumes that all variable items are valid and are handled by if cases here.  This could cause malformed JSON if received data is not valid or is not handled in if cases here.
      if idx < lastIndex:
        varJsonListItems = varJsonListItems + ", "
      idx += 1  
  varOutputString = "{ " + varJsonListItems + " }"
  varOutputString = varOutputString.replace(" ", "")
  varOutputData = json.loads(varOutputString)
  return varOutputData

def getReleaseDefData(yamlInputFile, dirOfReleaseDefJsonParts, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, artifactsTemplateFile, poolQueueId, azdo_project_id, azdo_organization_service_url, azdo_project_name, key_vault_name, key_vault_service_connection_id):
  with open(yamlInputFile) as f:
    releaseDef_dict = yaml.safe_load(f)
    releaseDefData = json.load(open(releaseDefConstructorTemplateFile, 'r'))
    for item in releaseDef_dict:
      if re.match("name", item):
        releaseDefData['name'] = releaseDef_dict.get(item)
      if re.match("description", item):
        releaseDefData['description'] = releaseDef_dict.get(item)
      if re.match("environments", item):
        environmentsDataList = getEnvironmentsDataList(releaseDef_dict.get(item), dirOfReleaseDefJsonParts, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id)
        releaseDefData['environments'] = environmentsDataList
      if re.match("variables", item):
        variablesData = getVariablesData(releaseDef_dict.get(item))
        releaseDefData['variables'] = variablesData
    return releaseDefData

def createReleaseDefinitionApiRequest(data, azdo_organization_name, azdo_project_id, azPAT):
    personal_access_token = ":"+azPAT
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
    api_version = "5.1"
    url = ("https://vsrm.dev.azure.com/%s/%s/_apis/release/definitions?api-version=%s" % (azdo_organization_name, azdo_project_id, api_version))
    r = requests.post(url, data=json.dumps(data), headers=headers)
    respCode = r.status_code
    logString = "r.status_code is: "
    logWriter.writeLogVerbose("acm", logString)
    logString = str(respCode)
    logWriter.writeLogVerbose("acm", logString)
    logString = "r.json() is: "
    logWriter.writeLogVerbose("acm", logString)
    logString = json.dumps(r.json())
    logWriter.writeLogVerbose("acm", logString)
    return respCode

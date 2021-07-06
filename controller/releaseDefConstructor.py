## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import json
import yaml
import re
import sys  
import requests
import os
import base64


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

def getArtifactsDataList(artifactsTemplateFile, project_id, org_service_url, project_name, buildRepoListOfTuples):
  artifactsDataList = [] 
  for buildRepoTuple in buildRepoListOfTuples:
    buildDefId = buildRepoTuple[0]
    repoName = buildRepoTuple[1]
    artifactsData = json.load(open(artifactsTemplateFile, 'r'))
    artifact_alias = "_" + repoName
    artifactsData['sourceId'] = project_id + ":" + str(buildDefId)
    artifactsData['artifactSourceDefinitionUrl']['id'] = org_service_url + project_name + "/_build?definitionId=" + str(buildDefId)
    artifactsData['alias'] = artifact_alias
    artifactsData['definitionReference']['definition']['id'] = buildDefId
    artifactsData['definitionReference']['definition']['name'] = repoName
    artifactsData['definitionReference']['project']['id'] = project_id
    artifactsData['definitionReference']['project']['name'] = project_name
    ##Only one artifact can be designated isPrimary=true.  Later we can add a flag to specify which one isPrimary.  For now, we are marking all as false to avoid throwing an error in the API call.  
    artifactsData['isPrimary'] = "false"
    artifactsDataList.append(artifactsData)
  return artifactsDataList

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

def getReleaseDefData(yamlInputFile, dirOfReleaseDefJsonParts, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, artifactsTemplateFile, poolQueueId, azdo_project_id, azdo_organization_service_url, azdo_project_name, buildRepoListOfTuples, key_vault_name, key_vault_service_connection_id):
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
    artifactsDataList = getArtifactsDataList(artifactsTemplateFile, azdo_project_id, azdo_organization_service_url, azdo_project_name, buildRepoListOfTuples)
    releaseDefData['artifacts'] = artifactsDataList
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
    print("r.status_code is: ", respCode)
    print("r.json() is: ", r.json())
    return respCode

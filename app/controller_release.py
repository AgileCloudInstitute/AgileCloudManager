## Copyright 2024 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

import json  
import yaml  
import re  
import sys    
import requests  
import base64  

from command_runner import command_runner  
from command_formatter import command_formatter  
from controller_terraform import controller_terraform  
from log_writer import log_writer  
from config_fileprocessor import config_fileprocessor  
  
class controller_release:  
  
  def __init__(self):    
    pass  
 
  #@public
  def onPipeline(self, serviceType, systemConfig, instance):
    import config_cliprocessor
    crnr = command_runner()
    cmd_fmtr = command_formatter()
    ctf = controller_terraform()
    lw = log_writer()
    cfp = config_fileprocessor()
    keyDir = cfp.getKeyDir(systemConfig)
    projName = instance.get('projectName')
    operation = "output"
    ctf.terraformCrudOperation(operation, keyDir, systemConfig, instance, 'systems', serviceType, None, projName)
    #Get the following 2:
    if ('azuredevops_project_id' in ctf.tfOutputDict.keys()) and ('azuredevops_service_connection_id' in ctf.tfOutputDict.keys()):
      azuredevops_project_id = ctf.tfOutputDict['azuredevops_project_id']
      azuredevops_service_connection_id = ctf.tfOutputDict['azuredevops_service_connection_id']
    else:
      logString = "ERROR: The terraform module that creates the Azure Devops Project must have output variables named azuredevops_project_id and azuredevops_service_connection_id which each contain a valid id.  Since the module you are using does not have both an azuredevops_project_id and an azuredevops_service_connection_id output variable, the program is halting so you can fix the problem and rerun the command that got you here.  "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    #Next: get code instance names
    typeName = 'projects'
    cloud = systemConfig.get("cloud")
    if len(cloud) < 2:
      logString = "ERROR: cloud name not valid.  Add better validation checking to the code. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    if cloud == 'azure':
      yaml_keys_file_and_path = cmd_fmtr.getKeyFileAndPath(keyDir)
      clientId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
      clientSecret = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret') 
      tenantId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
      #### #The following command gets the client logged in and able to operate on azure repositories.
      myCmd = "az login --service-principal -u " + clientId + " -p " + clientSecret + " --tenant " + tenantId
      crnr.runShellCommand(myCmd)
      #NOTE: ESTABLISH RULES FOR A SCHEMA INCLUDING RELATIONSHIP BETWEEN PROJECTS, code, AND RELEASE DEFINITIONS, AND THEN FILTER INSTANCE NAMES TO ONLY RETURN INSTANCES THAT MATCH SCHEMA RULES.  
      logString = "done with -- " + typeName + " -----------------------------------------------------------------------------"
      lw.writeLogVerbose("acm", logString)
      orgServiceURL = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgServiceURL')
      orgServiceURL = orgServiceURL.replace('"','')
      orgServiceURL = orgServiceURL.replace("'","")
      if orgServiceURL[len(orgServiceURL)-1] != '/':
        orgServiceURL = orgServiceURL + '/'
      organization = orgServiceURL.rsplit('/')[3]
      azPat = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgPAT')
      azPat = azPat.replace('"','')
      azPat = azPat.replace("'","")
      azuredevops_project_id = azuredevops_project_id.replace('"','')
      queue_name = "Default"
      poolQueueId = crnr.getPoolQueueIdApiRequest(organization, azuredevops_project_id, queue_name, azPat)
      dirOfReleaseDefJsonParts = config_cliprocessor.inputVars.get('dirOfReleaseDefJsonParts')
      #////////////////////////////////////////////////////////////////////////////////////////////////////////
      #// Step Three: Convert YAML definition to JSON data
      #////////////////////////////////////////////////////////////////////////////////////////////////////////
      userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
      YamlReleaseDefFile = instance.get('templateName')
      yamlFile = userCallingDir + cmd_fmtr.getSlashForOS() + YamlReleaseDefFile
      deployPhaseTemplateFile = dirOfReleaseDefJsonParts + 'deployPhaseTemplate.json'
      environmentTemplateFile = dirOfReleaseDefJsonParts + 'environmentTemplate.json'
      releaseDefConstructorTemplateFile = dirOfReleaseDefJsonParts + 'releaseDefConstructorTemplate.json'
      artifactsTemplateFile = dirOfReleaseDefJsonParts + 'artifactsTemplate.json'
      vaultName = ''
      releaseDefData = self.getReleaseDefData(yamlFile, dirOfReleaseDefJsonParts, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, artifactsTemplateFile, poolQueueId, azuredevops_project_id, orgServiceURL, projName, vaultName, azuredevops_service_connection_id)
      logString = "--------------------------------------------------------"
      lw.writeLogVerbose("acm", logString)
      logString = "revised releaseDefData is: "
      lw.writeLogVerbose("acm", logString)
      try:
        logString = releaseDefData
        lw.writeLogVerbose("acm", logString)
      except Exception as e:
        logString = "ERROR: The following exception was thrown while trying to write releaseDefData to the log:  "
        lw.writeLogVerbose("acm", logString)
        logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
        lw.writeLogVerbose("acm", logString)
        exit(1)
      logString = "--------------------------------------------------------"
      lw.writeLogVerbose("acm", logString)
      #//////////////////////////////////////////////////////////////////////////////////////////////
      #// Step Four: Create Release Definition By Making API Call.
      #//////////////////////////////////////////////////////////////////////////////////////////////
      try: 
        rCode = self.createReleaseDefinitionApiRequest(releaseDefData, organization, azuredevops_project_id, azPat)
      except Exception as e:
        logString = "ERROR: The following exception was thrown by createReleaseDefinitionApiRequest(...):  "
        lw.writeLogVerbose("acm", logString)
        logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
        lw.writeLogVerbose("acm", logString)
        exit(1)
      logString = "response code from create release definition API call is: "
      lw.writeLogVerbose("acm", logString)
      try:
        logString = str(rCode)
        lw.writeLogVerbose("acm", logString)
      except Exception as e:
        logString = "ERROR: The following exception was thrown while trying to write response code from the create release definition API call to the log:  "
        lw.writeLogVerbose("acm", logString)
        logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
        lw.writeLogVerbose("acm", logString)
        exit(1)
    else:
      logString = "Halting program because currently Azure DevOps is the only tool supported for release definitions.  "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
  
  #@private
  def getPythonTaskData(self, task_idx, dirOfReleaseDefJsonParts, task):  
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

  #@private
  def getKeyVaultTaskData(self, key_vault_name, dirOfReleaseDefJsonParts, key_vault_service_connection_id):  
    keyVaultTaskTemplateFile = dirOfReleaseDefJsonParts + 'keyVaultTaskTemplate.json'
    keyVaultTaskData = json.load(open(keyVaultTaskTemplateFile, 'r'))  
    key_vault_service_connection_id = key_vault_service_connection_id.strip('\"')
    keyVaultTaskData['name'] = "Azure Key Vault: " + key_vault_name
    keyVaultTaskData['inputs']['ConnectedServiceName'] = key_vault_service_connection_id
    keyVaultTaskData['inputs']['KeyVaultName'] = key_vault_name
    return keyVaultTaskData

  #@private
  def getWorkflowTasksList(self, workflowTasksList, dirOfReleaseDefJsonParts, key_vault_name, key_vault_service_connection_id):
    taskDataList = []
    if key_vault_name:
      taskData = self.getKeyVaultTaskData(key_vault_name, dirOfReleaseDefJsonParts, key_vault_service_connection_id)
      taskDataList.append(taskData)
    for task_idx, task in enumerate(workflowTasksList):
      if task['type'] == 'Python':
        taskData = self.getPythonTaskData(task_idx, dirOfReleaseDefJsonParts, task)
        taskDataList.append(taskData)
    return taskDataList

  #@private
  def getDeploymentInput(self, poolQueueId, dirOfReleaseDefJsonParts, deploymentInput):  
    #This will later need to receive the user-supplied YAML fragment as input when the params are changed to allow the YAML to specify artifacts, etc.  
    depInputTemplateFile = dirOfReleaseDefJsonParts + 'deploymentInputTemplate.json'  
    depInputData = json.load(open(depInputTemplateFile, 'r'))  
    downloadInputsList = []  
    dinputsData = ''
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
    if dinputsData != '':
      depInputData['artifactsDownloadInput'] = dinputsData
    depInputData['queueId'] = poolQueueId
    return depInputData
  
  #@private
  def getDeploymentPhaseData(self, phase_idx, dirOfReleaseDefJsonParts, deployPhase, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id):
    deployPhaseData = json.load(open(deployPhaseTemplateFile, 'r'))
    #Now iterate the YAML input
    for depPhase_item in deployPhase:  
      if re.match("name", depPhase_item):  
        deployPhaseData['name'] = deployPhase.get(depPhase_item)
      if re.match("deploymentInput", depPhase_item):  
        depInput = self.getDeploymentInput(poolQueueId, dirOfReleaseDefJsonParts, deployPhase.get(depPhase_item))  
        deployPhaseData['deploymentInput'] = depInput  
      if re.match("workflowTasks", depPhase_item):  
        taskDataList = self.getWorkflowTasksList(deployPhase.get(depPhase_item), dirOfReleaseDefJsonParts, key_vault_name, key_vault_service_connection_id)
        deployPhaseData['workflowTasks'] = taskDataList
    return deployPhaseData

  #@private
  def getEnvironmentData(self, env_idx, dirOfReleaseDefJsonParts, environment, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id):
    environmentData = json.load(open(environmentTemplateFile, 'r'))
    for env_item in environment:  
      if re.match("name", env_item):  
        environmentData['name'] = environment.get(env_item)  
      if re.match("deployPhases", env_item):  
        deployPhaseList = environment.get(env_item)  
        deployPhaseDataList = []  
        for phase_idx, deployPhase in enumerate(deployPhaseList):  
          deployPhaseData = self.getDeploymentPhaseData(phase_idx, dirOfReleaseDefJsonParts, deployPhase, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id)  
          deployPhaseDataList.append(deployPhaseData)
        environmentData['deployPhases'] = deployPhaseDataList 
    stageIdx = env_idx+1
    environmentData['rank'] = stageIdx
    return environmentData

  #@private
  def getEnvironmentsDataList(self, environmentsList, dirOfReleaseDefJsonParts, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id):
    environmentsDataList = []
    for env_idx, environment in enumerate(environmentsList):
      environmentData = self.getEnvironmentData(env_idx, dirOfReleaseDefJsonParts, environment, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id)
      environmentsDataList.append(environmentData)
    return environmentsDataList

  #@private
  def getVariablesData(self, variablesYAML):
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

  #@private
  def getReleaseDefData(self, yamlInputFile, dirOfReleaseDefJsonParts, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, artifactsTemplateFile, poolQueueId, azdo_project_id, azdo_organization_service_url, azdo_project_name, key_vault_name, key_vault_service_connection_id):
    with open(yamlInputFile) as f:
      releaseDef_dict = yaml.safe_load(f)
      releaseDefData = json.load(open(releaseDefConstructorTemplateFile, 'r'))
      for item in releaseDef_dict:
        if re.match("name", item):
          releaseDefData['name'] = releaseDef_dict.get(item)
        if re.match("description", item):
          releaseDefData['description'] = releaseDef_dict.get(item)
        if re.match("environments", item):
          environmentsDataList = self.getEnvironmentsDataList(releaseDef_dict.get(item), dirOfReleaseDefJsonParts, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id)
          releaseDefData['environments'] = environmentsDataList
        if re.match("variables", item):
          variablesData = self.getVariablesData(releaseDef_dict.get(item))
          releaseDefData['variables'] = variablesData
      return releaseDefData

  #@private
  def createReleaseDefinitionApiRequest(self, data, azdo_organization_name, azdo_project_id, azPAT):
    lw = log_writer()
    personal_access_token = ":"+azPAT
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
    api_version = "5.1"
    url = ("https://vsrm.dev.azure.com/%s/%s/_apis/release/definitions?api-version=%s" % (azdo_organization_name, azdo_project_id, api_version))
    r = requests.post(url, data=json.dumps(data), headers=headers)
    respCode = r.status_code
    logString = "r.status_code is: "
    lw.writeLogVerbose("acm", logString)
    logString = str(respCode)
    lw.writeLogVerbose("acm", logString)
    logString = "r.json() is: "
    lw.writeLogVerbose("acm", logString)
    logString = json.dumps(r.json())
    lw.writeLogVerbose("acm", logString)
    return respCode

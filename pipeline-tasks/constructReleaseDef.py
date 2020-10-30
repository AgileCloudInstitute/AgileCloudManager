import json
import yaml
import re
import sys  
import requests
import os
import base64
import deploymentFunctions as depfunc  

YamlReleaseDefFile=sys.argv[1] 
print("YamlReleaseDefFile is: ", YamlReleaseDefFile)
jsonFragmentDir = '../release-definitions/json-fragments/' 
  
YamlPRBFileName=sys.argv[2]   
yamlConfigDir = '/home/agile-cloud/staging/'  
myYamlInputFile = yamlConfigDir + YamlPRBFileName  
print("myYamlInputFile is: ", myYamlInputFile)  

#Environment variable set during cloud-init instantiation
acmRootDir=os.environ['ACM_ROOT_DIR']

def getPythonTaskData(task_idx, task):  
  pythonTaskTemplateFile = jsonFragmentDir + 'pythonTaskTemplate.json'  
  pythonTaskData = json.load(open(pythonTaskTemplateFile, 'r'))  
  # print("pythonTaskData is: ", pythonTaskData)  
  # print("--------------------------------------------------------")  
  # print("--------- Gonna print a new workflow task ----------------")  
  # print(task_idx, ": ", task)  
  # print("--------- Gonna decompose the workflow task ----------------")  
  for task_item in task:  
    # print(task_idx, ": ", "task_item is: ", task_item)  
    if re.match("name", task_item):  
      #print(task_idx, ": ", "name is: ", task.get(task_item))  
      pythonTaskData['name'] = task.get(task_item)
    if re.match("type", task_item):  
      # print(task_idx, ": ", "type is: ", task.get(task_item))
      if re.match("Python", task.get(task_item)): 
        pythonTaskData['taskId'] = '6392f95f-7e76-4a18-b3c7-7f078d2f7700'
    if re.match("scriptPath", task_item):  
      #print(task_idx, ": ", "scriptPath is: ", task.get(task_item))
      pythonTaskData['inputs']['scriptPath'] = task.get(task_item)
    if re.match("arguments", task_item):  
      #print(task_idx, ": ", "arguments is: ", task.get(task_item))  
      pythonTaskData['inputs']['arguments'] = task.get(task_item)
  return pythonTaskData

def getKeyVaultTaskData(key_vault_name, key_vault_service_connection_id):  
  keyVaultTaskTemplateFile = jsonFragmentDir + 'keyVaultTaskTemplate.json'
  keyVaultTaskData = json.load(open(keyVaultTaskTemplateFile, 'r'))  
  # print("keyVaultTaskData is: ", keyVaultTaskData)
  # print("--------------------------------------------------------")
  # print("--------- Gonna print a new workflow task ----------------")  
  keyVaultTaskData['name'] = "Azure Key Vault: " + key_vault_name
  keyVaultTaskData['inputs']['ConnectedServiceName'] = key_vault_service_connection_id
  keyVaultTaskData['inputs']['KeyVaultName'] = key_vault_name
  # the task id from the template file should be: '1e244d32-2dd4-4165-96fb-b7441ca9331e':
  # print("keyVaultTaskData is: ", keyVaultTaskData)
  # print("-----------------------------------------------------------")
  return keyVaultTaskData

def getWorkflowTasksList(workflowTasksList, key_vault_name, key_vault_service_connection_id):
  # print("len workflowTasksList is: ", len(workflowTasksList))
  taskDataList = []
  if len(key_vault_name) > 3:
    # print("--------------------------------------------------------")
    taskData = getKeyVaultTaskData(key_vault_name, key_vault_service_connection_id)
    taskDataList.append(taskData)
    # print("--------------------------------------------------------")
  for task_idx, task in enumerate(workflowTasksList):
    if task['type'] == 'Python':
      # print("############ TYPE IS PYTHON ############")
      taskData = getPythonTaskData(task_idx, task)
      # print("--------------------------------------------------------")
      # print("revised pythonTaskData is: ", taskData)
      taskDataList.append(taskData)
      # print("--------------------------------------------------------")
    # if task_idx == (len(workflowTasksList)-1):
      # print("////////////////// FINISHED PROCESSING THE LAST TASK \\\\\\\\\\\\\\\\\\\\\\")
  return taskDataList

def getDeploymentInput(poolQueueId, deploymentInput):  
  #This will later need to receive the user-supplied YAML fragment as input when the params are changed to allow the YAML to specify artifacts, etc.  
  depInputTemplateFile = jsonFragmentDir + 'deploymentInputTemplate.json'  
  depInputData = json.load(open(depInputTemplateFile, 'r'))  
  # print("depInputData inside getDeploymentInput() is: ", depInputData)  
  # print("--------------------------------------------------------")  
  # print("deploymentInput inside getDeploymentInput() is: ", deploymentInput)
  # print("--------------------------------------------------------")  
  downloadInputsList = []  
  for dInput in deploymentInput:  
    for dep_item in dInput:
      # print("dep_item is: ", dep_item)
      if re.match("artifactsDownloadInput", dep_item):  
        artifactsList = dInput.get(dep_item)  
        # print("artifactsList is: ", artifactsList)  
        # print("--------------------------------------------------------")  
        # print("depInputData is: ", depInputData)  
        # print("--------------------------------------------------------")  
        for artifact in artifactsList:  
          # print("artifact is: ", artifact)  
          # print("--------------------------------------------------------")  
          artifactDownloadInputTemplateFile = jsonFragmentDir + 'downloadInputArtifactTemplate.json'  
          artifactData = json.load(open(artifactDownloadInputTemplateFile, 'r'))  
          for artifact_item in artifact:
            # print("artifact_item is: ", artifact_item)  
            # print("--------------------------------------------------------")  
            if re.match("alias", artifact_item):  
              artifactData['alias'] = artifact.get(artifact_item)  
          downloadInputsList.append(artifactData)  
        dinputsData = {"downloadInputs": []}
        #json_dinputsData = json.loads(dinputsData)
        # print("dinputsData is: ", dinputsData)
        # print("--------------------------------------------------------")  
        # print("dinputsData['downloadInputs'] is: ", dinputsData['downloadInputs'])
        # print("--------------------------------------------------------")  
        #dloadInputsList = json.dumps(downloadInputsList)
        # print("revised downloadInputsList is: ", downloadInputsList)
        # print("--------------------------------------------------------") 
        dinputsData['downloadInputs'] = downloadInputsList
        # print("revised dinputsData is: ", dinputsData)
        # print("--------------------------------------------------------")  
  depInputData['artifactsDownloadInput'] = dinputsData
  # print("---- Inside queueId block ----")  
  depInputData['queueId'] = poolQueueId
  # print("--------------------------------------------------------")  
  # print("revised depInputData about to be returned is: ", depInputData)
  # print("--------------------------------------------------------")  
  return depInputData
  
def getDeploymentPhaseData(phase_idx, deployPhase, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id):
  deployPhaseData = json.load(open(deployPhaseTemplateFile, 'r'))
  # print("deployPhaseData is: ", deployPhaseData)
  # print("--------- Gonna print a new deployment phase ----------------")
  # print(phase_idx, ": ", deployPhase)
  # print("--------- Gonna decompose the deployment phase ----------------")
  #Now iterate the YAML input
  for depPhase_item in deployPhase:  
    # print(phase_idx, ": ", "depPhase_item is: ", depPhase_item)
    if re.match("name", depPhase_item):  
      #print(phase_idx, ": ", "name is: ", deployPhase.get(depPhase_item))  
      deployPhaseData['name'] = deployPhase.get(depPhase_item)
    if re.match("deploymentInput", depPhase_item):  
      depInput = getDeploymentInput(poolQueueId, deployPhase.get(depPhase_item))  
      deployPhaseData['deploymentInput'] = depInput  
    if re.match("workflowTasks", depPhase_item):  
      taskDataList = getWorkflowTasksList(deployPhase.get(depPhase_item), key_vault_name, key_vault_service_connection_id)
      # print("--------------------------------------------------------")
      # print("taskDataList is: ", taskDataList)
      # print("--------------------------------------------------------")
      deployPhaseData['workflowTasks'] = taskDataList
  return deployPhaseData

def getEnvironmentData(env_idx, environment, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id):
  environmentData = json.load(open(environmentTemplateFile, 'r'))
  # print("environmentData is: ", environmentData)
  # print("--------- Gonna print a new environment item ----------------")
  # print(env_idx, ": ", environment) 
  # print("--------- Gonna decompose the environment item ----------------")
  for env_item in environment:  
    # print(env_idx, ": ", "env_item is: ", env_item)  
    if re.match("name", env_item):  
      #print(env_idx, ": ", "name is: ", environment.get(env_item))  
      environmentData['name'] = environment.get(env_item)  
    if re.match("deployPhases", env_item):  
      deployPhaseList = environment.get(env_item)  
      # print("len deployPhaseList is: ", len(deployPhaseList))  
      deployPhaseDataList = []  
      for phase_idx, deployPhase in enumerate(deployPhaseList):  
        # print("-----------------------------------------------------------")  
        # print("deployPhase in getEnvironmentData() is: ", deployPhase)  
        # print("-----------------------------------------------------------")
        deployPhaseData = getDeploymentPhaseData(phase_idx, deployPhase, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id)  
        # if phase_idx == (len(deployPhaseList)-1):
          # print("////////////////// FINISHED PROCESSING THE LAST DEPLOYMENT PHASE \\\\\\\\\\\\\\\\\\\\\\")
          # print("--------------------------------------------------------")
          # print("revised deployPhaseData is: ", deployPhaseData)
          # print("--------------------------------------------------------")
        deployPhaseDataList.append(deployPhaseData)
      # print("--------------------------------------------------------")
      # print("deployPhaseDataList is:", deployPhaseDataList)
      # print("--------------------------------------------------------")
      environmentData['deployPhases'] = deployPhaseDataList 
  stageIdx = env_idx+1
  print("stageIdx is: ", stageIdx)
  environmentData['rank'] = stageIdx
  return environmentData

def getEnvironmentsDataList(environmentsList, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id):
  # print("len environmentsList is: ", len(environmentsList))
  environmentsDataList = []
  for env_idx, environment in enumerate(environmentsList):
    environmentData = getEnvironmentData(env_idx, environment, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id)
    # print("--------------------------------------------------------")
    # print("revised environmentData is: ", environmentData)
    environmentsDataList.append(environmentData)
    # print("--------------------------------------------------------")
    # if env_idx == (len(environmentsList)-1):
      # print("////////////////// FINISHED PROCESSING THE LAST ENVIRONMENT \\\\\\\\\\\\\\\\\\\\\\")
  return environmentsDataList

def getArtifactsDataList(artifactsTemplateFile, project_id, org_service_url, project_name, buildRepoListOfTuples):
  artifactsDataList = [] 
  for buildRepoTuple in buildRepoListOfTuples:
    buildDefId = buildRepoTuple[0]
    repoName = buildRepoTuple[1]
    artifactsData = json.load(open(artifactsTemplateFile, 'r'))
    # print("-----------------------------------------------------------------")
    # print("artifactsData is: ", artifactsData)
    # print("-----------------------------------------------------------------")
    artifact_alias = "_" + repoName
    #old version keeping for backup: artifactsData['sourceId'] = project_id + ":1"
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
  print("-----------------------------------------------------------------")
  print("revised artifactsDataList is: ", artifactsDataList)
  print("-----------------------------------------------------------------")
  return artifactsDataList

def getVariablesData(variablesYAML):
  #lastIndex = len(variablesYAML)
  #print("lastIndex at start of getVariablesData() is: ", lastIndex)
  idx = 1
  varJsonListItems = ""
  # print("variablesYAML is: ", variablesYAML)
  #NOTE: Assuming here the variablesYAML is a list containing a single dict of keys/values, so not we extract the dict from the YAML and assume there is only one dict so that the loop only runs once.  
  for varsList in variablesYAML:
    lastIndex = len(varsList)
    # print("lastIndex at start of for pair is: ", lastIndex)
    # print("idx at start of for pair is: ", idx)
    # print("varsList is: ", varsList)
    for var in varsList:
      # print("lastIndex at start of for var in varsList is: ", lastIndex)
      # print("idx at start of for var in varsList is: ", idx)
      # print("var is: ", var)  
      #/////////////// begin test new syntax
      # print(var, " is: ", varsList.get(var))
      varJSON = " \""+ var + "\":{ \"value\":\""+varsList.get(var)+"\"}"
      varJsonListItems = varJsonListItems + varJSON
      # print("varJsonListItems right after assignment is: ", varJsonListItems)
      #The following check assumes that all variable items are valid and are handled by if cases here.  This could cause malformed JSON if received data is not valid or is not handled in if cases here.
      if idx < lastIndex:
        varJsonListItems = varJsonListItems + ", "
      #/////////////// end test new syntax
      #if re.match("aws-region", var):
      #  print("aws-region is: ", varsList.get(var))
      #  varJSON = " \"aws-region\":{ \"value\":\""+varsList.get(var)+"\"}"
      #  varJsonListItems = varJsonListItems + varJSON
      #  #The following check assumes that all variable items are valid and are handled by if cases here.  This could cause malformed JSON if received data is not valid or is not handled in if cases here.
      #  if idx < lastIndex:
      #    varJsonListItems = varJsonListItems + ", "
      idx += 1  
    #idx += 1  
  varOutputString = "{ " + varJsonListItems + " }"
  varOutputString = varOutputString.replace(" ", "")
  # print("varOutputString just before json loads is: ", varOutputString)
  varOutputData = json.loads(varOutputString)
  # print("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"")
  # print("varOutputData is: ", varOutputData)
  # print("/////////////////////////////////////////////////////////")
  #{"aws-region":{"value":"us-west-2"}}
  return varOutputData

def getReleaseDefData(yamlInputFile, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, artifactsTemplateFile, poolQueueId, azdo_project_id, azdo_organization_service_url, azdo_project_name, buildRepoListOfTuples, key_vault_name, key_vault_service_connection_id):
  with open(yamlInputFile) as f:
    releaseDef_dict = yaml.safe_load(f)
    releaseDefData = json.load(open(releaseDefConstructorTemplateFile, 'r'))
    for item in releaseDef_dict:
      if re.match("name", item):
        releaseDefData['name'] = releaseDef_dict.get(item)
      if re.match("description", item):
        releaseDefData['description'] = releaseDef_dict.get(item)
      if re.match("environments", item):
        environmentsDataList = getEnvironmentsDataList(releaseDef_dict.get(item), environmentTemplateFile, deployPhaseTemplateFile, poolQueueId, key_vault_name, key_vault_service_connection_id)
        releaseDefData['environments'] = environmentsDataList
      if re.match("variables", item):
        variablesData = getVariablesData(releaseDef_dict.get(item))
        releaseDefData['variables'] = variablesData
    artifactsDataList = getArtifactsDataList(artifactsTemplateFile, azdo_project_id, azdo_organization_service_url, azdo_project_name, buildRepoListOfTuples)
    releaseDefData['artifacts'] = artifactsDataList
    return releaseDefData

def createReleaseDefinitionApiRequest(data, azdo_organization_name, azdo_project_id):
    personal_access_token = ":"+os.environ["AZ_PAT"]
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

#############################################################################################################
### New functions
#############################################################################################################

def getRepoBuildOutputs(sourceReposList, myYamlInputFile, awsCredFile, acmRootDir): 
  project_name = depfunc.getProjectName(myYamlInputFile)
  project_calls_root = depfunc.getProjectCallsRoot(myYamlInputFile, acmRootDir)
  build_repo_list = []
  if len(sourceReposList) > 0:
    print(len(sourceReposList), " source repository URLs were imported from YAML input.  Going to process each now.  ")
    for sourceRepo in sourceReposList:
      print("sourceRepo before call to getRepoName() is: ", sourceRepo)
      nameOfRepo = depfunc.getRepoName(sourceRepo)
      print("nameOfRepo returned by getNameRepo() is: ", nameOfRepo)
      call_name = "call-to-" + nameOfRepo  
      call_to_repobuild_dir = project_calls_root+ "repo-builds/" + call_name  
      print("call_to_repobuild_dir is: ", call_to_repobuild_dir)
      backendConfigRepo = depfunc.getRepoBuildBackendConfig(nameOfRepo, myYamlInputFile, awsCredFile)
      print("backendConfigRepo is: ", backendConfigRepo)
      initBackendRepoBuildCommand = 'terraform init ' + backendConfigRepo
      print("initBackendRepoBuildCommand is: ", initBackendRepoBuildCommand)
      rbSecretsFile = '/home/agile-cloud/vars/agile-cloud-manager/'+project_name+'-'+ nameOfRepo + '-repoBuild-secrets.tfvars'
      inputsRepoBuild = depfunc.getRepoBuildInputs(myYamlInputFile, awsCredFile, rbSecretsFile, project_name, sourceRepo, nameOfRepo)
      print("inputsRepoBuild is: ", inputsRepoBuild)
      depfunc.runTerraformCommand(initBackendRepoBuildCommand, call_to_repobuild_dir)
      depfunc.runTerraformCommand('terraform output ', call_to_repobuild_dir)
      buildRepoTuple = (depfunc.azuredevops_build_definition_id, depfunc.azuredevops_git_repository_name)  
      build_repo_list.append(buildRepoTuple)
      print("........................................................................................................")
  else:
    print("Zero source repository URLs were imported from the YAML input.  ")
  return build_repo_list  
  
#///////////////////////////////////////////////////////////////////////////////////////////////////////
def getProjectOutputs(myYamlInputFile, acmRootDir, awsCredFile):
  project_name = depfunc.getProjectName(myYamlInputFile)
  projectSecretsFile = '/home/agile-cloud/vars/agile-cloud-manager/'+project_name+'-project-secrets.tfvars'
  depfunc.getOutputFromFoundation(myYamlInputFile, awsCredFile, acmRootDir )
  call_to_project_dir = depfunc.getDirectoryOfCallToProjectModule(myYamlInputFile, acmRootDir)
  backendProjectConfig = depfunc.getProjectBackendConfig(myYamlInputFile, awsCredFile)
  initBackendProjectCommand = 'terraform init ' + backendProjectConfig
  print("initBackendProjectCommand is: ", initBackendProjectCommand)
  #print("Confirm that sbscription_id and tenant_id have been successfully populated from foundation output: ")
  #print("subscription_id  is: ", subscription_id)
  #print("tenant_id  is: ", tenant_id)
  #projectVars = getProjectInputs(myYamlInputFile, awsCredFile, projectSecretsFile, subscription_id, tenant_id )
  #print("projectVars is: ", projectVars)
  #crudProjectCommand = crudCommand + projectVars
  depfunc.runTerraformCommand(initBackendProjectCommand, call_to_project_dir)
  depfunc.runTerraformCommand('terraform output ', call_to_project_dir)

def getOrganizationNameFromYaml(yamlInputFile): 
  azdoOrgName = ''
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("azdoConnection", item):  
        connectionItems = topLevel_dict.get(item)  
        for connectionItem in connectionItems:
          if re.match("azdoOrgServiceURL", connectionItem):
            azdoOrgServiceURL = connectionItems.get(connectionItem)
            azdoOrgServiceURL = azdoOrgServiceURL.split("azure.com/",1)[1]
            azdoOrgName = azdoOrgServiceURL.replace("/","")
  return azdoOrgName

def getOrgServiceUrlFromYaml(yamlInputFile): 
  azdoOrgServiceURL = ''
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("azdoConnection", item):  
        connectionItems = topLevel_dict.get(item)  
        for connectionItem in connectionItems:
          if re.match("azdoOrgServiceURL", connectionItem):
            azdoOrgServiceURL = connectionItems.get(connectionItem)
  return azdoOrgServiceURL


##############################################################################################
### Step One: Get The Output Variables From the project module and from the repo-build module
##############################################################################################
#The awsCredFile is for the terraform backend that will store state for the azure infrastructure created for the agile cloud manager.
awsCredFile = '/home/agile-cloud/.aws/credentials'
getProjectOutputs(myYamlInputFile, acmRootDir, awsCredFile)
  
#Get each pathToRepoBuildCalls
sourceReposList = depfunc.getListOfSourceRepos(myYamlInputFile)  
buildRepoListOfTuples = getRepoBuildOutputs(sourceReposList, myYamlInputFile, awsCredFile, acmRootDir)

print("depfunc.azuredevops_project_id is: ", depfunc.azuredevops_project_id)
print("depfunc.azuredevops_service_connection_id is: ", depfunc.azuredevops_service_connection_id)
print("buildRepoListOfTuples is: ", buildRepoListOfTuples)

###################################################################################################################################################
### Temporarily commenting out the entire rest of this file while we re-write from the start using the new directory structure
###################################################################################################################################################
orgName = getOrganizationNameFromYaml(myYamlInputFile)
print("orgName is: ", orgName)
# ### //////////////////////
orgServiceUrl = getOrgServiceUrlFromYaml(myYamlInputFile)
print("orgServiceUrl is: ", orgServiceUrl)  
projectName = depfunc.getProjectName(myYamlInputFile)
print("projectName is: ", projectName)

#########################################################################################################
### Step Two: Get The poolQueueId from the agent pool Queue that will be used by the release definition.
#########################################################################################################
queue_name = "Default"
poolQueueId = depfunc.getPoolQueueIdApiRequest(orgName, depfunc.azuredevops_project_id, queue_name)
print("poolQueueId is: ", poolQueueId)  
print("---------------------------------------------------------")

######################################################################################
### Step Three: Convert YAML definition to JSON data
######################################################################################
yamlDir = '../release-definitions/yaml-definition-files/'
#yamlFile = yamlDir + 'createTerraformSimpleAWS.yaml'
yamlFile = yamlDir + YamlReleaseDefFile
deployPhaseTemplateFile = jsonFragmentDir + 'deployPhaseTemplate.json'
environmentTemplateFile = jsonFragmentDir + 'environmentTemplate.json'
releaseDefConstructorTemplateFile = jsonFragmentDir + 'releaseDefConstructorTemplate.json'
artifactsTemplateFile = jsonFragmentDir + 'artifactsTemplate.json'

# vaultName = depfunc.azuredevops_key_vault_name
#The following line is a test to confirm that we can toggle the key vault task on or off depending on whether or not the vault name is populated.  
vaultName = 'testvlt789'  

releaseDefData = getReleaseDefData(yamlFile, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, artifactsTemplateFile, poolQueueId, depfunc.azuredevops_project_id, orgServiceUrl, projectName, buildRepoListOfTuples, vaultName, depfunc.azuredevops_service_connection_id)
print("--------------------------------------------------------")
# print("revised releaseDefData is: ", releaseDefData)
print("--------------------------------------------------------")


##############################################################################################
### Step Four: Create Release Definition By Making API Call.
##############################################################################################
rCode = createReleaseDefinitionApiRequest(releaseDefData, orgName, depfunc.azuredevops_project_id)

print("response code from create release definition API call is: ", rCode)

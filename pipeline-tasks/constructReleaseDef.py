import json
import yaml
import re
import sys  
import requests
import os
import base64
import deploymentFunctions as depfunc  
  
jsonFragmentDir = '../release-definitions/json-fragments/' 
  
def getPythonTaskData(task_idx, task):  
  pythonTaskTemplateFile = jsonFragmentDir + 'pythonTaskTemplate.json'  
  pythonTaskData = json.load(open(pythonTaskTemplateFile, 'r'))  
  print("pythonTaskData is: ", pythonTaskData)
  print("--------------------------------------------------------")
  print("--------- Gonna print a new workflow task ----------------")  
  print(task_idx, ": ", task)  
  print("--------- Gonna decompose the workflow task ----------------")  
  for task_item in task:  
    print(task_idx, ": ", "task_item is: ", task_item)  
    if re.match("name", task_item):  
      #print(task_idx, ": ", "name is: ", task.get(task_item))  
      pythonTaskData['name'] = task.get(task_item)
    if re.match("type", task_item):  
      print(task_idx, ": ", "type is: ", task.get(task_item))
      if re.match("Python", task.get(task_item)): 
        pythonTaskData['taskId'] = '6392f95f-7e76-4a18-b3c7-7f078d2f7700'
    if re.match("scriptPath", task_item):  
      #print(task_idx, ": ", "scriptPath is: ", task.get(task_item))
      pythonTaskData['inputs']['scriptPath'] = task.get(task_item)
    if re.match("arguments", task_item):  
      #print(task_idx, ": ", "arguments is: ", task.get(task_item))  
      pythonTaskData['inputs']['arguments'] = task.get(task_item)
    if re.match("workingDirectory", task_item):  
      #print(task_idx, ": ", "workingDirectory is: ", task.get(task_item))  
      pythonTaskData['inputs']['workingDirectory'] = task.get(task_item)
  return pythonTaskData

def getWorkflowTasksList(workflowTasksList):
  print("len workflowTasksList is: ", len(workflowTasksList))
  taskDataList = []
  for task_idx, task in enumerate(workflowTasksList):
    if task['type'] == 'Python':
      print("############ TYPE IS PYTHON ############")
      taskData = getPythonTaskData(task_idx, task)
      print("--------------------------------------------------------")
      print("revised pythonTaskData is: ", taskData)
      taskDataList.append(taskData)
      print("--------------------------------------------------------")
    if task_idx == (len(workflowTasksList)-1):
      print("////////////////// FINISHED PROCESSING THE LAST TASK \\\\\\\\\\\\\\\\\\\\\\")
  return taskDataList

def getDeploymentInput(poolQueueId, deploymentInput):  
  #This will later need to receive the user-supplied YAML fragment as input when the params are changed to allow the YAML to specify artifacts, etc.  
  depInputTemplateFile = jsonFragmentDir + 'deploymentInputTemplate.json'  
  depInputData = json.load(open(depInputTemplateFile, 'r'))  
  print("depInputData inside getDeploymentInput() is: ", depInputData)  
  print("--------------------------------------------------------")  
  print("deploymentInput inside getDeploymentInput() is: ", deploymentInput)
  print("--------------------------------------------------------")  
  downloadInputsList = []  
  for dInput in deploymentInput:  
    for dep_item in dInput:
      print("dep_item is: ", dep_item)
      if re.match("artifactsDownloadInput", dep_item):  
        artifactsList = dInput.get(dep_item)  
        print("artifactsList is: ", artifactsList)  
        print("--------------------------------------------------------")  
        print("depInputData is: ", depInputData)  
        print("--------------------------------------------------------")  
        for artifact in artifactsList:  
          print("artifact is: ", artifact)  
          print("--------------------------------------------------------")  
          artifactDownloadInputTemplateFile = jsonFragmentDir + 'downloadInputArtifactTemplate.json'  
          artifactData = json.load(open(artifactDownloadInputTemplateFile, 'r'))  
          for artifact_item in artifact:
            print("artifact_item is: ", artifact_item)  
            print("--------------------------------------------------------")  
            if re.match("alias", artifact_item):  
              artifactData['alias'] = artifact.get(artifact_item)  
          downloadInputsList.append(artifactData)  
        dinputsData = {"downloadInputs": []}
        #json_dinputsData = json.loads(dinputsData)
        print("dinputsData is: ", dinputsData)
        print("--------------------------------------------------------")  
        print("dinputsData['downloadInputs'] is: ", dinputsData['downloadInputs'])
        print("--------------------------------------------------------")  
        #dloadInputsList = json.dumps(downloadInputsList)
        print("revised downloadInputsList is: ", downloadInputsList)
        print("--------------------------------------------------------") 
        dinputsData['downloadInputs'] = downloadInputsList
        print("revised dinputsData is: ", dinputsData)
        print("--------------------------------------------------------")  
  depInputData['artifactsDownloadInput'] = dinputsData
  print("---- Inside queueId block ----")  
  depInputData['queueId'] = poolQueueId
  print("--------------------------------------------------------")  
  print("revised depInputData about to be returned is: ", depInputData)
  print("--------------------------------------------------------")  
  return depInputData
  
def getDeploymentPhaseData(phase_idx, deployPhase, deployPhaseTemplateFile, poolQueueId):
  deployPhaseData = json.load(open(deployPhaseTemplateFile, 'r'))
  print("deployPhaseData is: ", deployPhaseData)
  print("--------- Gonna print a new deployment phase ----------------")
  print(phase_idx, ": ", deployPhase)
  print("--------- Gonna decompose the deployment phase ----------------")
  #Now iterate the YAML input
  for depPhase_item in deployPhase:  
    print(phase_idx, ": ", "depPhase_item is: ", depPhase_item)
    if re.match("name", depPhase_item):  
      #print(phase_idx, ": ", "name is: ", deployPhase.get(depPhase_item))  
      deployPhaseData['name'] = deployPhase.get(depPhase_item)
    if re.match("deploymentInput", depPhase_item):  
      depInput = getDeploymentInput(poolQueueId, deployPhase.get(depPhase_item))  
      deployPhaseData['deploymentInput'] = depInput  
    if re.match("workflowTasks", depPhase_item):  
      taskDataList = getWorkflowTasksList(deployPhase.get(depPhase_item))
      print("--------------------------------------------------------")
      print("taskDataList is: ", taskDataList)
      print("--------------------------------------------------------")
      deployPhaseData['workflowTasks'] = taskDataList
  return deployPhaseData

def getEnvironmentData(env_idx, environment, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId):
  environmentData = json.load(open(environmentTemplateFile, 'r'))
  print("environmentData is: ", environmentData)
  print("--------- Gonna print a new environment item ----------------")
  print(env_idx, ": ", environment) 
  print("--------- Gonna decompose the environment item ----------------")
  for env_item in environment:  
    print(env_idx, ": ", "env_item is: ", env_item)  
    if re.match("name", env_item):  
      #print(env_idx, ": ", "name is: ", environment.get(env_item))  
      environmentData['name'] = environment.get(env_item)  
    if re.match("deployPhases", env_item):  
      deployPhaseList = environment.get(env_item)  
      print("len deployPhaseList is: ", len(deployPhaseList))  
      deployPhaseDataList = []  
      for phase_idx, deployPhase in enumerate(deployPhaseList):  
        print("-----------------------------------------------------------")  
        print("deployPhase in getEnvironmentData() is: ", deployPhase)  
        print("-----------------------------------------------------------")
        deployPhaseData = getDeploymentPhaseData(phase_idx, deployPhase, deployPhaseTemplateFile, poolQueueId)  
        if phase_idx == (len(deployPhaseList)-1):
          print("////////////////// FINISHED PROCESSING THE LAST DEPLOYMENT PHASE \\\\\\\\\\\\\\\\\\\\\\")
          print("--------------------------------------------------------")
          print("revised deployPhaseData is: ", deployPhaseData)
          print("--------------------------------------------------------")
        deployPhaseDataList.append(deployPhaseData)
      print("--------------------------------------------------------")
      print("deployPhaseDataList is:", deployPhaseDataList)
      print("--------------------------------------------------------")
      environmentData['deployPhases'] = deployPhaseDataList 
  return environmentData

def getEnvironmentsDataList(environmentsList, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId):
  print("len environmentsList is: ", len(environmentsList))
  environmentsDataList = []
  for env_idx, environment in enumerate(environmentsList):
    environmentData = getEnvironmentData(env_idx, environment, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId)
    print("--------------------------------------------------------")
    print("revised environmentData is: ", environmentData)
    environmentsDataList.append(environmentData)
    print("--------------------------------------------------------")
    if env_idx == (len(environmentsList)-1):
      print("////////////////// FINISHED PROCESSING THE LAST ENVIRONMENT \\\\\\\\\\\\\\\\\\\\\\")
  return environmentsDataList

def getArtifactsDataList(artifactsTemplateFile, project_id, org_service_url, project_name, build_definition_id, git_repository_name):
  #Note: This will be separated into two functions later to facilitate creation of multiple artifacts.  This now is simplified for demonstration.  
  artifactsDataList = [] 
  artifactsData = json.load(open(artifactsTemplateFile, 'r'))
  print("-----------------------------------------------------------------")
  print("artifactsData is: ", artifactsData)
  print("-----------------------------------------------------------------")
  artifact_alias = "_" + git_repository_name
  artifactsData['sourceId'] = project_id + ":1"
  artifactsData['artifactSourceDefinitionUrl']['id'] = org_service_url + project_name + "/_build?definitionId=" + str(build_definition_id)
  artifactsData['alias'] = artifact_alias
  artifactsData['definitionReference']['definition']['id'] = build_definition_id
  artifactsData['definitionReference']['definition']['name'] = git_repository_name
  artifactsData['definitionReference']['project']['id'] = project_id
  artifactsData['definitionReference']['project']['name'] = project_name
  artifactsDataList.append(artifactsData)
  print("-----------------------------------------------------------------")
  print("revised artifactsDataList is: ", artifactsDataList)
  print("-----------------------------------------------------------------")
  return artifactsDataList

def getReleaseDefData(yamlInputFile, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, artifactsTemplateFile, poolQueueId, azdo_project_id, azdo_organization_service_url, azdo_project_name, azdo_build_definition_id, azdo_git_repository_name):
  with open(yamlInputFile) as f:
    releaseDef_dict = yaml.safe_load(f)
    releaseDefData = json.load(open(releaseDefConstructorTemplateFile, 'r'))
    print("releaseDefData is: ", releaseDefData)
    for item in releaseDef_dict:
      print("item is: ", item)
      if re.match("name", item):
        #print("name is: ", releaseDef_dict.get(item))
        releaseDefData['name'] = releaseDef_dict.get(item)
      if re.match("description", item):
        #print("description is: ", releaseDef_dict.get(item))
        releaseDefData['description'] = releaseDef_dict.get(item)
      if re.match("environments", item):
        print("Inside environments block. ")
        print("environments item is: ", item)
        print("environments get(item) is: ", releaseDef_dict.get(item))
        environmentsDataList = getEnvironmentsDataList(releaseDef_dict.get(item), environmentTemplateFile, deployPhaseTemplateFile, poolQueueId)
        print("--------------------------------------------------------")
        print("revised environmentsDataList is: ", environmentsDataList)
        releaseDefData['environments'] = environmentsDataList
    #Processing artifacts from terraform output and not from YAML under current configuration.  This can be adjusted based on your organization's policies.  
    print("Inside the artifacts block.  ")
    artifactsDataList = getArtifactsDataList(artifactsTemplateFile, azdo_project_id, azdo_organization_service_url, azdo_project_name, azdo_build_definition_id, azdo_git_repository_name)
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


##############################################################################################
### Step One: Get The Output Variables From the azure-pipelines-project-repo-build module
##############################################################################################
initCommand='terraform init'
pathToProjectRepoBuildCalls = "/home/aci-user/cloned-repos/agile-cloud-manager/calls-to-modules/azure-pipelines-project-repo-build-resources/"
outputProjectRepoBuildCommand='terraform output '

depfunc.runTerraformCommand(initCommand, pathToProjectRepoBuildCalls)
depfunc.runTerraformCommand(outputProjectRepoBuildCommand, pathToProjectRepoBuildCalls)

print("Back in constructReleaseDef.py .")
print("depfunc.azuredevops_project_id is: ", depfunc.azuredevops_project_id )
print("depfunc.azuredevops_organization_name is: ", depfunc.azuredevops_organization_name)

#########################################################################################################
### Step Two: Get The poolQueueId from the agent pool Queue that will be used by the release definition.
#########################################################################################################
queue_name = "Default"
poolQueueId = depfunc.getPoolQueueIdApiRequest(depfunc.azuredevops_organization_name, depfunc.azuredevops_project_id, queue_name)
print("poolQueueId is: ", poolQueueId)  
print("---------------------------------------------------------")

######################################################################################
### Step Three: Convert YAML definition to JSON data
######################################################################################
yamlDir = '../release-definitions/yaml-definition-files/'
yamlFile = yamlDir + 'createTerraformSimpleAWS.yaml'
deployPhaseTemplateFile = jsonFragmentDir + 'deployPhaseTemplate.json'
environmentTemplateFile = jsonFragmentDir + 'environmentTemplate.json'
releaseDefConstructorTemplateFile = jsonFragmentDir + 'releaseDefConstructorTemplate.json'
artifactsTemplateFile = jsonFragmentDir + 'artifactsTemplate.json'

releaseDefData = getReleaseDefData(yamlFile, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, artifactsTemplateFile, poolQueueId, depfunc.azuredevops_project_id, depfunc.azuredevops_organization_service_url, depfunc.azuredevops_project_name, depfunc.azuredevops_build_definition_id, depfunc.azuredevops_git_repository_name)
print("--------------------------------------------------------")
print("revised releaseDefData is: ", releaseDefData)
print("--------------------------------------------------------")


# ##############################################################################################
# ### Step Four: Create Release Definition By Making API Call.
# ##############################################################################################
# rCode = createReleaseDefinitionApiRequest(releaseDefData, depfunc.azuredevops_organization_name, depfunc.azuredevops_project_id)

# print("response code from create release definition API call is: ", rCode)

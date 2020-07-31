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

def getDeploymentInput(poolQueueId):
  #This will later need to receive the user-supplied YAML fragment as input when the params are changed to allow the YAML to specify artifacts, etc.
  depInputTemplateFile = jsonFragmentDir + 'deploymentInputTemplate.json'  
  depInputData = json.load(open(depInputTemplateFile, 'r'))  
  print("depInputData is: ", depInputData)
  print("--------------------------------------------------------")
  print("---- Inside queueId block ----")  
  depInputData['queueId'] = poolQueueId
  return depInputData
    
def getDeploymentPhaseData(phase_idx, deployPhase, deployPhaseTemplateFile, poolQueueId):
  deployPhaseData = json.load(open(deployPhaseTemplateFile, 'r'))
  print("deployPhaseData is: ", deployPhaseData)
  print("--------- Gonna print a new deployment phase ----------------")
  print(phase_idx, ": ", deployPhase)
  print("--------- Gonna decompose the deployment phase ----------------")
  #Handling deployment input individually here because its inputs are from an API call and not from YAML now.  This will change later when artifact info will later be brought in from YAML.
  depInput = getDeploymentInput(poolQueueId)
  deployPhaseData['deploymentInput'] = depInput 
  #Now iterate the YAML input
  for depPhase_item in deployPhase:  
    print(phase_idx, ": ", "depPhase_item is: ", depPhase_item)
    if re.match("name", depPhase_item):  
      #print(phase_idx, ": ", "name is: ", deployPhase.get(depPhase_item))  
      deployPhaseData['name'] = deployPhase.get(depPhase_item)
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
      print("len deployPhaseList is: ", deployPhaseList)
      deployPhaseDataList = []
      for phase_idx, deployPhase in enumerate(deployPhaseList):  
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

def getReleaseDefData(yamlInputFile, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId):
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

releaseDefData = getReleaseDefData(yamlFile, releaseDefConstructorTemplateFile, environmentTemplateFile, deployPhaseTemplateFile, poolQueueId)
print("--------------------------------------------------------")
print("revised releaseDefData is: ", releaseDefData)
print("--------------------------------------------------------")
  
##############################################################################################
### Step Four: Create Release Definition By Making API Call.
##############################################################################################
rCode = createReleaseDefinitionApiRequest(releaseDefData, depfunc.azuredevops_organization_name, depfunc.azuredevops_project_id)

print("response code from create release definition API call is: ", rCode)

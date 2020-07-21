print("Inside installReleaseDefinition.py script.")  
  
import sys  
import requests
import os
import base64
import json

import deploymentFunctions as depfunc  
  
pathToAzdoProviderInputs='/home/aci-user/vars/agile-cloud-manager/inputs-azdo-provider.tfvars'
pathToAzurermProviderInputs='/home/aci-user/vars/agile-cloud-manager/inputs-azurerm-provider.tfvars'
pathToAzdoProjectRepoBuildAutoInputs='/home/aci-user/vars/agile-cloud-manager/inputs-project-repo-build-auto.tfvars'
pathToAzdoProjectRepoBuildManualInputs='/home/aci-user/vars/agile-cloud-manager/inputs-project-repo-build-manual.tfvars'

getAzdoProviderInputs=' -var-file='+pathToAzdoProviderInputs
getAzurermProviderInputs=' -var-file='+pathToAzurermProviderInputs
getAzdoProjectRepoBuildAutoInputs=' -var-file='+pathToAzdoProjectRepoBuildAutoInputs
getAzdoProjectRepoBuildManualInputs=' -var-file='+pathToAzdoProjectRepoBuildManualInputs

initCommand='terraform init'

pathToProjectRepoBuildCalls = "/home/aci-user/cloned-repos/agile-cloud-manager/calls-to-modules/azure-pipelines-project-repo-build-resources/"
outputProjectRepoBuildCommand='terraform output '

##############################################################################################
### Step One: Get The Output Variables From the azure-pipelines-project-repo-build module
##############################################################################################

depfunc.runTerraformCommand(initCommand, pathToProjectRepoBuildCalls)
depfunc.runTerraformCommand(outputProjectRepoBuildCommand, pathToProjectRepoBuildCalls)

print("Back in installReleaseDefinition.py .")
print("depfunc.azuredevops_build_definition_id is: ", depfunc.azuredevops_build_definition_id)
print("depfunc.azuredevops_git_repository_id is: ", depfunc.azuredevops_git_repository_id)
print("depfunc.azuredevops_git_repository_name is: ", depfunc.azuredevops_git_repository_name)
print("depfunc.azuredevops_project_id is: ", depfunc.azuredevops_project_id )
print("depfunc.azuredevops_project_name is: ", depfunc.azuredevops_project_name)
print("depfunc.azuredevops_organization_service_url is: ", depfunc.azuredevops_organization_service_url)

print("depfunc.azuredevops_key_vault_name is: ", depfunc.azuredevops_key_vault_name)
print("depfunc.azuredevops_organization_name is: ", depfunc.azuredevops_organization_name)

print("depfunc.azuredevops_service_connection_id is: ", depfunc.azuredevops_service_connection_id)

##############################################################################################
### Step Two: Get The poolId from the agent pool that will be used by the release definition.
##############################################################################################
def getApiRequest(url):  
    personal_access_token = ":"+os.environ["AZ_PAT"]
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
    r = requests.get(url, headers=headers)
    print("r.status_code is: ", r.status_code)
    #Add some better error handling here to handle various response codes.  We are assuming that a 200 response is received in order to continue here.  
    return r.json()

#Get the Agent Pool Queues whose name matches the search criteria.  This should only be one queue because name should be a unique key.  
#Set variables to be shared across API calls.  These will be imported from terraform output variables.
api_version_p = "5.1-preview.1"
api_version = "5.1"
queue_name = "Default"
#Get a list of agent pools.
#GET https://dev.azure.com/{organization}/{project}/_apis/distributedtask/queues?queueName={queueName}&actionFilter={actionFilter}&api-version=5.1-preview.1
#agentpools_url = ("https://dev.azure.com/%s/_apis/distributedtask/pools?api-version=%s" % (azuredevops_organization_name, api_version))
queues_url = ("https://dev.azure.com/%s/%s/_apis/distributedtask/queues?queueName=%s&api-version=%s" % (depfunc.azuredevops_organization_name, depfunc.azuredevops_project_id, queue_name, api_version_p))
poolName="Default"
agentpools_url = ("https://dev.azure.com/%s/_apis/distributedtask/pools?poolName=%s&api-version=%s" % (depfunc.azuredevops_organization_name, poolName, api_version))
print("-------------------------------------------------------------")
print("-------------------------------------------------------------")
print("---- About to get list of Agent Pool Job Queues ----")
print("---- About to get list of Agent Pools ----")
queuesData = getApiRequest(queues_url)
print("queuesData is: ", queuesData)
print("---------------------------------------------------------")
poolsData = getApiRequest(agentpools_url)
print("poolsData is: ", poolsData)
print("---------------------------------------------------------")
#Using index 0 here because queue_name should be a unique key that brings only one result in this response
#Using index 0 here because pool_name should be a unique key that brings only one result in this response
poolQueueId = queuesData['value'][0]['id']
poolId = poolsData['value'][0]['id']
print("poolQueueId is: ", poolQueueId)  
print("poolId is: ", poolId)  
print("---------------------------------------------------------")
artifactAlias = "_" + depfunc.azuredevops_git_repository_name

##############################################################################################
### Step Three: Create Release Definition By Making API Call.
##############################################################################################
def createReleaseDefinitionApiRequest(templateFile, azdo_organization_name, azdo_project_id, azdo_project_name, azdo_build_definition_id, azdo_git_repository_name, azdo_organization_service_url, queue_id, artifact_alias, azdo_service_connection_id):
    personal_access_token = ":"+os.environ["AZ_PAT"]
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
    api_version = "5.1"
    url = ("https://vsrm.dev.azure.com/%s/%s/_apis/release/definitions?api-version=%s" % (azdo_organization_name, azdo_project_id, api_version))
    with open(templateFile, 'r') as json_file:
      print("json_file is: ", json_file)
      data = json.load(json_file)
      print("---------------------------------------------------------")
      print("name is: ", data['name'])
      data['name'] = 'Create AWS Simple Example'
      print("name is now: ", data['name'])
      print("environment name is: ", data['environments'][0]['name'])
      data['environments'][0]['name'] = 'Name of environment from user-supplied script'
      print("environment name is now: ", data['environments'][0]['name'])
      print("alias is: ", data['environments'][0]['deployPhases'][0]['deploymentInput']['artifactsDownloadInput']['downloadInputs'][0]['alias'])
      data['environments'][0]['deployPhases'][0]['deploymentInput']['artifactsDownloadInput']['downloadInputs'][0]['alias'] = artifact_alias
      print("alias is now: ", data['environments'][0]['deployPhases'][0]['deploymentInput']['artifactsDownloadInput']['downloadInputs'][0]['alias'])
      print("queueId is: ", data['environments'][0]['deployPhases'][0]['deploymentInput']['queueId'])
      data['environments'][0]['deployPhases'][0]['deploymentInput']['queueId'] = queue_id
      print("queueId is now: ", data['environments'][0]['deployPhases'][0]['deploymentInput']['queueId'])
      print("---------------------------------------------------------")
      print("[\'artifacts\'][\'sourceId\'] is: ", data['artifacts'][0]['sourceId'])
      print("[\'artifacts\'][\'artifactSourceDefinitionUrl\'][\'id\'] is: ", data['artifacts'][0]['artifactSourceDefinitionUrl']['id'])
      print("[\'artifacts\'][\'alias\'] is: ", data['artifacts'][0]['alias'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['definition']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['definition']['name'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['project']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['project']['name'])
      print("---------------------------------------------------------")
      data['artifacts'][0]['sourceId'] = azdo_project_id + ":1"
      data['artifacts'][0]['artifactSourceDefinitionUrl']['id'] = azdo_organization_service_url + azdo_project_name + "/_build?definitionId=" + str(azdo_build_definition_id)
      data['artifacts'][0]['alias'] = artifactAlias
      data['artifacts'][0]['definitionReference']['definition']['id'] = azdo_build_definition_id
      data['artifacts'][0]['definitionReference']['definition']['name'] = azdo_git_repository_name
      data['artifacts'][0]['definitionReference']['project']['id'] = azdo_project_id
      data['artifacts'][0]['definitionReference']['project']['name'] = azdo_project_name
      print("---------------------------------------------------------")
      print("[\'artifacts\'][\'sourceId\'] is: ", data['artifacts'][0]['sourceId'])
      print("[\'artifacts\'][\'artifactSourceDefinitionUrl\'][\'id\'] is: ", data['artifacts'][0]['artifactSourceDefinitionUrl']['id'])
      print("[\'artifacts\'][\'alias\'] is: ", data['artifacts'][0]['alias'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['definition']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['definition']['name'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['project']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['project']['name'])

      print("-------------------------------------------------------------------")
      myIdx = 0
      for item in data['environments'][0]['deployPhases'][0]['workflowTasks']:
          #print("item is: ", item)
          print("item[taskId] is: ", item['taskId'])
          print("name of task is: ", data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['name'])
          if item['taskId'] == '6392f95f-7e76-4a18-b3c7-7f078d2f7700':
            print("This is a Python script task. ")
          if item['taskId'] == '6c731c3c-3c68-459a-a5c9-bde6e6595b5b':
            print("This is a Bash script task. ")
          if item['taskId'] == '1e244d32-2dd4-4165-96fb-b7441ca9331e':
            print("This is a Key Vault script task.  ")
            print("ConnectedServiceName is: ", data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['ConnectedServiceName'])
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['ConnectedServiceName'] = azdo_service_connection_id
            print("KeyVaultName is: ", data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['KeyVaultName'])
          myIdx += 1
      print("-------------------------------------------------------------------")

      print("---------------------------------------------------------")
      print("url is: ", url)
      print("---------------------------------------------------------")
      print("revised data is: ", data)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print("r.status_code is: ", r.status_code)
    print("r.json() is: ", r.json())
    
jsonTemplateFile = 'releaseDefinitionTemplate.json'
createReleaseDefinitionApiRequest(jsonTemplateFile, depfunc.azuredevops_organization_name, depfunc.azuredevops_project_id, depfunc.azuredevops_project_name, depfunc.azuredevops_build_definition_id, depfunc.azuredevops_git_repository_name, depfunc.azuredevops_organization_service_url, poolQueueId, artifactAlias, depfunc.azuredevops_service_connection_id)

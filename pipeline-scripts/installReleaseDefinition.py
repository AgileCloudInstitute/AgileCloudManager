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

print("azuredevops_key_vault_name is: ", depfunc.azuredevops_key_vault_name)
print("azuredevops_organization_name is: ", depfunc.azuredevops_organization_name)

##############################################################################################
### Step Two: Get The queueId from the agent pool that will be used by the release definition.
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
api_version_p = "5.1-preview.1"
queue_name = "Default"
#GET https://dev.azure.com/{organization}/{project}/_apis/distributedtask/queues?queueName={queueName}&actionFilter={actionFilter}&api-version=5.1-preview.1
queues_url = ("https://dev.azure.com/%s/%s/_apis/distributedtask/queues?queueName=%s&api-version=%s" % (depfunc.azuredevops_organization_name, depfunc.azuredevops_project_id, queue_name, api_version_p))
print("-------------------------------------------------------------")
print("---- About to get list of Agent Pool Job Queues ----")
queuesData = getApiRequest(queues_url)
print("---------------------------------------------------------")
#Using index 0 here because queue_name should be a unique key that brings only one result in this response
print("queueId is: ", queuesData['value'][0]['id'])  


##############################################################################################
### Step Three: Create Release Definition By Making API Call.
##############################################################################################
def createReleaseDefinitionApiRequest(templateFile, azdo_organization_name, azdo_project_id, azdo_project_name, azdo_build_definition_id, azdo_git_repository_name, azdo_organization_service_url):
    personal_access_token = ":"+os.environ["AZ_PAT"]
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
    api_version = "5.1"
    url = ("https://vsrm.dev.azure.com/%s/%s/_apis/release/definitions?api-version=%s" % (azuredevops_organization_name, azuredevops_project_id, api_version))
    with open(templateFile, 'r') as json_file:
      print("json_file is: ", json_file)
      data = json.load(json_file)
      print("---------------------------------------------------------")
      print("name is: ", data['name'])
      data['name'] = 'Create AWS Simple Example'
      print("name is now: ", data['name'])
      print("---------------------------------------------------------")
      print("[\'artifacts\'][\'sourceId\'] is: ", data['artifacts'][0]['sourceId'])
      print("[\'artifacts\'][\'artifactSourceDefinitionUrl\'][\'id\'] is: ", data['artifacts'][0]['artifactSourceDefinitionUrl']['id'])
      print("[\'artifacts\'][\'alias\'] is: ", data['artifacts'][0]['alias'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['definition']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['definition']['name'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['project']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['project']['name'])
      print("---------------------------------------------------------")
      data['artifacts'][0]['sourceId'] = azuredevops_project_id + ":1"
      data['artifacts'][0]['artifactSourceDefinitionUrl']['id'] = azuredevops_organization_service_url + azuredevops_project_name + "/_build?definitionId=" + str(azuredevops_build_definition_id)
      data['artifacts'][0]['alias'] = "_" + azuredevops_git_repository_name
      data['artifacts'][0]['definitionReference']['definition']['id'] = azuredevops_build_definition_id
      data['artifacts'][0]['definitionReference']['definition']['name'] = azuredevops_git_repository_name
      data['artifacts'][0]['definitionReference']['project']['id'] = azuredevops_project_id
      data['artifacts'][0]['definitionReference']['project']['name'] = azuredevops_project_name
      print("---------------------------------------------------------")
      print("[\'artifacts\'][\'sourceId\'] is: ", data['artifacts'][0]['sourceId'])
      print("[\'artifacts\'][\'artifactSourceDefinitionUrl\'][\'id\'] is: ", data['artifacts'][0]['artifactSourceDefinitionUrl']['id'])
      print("[\'artifacts\'][\'alias\'] is: ", data['artifacts'][0]['alias'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['definition']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['definition']['name'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['project']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['project']['name'])
      print("---------------------------------------------------------")
      print("url is: ", url)
      print("---------------------------------------------------------")
      print("revised data is: ", data)

jsonTemplateFile = 'releaseDefinitionTemplate.json'
createReleaseDefinitionApiRequest(jsonTemplateFile, depfunc.azuredevops_organization_name, depfunc.azuredevops_project_id, depfunc.azuredevops_project_name, depfunc.azuredevops_build_definition_id, depfunc.azuredevops_git_repository_name, depfunc.azuredevops_organization_service_url)


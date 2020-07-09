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
    print("r.json() is: ", r.json())


#Get a list of Agent Pool Queues
api_version_p = "5.1-preview.1"
queue_name = "Default"
#GET https://dev.azure.com/{organization}/{project}/_apis/distributedtask/queues?queueName={queueName}&actionFilter={actionFilter}&api-version=5.1-preview.1
queues_url = ("https://dev.azure.com/%s/%s/_apis/distributedtask/queues?queueName=%s&api-version=%s" % (depfunc.azuredevops_organization_name, depfunc.azuredevops_project_id, queue_name, api_version_p))
print("-------------------------------------------------------------")
print("---- About to get list of Agent Pool Job Queues ----")
getApiRequest(queues_url)

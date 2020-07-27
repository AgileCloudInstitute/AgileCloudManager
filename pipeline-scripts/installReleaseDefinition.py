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

#########################################################################################################
### Step Two: Get The poolQueueId from the agent pool Queue that will be used by the release definition.
#########################################################################################################
queue_name = "Default"
poolQueueId = depfunc.getPoolQueueIdApiRequest(depfunc.azuredevops_organization_name, depfunc.azuredevops_project_id, queue_name)
print("poolQueueId is: ", poolQueueId)  
print("---------------------------------------------------------")

##############################################################################################
### Step Three: Create Release Definition By Making API Call.
##############################################################################################
artifactAlias = "_" + depfunc.azuredevops_git_repository_name
jsonTemplateFile = 'releaseDefinitionTemplate.json'
myScriptInputVars = "$(-aws-public-access-key)  $(-aws-secret-access-key)  $(storageAccountNameTerraformBackend)  $(terra-backend-key)  $(aws-region)  $(System.DefaultWorkingDirectory)"
releaseDefinitionName = 'Create AWS Simple Example'
environmentName = 'Name of environment from user-supplied script'
rCode = depfunc.createReleaseDefinitionApiRequest(jsonTemplateFile, depfunc.azuredevops_organization_name, depfunc.azuredevops_project_id, depfunc.azuredevops_project_name, depfunc.azuredevops_build_definition_id, depfunc.azuredevops_git_repository_name, depfunc.azuredevops_organization_service_url, poolQueueId, artifactAlias, depfunc.azuredevops_service_connection_id, myScriptInputVars, releaseDefinitionName, environmentName)
print("response code from create release definition API call is: ", rCode)

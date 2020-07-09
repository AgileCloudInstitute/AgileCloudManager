print("Inside installReleaseDefinition.py script.")  
  
import sys  
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
outputCommand='terraform output '

pathToProjectRepoBuildCalls = "/home/aci-user/cloned-repos/agile-cloud-manager/calls-to-modules/azure-pipelines-project-repo-build-resources/"
outputProjectRepoBuildCommand=outputCommand+getAzdoProviderInputs+getAzdoProjectRepoBuildAutoInputs+getAzdoProjectRepoBuildManualInputs+getAzurermProviderInputs

##############################################################################################
### Step One: Get The Outpur Variables From the azure-pipelines-project-repo-build module
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

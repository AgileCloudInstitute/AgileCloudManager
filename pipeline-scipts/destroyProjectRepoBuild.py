
print("Inside destroyProjectRepoBuild.py script.")

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
destroyCommand='terraform destroy -auto-approve'

pathToProjectRepoBuildCalls = "/home/aci-user/cloned-repos/agile-cloud-manager/calls-to-modules/azure-pipelines-project-repo-build-resources/"
destroyProjectRepoBuildCommand=destroyCommand+getAzdoProviderInputs+getAzdoProjectRepoBuildAutoInputs+getAzdoProjectRepoBuildManualInputs+getAzurermProviderInputs

##############################################################################################
### Step One: Check to make sure that the azure devops terraform provider has been installed
##############################################################################################

#NEED TO ADD THIS.

##############################################################################################
### Step Two: Apply The azure-pipelines-project-repo-build module
##############################################################################################

depfunc.runTerraformCommand(initCommand, pathToProjectRepoBuildCalls)
depfunc.runTerraformCommand(destroyProjectRepoBuildCommand, pathToProjectRepoBuildCalls)

print("Back in destroyProjectRepoBuild.py .")


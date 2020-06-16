
print("Inside installProjectRepoBuild.py script.")

import sys 
import deploymentFunctions as depfunc

pathToTempRepoStorageParent='C:\\projects\\terraform\\azure-pipelines-system\\pipeline-scipts\\'
tmpRepoStorageFolder='tmpRepoStorage'
sourceRepo='https://github.com/AgileCloudInstitute/terraform-aws-simple-example.git'

pathToAzdoProviderInputs='C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\inputs-azdo-provider.tfvars'
pathToAzurermProviderInputs='C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\inputs-azurerm-provider.tfvars'
pathToAzdoProjectRepoBuildAutoInputs='C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\inputs-project-repo-build-auto.tfvars'
pathToAzdoProjectRepoBuildManualInputs='C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\inputs-project-repo-build-manual.tfvars'

getAzdoProviderInputs=' -var-file='+pathToAzdoProviderInputs
getAzurermProviderInputs=' -var-file='+pathToAzurermProviderInputs
getAzdoProjectRepoBuildAutoInputs=' -var-file='+pathToAzdoProjectRepoBuildAutoInputs
getAzdoProjectRepoBuildManualInputs=' -var-file='+pathToAzdoProjectRepoBuildManualInputs

initCommand='terraform init'
applyCommand='terraform apply -auto-approve'

pathToProjectRepoBuildCalls = "C:\\projects\\terraform\\azure-pipelines-system\\calls-to-modules\\azure-pipelines-project-repo-build-resources\\"
applyProjectRepoBuildCommand=applyCommand+getAzdoProviderInputs+getAzdoProjectRepoBuildAutoInputs+getAzdoProjectRepoBuildManualInputs+getAzurermProviderInputs

##############################################################################################
### Step One: Check to make sure that the azure devops terraform provider has been installed
##############################################################################################

#NEED TO ADD THIS.

##############################################################################################
### Step Two: Clone the source repo
##############################################################################################
depfunc.cloneSourceRepoToLocal(pathToTempRepoStorageParent,tmpRepoStorageFolder, sourceRepo)

##############################################################################################
### Step Three: Apply The azure-pipelines-project-repo-build module
##############################################################################################

depfunc.runTerraformCommand(initCommand, pathToProjectRepoBuildCalls)
depfunc.runTerraformCommand(applyProjectRepoBuildCommand, pathToProjectRepoBuildCalls)

print("Back in installProjectRepoBuild.py .")

##############################################################################################
### Step Four: Destroy local cloned copy of source repo
##############################################################################################
#depfunc.destroyLocalCloneOfSourceRepo(pathToTempRepoStorageParent,tmpRepoStorageFolder)

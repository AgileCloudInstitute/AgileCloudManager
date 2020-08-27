print("Inside installProjectRepoBuild.py script.")
import sys 
import deploymentFunctions as depfunc
import os 
import yaml 
    
##############################################################################################
### Step One:  Install azure devops extension for az client
##############################################################################################
#import subprocess
#import re
#ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

addExteensionCommand = 'az extension add --name azure-devops'
depfunc.runShellCommand(addExteensionCommand)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

myYamlInputFile = '/home/aci-user/staging/projectRepoBuildConfig.yaml'
foundationSecretsFile = '/home/aci-user/vars/agile-cloud-manager/foundation-secrets.tfvars'
prbSecretsFile = '/home/aci-user/vars/agile-cloud-manager/prb-secrets.tfvars'

#The awsCredFile is for the terraform backend that will store state for the azure infrastructure created for the agile cloud manager.
awsCredFile = '/home/aci-user/.aws/credentials'
initCommand='terraform init '
backendFoundationConfig = depfunc.getFoundationBackendConfig(myYamlInputFile, awsCredFile)
initBackendFoundationCommand = initCommand + backendFoundationConfig

outputCommand = 'terraform output '
#Environment variable set during cloud-init instantiation
acmRootDir=os.environ['ACM_ROOT_DIR']
pathToFoundationCalls = acmRootDir+"calls-to-modules/azure-pipelines-foundation-demo/"
  
##############################################################################################
### Step Two: Get Output from The azure-pipelines-foundation-demo module
##############################################################################################
depfunc.runTerraformCommand(initBackendFoundationCommand, pathToFoundationCalls)
depfunc.runTerraformCommand(outputCommand, pathToFoundationCalls)

print("depfunc.subscription_id  is: ", depfunc.subscription_id)
print("depfunc.tenant_id  is: ", depfunc.tenant_id)
print("depfunc.resourceGroupLocation  is: ", depfunc.resourceGroupLocation)
print("depfunc.resourceGroupName  is: ", depfunc.resourceGroupName)
print("depfunc.pipeKeyVaultName is: ", depfunc.pipeKeyVaultName)
print("depfunc.pipeSubnetId is: ", depfunc.pipeSubnetId)
print("depfunc.azuredevops_subscription_name is: ", depfunc.azuredevops_subscription_name)
print("depfunc.subscription_name is: ", depfunc.subscription_name)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# HOW SHOULD SECRETS FILES BE MANAGED?  foundationSecretsFile  awsCredFile
# HOW SHOULD MULTIPLE PROJECTREPOBUILD DEFINITIONS BE MANAGED?
# HOW SHOULD MULTIPLE BACKENDS BE MANAGED?  
# STILL NEED TO CREATE: depfunc.getProjectRepoBuildInputs(...)  AND depfunc.getProjectRepoBuildBackendConfig(...)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

##############################################################################################
### Step Three: Prepare the input variables for the azure-pipelines-project-repo-build-resources module
##############################################################################################

prbBackendConfig = depfunc.getProjectRepoBuildBackendConfig(myYamlInputFile, awsCredFile)
prbInputs = depfunc.getProjectsReposBuildInputs(myYamlInputFile, awsCredFile, prbSecretsFile, depfunc.subscription_id, depfunc.tenant_id, depfunc.resourceGroupLocation, depfunc.resourceGroupName, depfunc.pipeKeyVaultName, depfunc.pipeSubnetId, depfunc.subscription_name )

print("prbBackendConfig is: ", prbBackendConfig)
print("prbInputs is: ", prbInputs)

applyCommand='terraform apply -auto-approve'
## prbVars = depfunc.getProjectRepoBuildInputs(myYamlInputFile, foundationSecretsFile, depfunc.subscription_id, depfunc.tenant_id, depfunc.resourceGroupLocation, depfunc.resourceGroupName, depfunc.pipeKeyVaultName, depfunc.pipeSubnetId, depfunc.azuredevops_subscription_name)
applyPrbCommand=applyCommand+prbInputs
pathToPrbCalls = acmRootDir+"calls-to-modules/azure-pipelines-project-repo-build-resources/"
## print ('prbVars is: :', prbVars )
  
################################################################################################ 
### Step Three: Prepare the backend config for the azure-pipelines-project-repo-build-resources module
##############################################################################################
## backendPrbConfig = depfunc.getProjectRepoBuildBackendConfig(myYamlInputFile, awsCredFile)
initPrbCommand = initCommand + prbBackendConfig
## print("backendPrbConfig is: ", backendPrbConfig)

##############################################################################################
### Step Five: Initialize the Terraform backend for the azure-pipelines-project-repo-build-resources module
##############################################################################################
depfunc.runTerraformCommand(initPrbCommand, pathToPrbCalls)
depfunc.runTerraformCommand(applyPrbCommand, pathToPrbCalls)
print("Back in installProjectRepoBuild.py .")

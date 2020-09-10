print("Inside destroyProjectRepoBuild.py script.")  
import sys 
import deploymentFunctions as depfunc
import os 
import yaml 
    
##############################################################################################
### Step One:  Install azure devops extension for az client
##############################################################################################
addExteensionCommand = 'az extension add --name azure-devops'
depfunc.runShellCommand(addExteensionCommand)

#myYamlInputFile = 'projectRepoBuildConfig.yaml'
#////
YamlPRBFileName=sys.argv[1] 
yamlConfigDir = '/home/agile-cloud/staging/'
myYamlInputFile = yamlConfigDir + YamlPRBFileName
print("myYamlInputFile is: ", myYamlInputFile)
#////
foundationSecretsFile = '/home/agile-cloud/vars/agile-cloud-manager/foundation-secrets.tfvars'
prbSecretsFile = '/home/agile-cloud/vars/agile-cloud-manager/prb-secrets.tfvars'

#The awsCredFile is for the terraform backend that will store state for the azure infrastructure created for the agile cloud manager.
awsCredFile = '/home/agile-cloud/.aws/credentials'
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
prbInputs = depfunc.getProjectsReposBuildInputs(myYamlInputFile, awsCredFile, prbSecretsFile, depfunc.subscription_id, depfunc.tenant_id, depfunc.resourceGroupLocation, depfunc.resourceGroupName, depfunc.pipeSubnetId, depfunc.subscription_name )

print("prbBackendConfig is: ", prbBackendConfig)
print("prbInputs is: ", prbInputs)

destroyCommand='terraform destroy -auto-approve'
destroyPrbCommand=destroyCommand+prbInputs
pathToPrbCalls = acmRootDir+"calls-to-modules/azure-pipelines-project-repo-build-resources/"
  
################################################################################################ 
### Step Three: Prepare the backend config for the azure-pipelines-project-repo-build-resources module
##############################################################################################
initPrbCommand = initCommand + prbBackendConfig

##############################################################################################
### Step Five: Initialize the Terraform backend for the azure-pipelines-project-repo-build-resources module
##############################################################################################
depfunc.runTerraformCommand(initPrbCommand, pathToPrbCalls)
depfunc.runTerraformCommand(destroyPrbCommand, pathToPrbCalls)

print("Back in destroyProjectRepoBuild.py .")

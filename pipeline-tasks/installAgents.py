print("Inside installPipelineSystem.py script.")

import os
import sys 
import deploymentFunctions as depfunc

myYamlInputFile = '/home/aci-user/staging/agentsConfig.yaml'
foundationSecretsFile = '/home/aci-user/vars/agile-cloud-manager/foundation-secrets.tfvars'

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
### Step One: Get Output from The azure-pipelines-foundation-demo module
##############################################################################################
depfunc.runTerraformCommand(initBackendFoundationCommand, pathToFoundationCalls)
depfunc.runTerraformCommand(outputCommand, pathToFoundationCalls)

print("depfunc.subscription_id  is: ", depfunc.subscription_id)
print("depfunc.tenant_id  is: ", depfunc.tenant_id)
print("depfunc.resourceGroupLocation  is: ", depfunc.resourceGroupLocation)
print("depfunc.resourceGroupName  is: ", depfunc.resourceGroupName)
print("depfunc.nicName  is: ", depfunc.nicName)
print("depfunc.storName is: ", depfunc.storName)

##############################################################################################
### Step Two: Prepare the input variables for the azure-pipelines-agent-vms-demo module
##############################################################################################
applyCommand='terraform apply -auto-approve'
agentsVars = depfunc.getAgentsInputs(myYamlInputFile, foundationSecretsFile, depfunc.subscription_id, depfunc.tenant_id, depfunc.resourceGroupLocation, depfunc.resourceGroupName, depfunc.nicName, depfunc.storName )
applyAgentsCommand=applyCommand+agentsVars
pathToAgentCalls = acmRootDir+"calls-to-modules/azure-pipelines-agent-vms-demo/"
print ('agentsVars is: :', agentsVars )

################################################################################################ 
### Step Three: Prepare cloud init startup script for the azure-pipelines-agent-vms-demo module 
################################################################################################  
pathToCloudInitScript = depfunc.getCloudInitLocation(myYamlInputFile)  
depfunc.setEnvironmentVars(myYamlInputFile, pathToCloudInitScript)  

##############################################################################################
### Step Four: Prepare the backend config for the azure-pipelines-agent-vms-demo module
##############################################################################################
backendAgentsConfig = depfunc.getAgentsBackendConfig(myYamlInputFile, awsCredFile)
initAgentsCommand = initCommand + backendAgentsConfig
print("backendAgentsConfig is: ", backendAgentsConfig)

##############################################################################################
### Step Five: Initialize the Terraform backend for the azure-pipelines-agent-vms-demo module
##############################################################################################
depfunc.runTerraformCommand(initAgentsCommand, pathToAgentCalls)
depfunc.runTerraformCommand(applyAgentsCommand, pathToAgentCalls)
print("Back in installPipelineSystem.py .")

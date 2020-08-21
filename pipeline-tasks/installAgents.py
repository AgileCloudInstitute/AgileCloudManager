print("Inside installPipelineSystem.py script.")

import os
import sys 
import deploymentFunctions as depfunc

myYamlInputFile = '/home/aci-user/staging/enter-user-input-here-only.yaml'
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
print("depfunc.pipes_resource_group_region  is: ", depfunc.pipes_resource_group_region)
print("depfunc.pipes_resource_group_name  is: ", depfunc.pipes_resource_group_name)
print("depfunc.nicName  is: ", depfunc.nicName)
print("depfunc.storageAccountDiagName is: ", depfunc.storageAccountDiagName)

##############################################################################################
### Step Two: Prepare the input variables for the azure-pipelines-agent-vms-demo module
##############################################################################################
applyCommand='terraform apply -auto-approve'
agentsVars = depfunc.getAgentsInputs(myYamlInputFile, foundationSecretsFile, depfunc.subscription_id, depfunc.tenant_id, depfunc.pipes_resource_group_region, depfunc.pipes_resource_group_name, depfunc.nicName, depfunc.storageAccountDiagName )
applyAgentsCommand=applyCommand+AgentsVars
pathToAgentCalls = acmRootDir+"calls-to-modules/azure-pipelines-agent-vms-demo/"
print ('agentsVars is: :', agentsVars )

##############################################################################################
### Step Three: Prepare the backend config for the azure-pipelines-agent-vms-demo module
##############################################################################################
backendAgentsConfig = depfunc.getAgentsBackendConfig(myYamlInputFile, awsCredFile)
initAgentsCommand = initCommand + backendAgentsConfig
print("backendAgentsConfig is: ", backendAgentsConfig)

#//////////////////////////////////////////////////////////////////////////////////////////////////////

# ##############################################################################################
# ### Step One: Apply The azure-pipelines-foundation-demo module
# ##############################################################################################
# depfunc.runTerraformCommand(initBackendCommand, pathToFoundationCalls)
# #Can we get away with removing the cred file here yet?  We are removing it so that credentials can be passed into apply separately.
# #os.remove(awsCredFile)
# #UNCOMMENT THE NEXT LINE.
# depfunc.runTerraformCommand(applyFoundationCommand, pathToFoundationCalls)

# ### Now create the auto output of input variables for the agent-vms-demo module
# print("storName in installPipelineSystem.py is: ", depfunc.storName)
# valueToChange=depfunc.storName
# searchTermAgentInputs="storageAccountDiagName"
# depfunc.changeLineInFile(pathToAgentAutoInputs, searchTermAgentInputs, valueToChange)
# print("Back in installPipelineSystem.py .")

# print("nicName in installPipelineSystem.py is: ", depfunc.nicName)
# valueToChange=depfunc.nicName
# searchTermAgentInputs="nicName"
# depfunc.changeLineInFile(pathToAgentAutoInputs, searchTermAgentInputs, valueToChange)
# print("Back in installPipelineSystem.py .")


# print("resourceGroupName in installPipelineSystem.py is: ", depfunc.resourceGroupName)
# valueToChange=depfunc.resourceGroupName
# searchTermAgentInputs="resourceGroupName"
# depfunc.changeLineInFile(pathToAgentAutoInputs, searchTermAgentInputs, valueToChange)
# print("Back in installPipelineSystem.py .")


# print("resourceGroupLocation in installPipelineSystem.py is: ", depfunc.resourceGroupLocation)
# valueToChange=depfunc.resourceGroupLocation
# searchTermAgentInputs="resourceGroupLocation"
# depfunc.changeLineInFile(pathToAgentAutoInputs, searchTermAgentInputs, valueToChange)
# print("Back in installPipelineSystem.py .")

# #### Next create the auto output for the project-repo-build input file:

# print("pipeSubnetId in installPipelineSystem.py is: ", depfunc.pipeSubnetId)
# valueToChange=depfunc.pipeSubnetId
# searchTermAgentInputs="pipeSubnetId"
# depfunc.changeLineInFile(pathToAzdoProjectRepoBuildAutoInputs, searchTermAgentInputs, valueToChange)
# print("Back in installPipelineSystem.py .")

# print("pipeResourceGroupName in installPipelineSystem.py is: ", depfunc.resourceGroupName)
# valueToChange=depfunc.resourceGroupName
# searchTermAgentInputs="pipeResourceGroupName"
# depfunc.changeLineInFile(pathToAzdoProjectRepoBuildAutoInputs, searchTermAgentInputs, valueToChange)
# print("Back in installPipelineSystem.py .")

# print("pipeResourceGroupRegion in installPipelineSystem.py is: ", depfunc.resourceGroupLocation)
# valueToChange=depfunc.resourceGroupLocation
# searchTermAgentInputs="pipeResourceGroupRegion"
# depfunc.changeLineInFile(pathToAzdoProjectRepoBuildAutoInputs, searchTermAgentInputs, valueToChange)
# print("Back in installPipelineSystem.py .")

# print("pipeKeyVaultName in installPipelineSystem.py is: ", depfunc.pipeKeyVaultName)
# valueToChange=depfunc.pipeKeyVaultName
# searchTermAgentInputs="pipeKeyVaultName"
# depfunc.changeLineInFile(pathToAzdoProjectRepoBuildAutoInputs, searchTermAgentInputs, valueToChange)
# print("Back in installPipelineSystem.py .")


# ##############################################################################################
# ### Step Two: Apply the azure-pipelines-agent-vms-demo module
# ##############################################################################################
# depfunc.runTerraformCommand(initCommand, pathToAgentCalls)
# depfunc.runTerraformCommand(applyAgentCommand, pathToAgentCalls)
# print("Back in installPipelineSystem.py .")

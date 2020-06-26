
print("Inside installPipelineSystem.py script.")

import os
import sys 
import deploymentFunctions as depfunc

#The following are created/populated when you run  setup.sh at the time you download this repo.
pathToAgentAutoInputs='/home/aci-user/vars/agile-cloud-manager/inputs-agent-vms-auto.tfvars'
pathToAgentManualInputs='/home/aci-user/vars/agile-cloud-manager/inputs-agent-vms-manual.tfvars'
pathToAzurermProviderInputs='/home/aci-user/vars/agile-cloud-manager/inputs-azurerm-provider.tfvars'
pathToFoundationInputs='/home/aci-user/vars/agile-cloud-manager/inputs-foundation-demo.tfvars'
pathToAzdoProjectRepoBuildAutoInputs='/home/aci-user/vars/agile-cloud-manager/inputs-project-repo-build-auto.tfvars'

getAgentAutoInputs=' -var-file='+pathToAgentAutoInputs
getAgentManualInputs=' -var-file='+pathToAgentManualInputs
getAzurermProviderInputs=' -var-file='+pathToAzurermProviderInputs
getFoundationInputs=' -var-file='+pathToFoundationInputs

initCommand='terraform init'
applyCommand='terraform apply -auto-approve'
applyFoundationCommand=applyCommand+getAzurermProviderInputs+getFoundationInputs

#Environment variable set during cloud-init instantiation
acmRootDir=os.environ['ACM_ROOT_DIR']
pathToFoundationCalls = acmRootDir+"calls-to-modules/azure-pipelines-foundation-demo/"
pathToAgentCalls = acmRootDir+"calls-to-modules/azure-pipelines-agent-vms-demo/"
applyAgentCommand=applyCommand+getAzurermProviderInputs+getAgentAutoInputs+getAgentManualInputs

print ('getFoundationInputs:', getFoundationInputs )
print ('getAgentAutoInputs:', getAgentAutoInputs )

##############################################################################################
### Step One: Apply The azure-pipelines-foundation-demo module
##############################################################################################
depfunc.runTerraformCommand(initCommand, pathToFoundationCalls)
depfunc.runTerraformCommand(applyFoundationCommand, pathToFoundationCalls)

### Now create the auto output of input variables for the agent-vms-demo module
print("storName in installPipelineSystem.py is: ", depfunc.storName)
valueToChange=depfunc.storName
searchTermAgentInputs="storageAccountDiagName"
depfunc.changeLineInFile(pathToAgentAutoInputs, searchTermAgentInputs, valueToChange)
print("Back in installPipelineSystem.py .")

print("nicName in installPipelineSystem.py is: ", depfunc.nicName)
valueToChange=depfunc.nicName
searchTermAgentInputs="nicName"
depfunc.changeLineInFile(pathToAgentAutoInputs, searchTermAgentInputs, valueToChange)
print("Back in installPipelineSystem.py .")


print("resourceGroupName in installPipelineSystem.py is: ", depfunc.resourceGroupName)
valueToChange=depfunc.resourceGroupName
searchTermAgentInputs="resourceGroupName"
depfunc.changeLineInFile(pathToAgentAutoInputs, searchTermAgentInputs, valueToChange)
print("Back in installPipelineSystem.py .")


print("resourceGroupLocation in installPipelineSystem.py is: ", depfunc.resourceGroupLocation)
valueToChange=depfunc.resourceGroupLocation
searchTermAgentInputs="resourceGroupLocation"
depfunc.changeLineInFile(pathToAgentAutoInputs, searchTermAgentInputs, valueToChange)
print("Back in installPipelineSystem.py .")

#### Next create the auto output for the project-repo-build input file:

print("storageAccountNameTerraformBackend in installPipelineSystem.py is: ", depfunc.storageAccountNameTerraformBackend)
valueToChange=depfunc.storageAccountNameTerraformBackend
searchTermAgentInputs="storageAccountNameTerraformBackend"
depfunc.changeLineInFile(pathToAzdoProjectRepoBuildAutoInputs, searchTermAgentInputs, valueToChange)
print("Back in installPipelineSystem.py .")

print("pipeResourceGroupName in installPipelineSystem.py is: ", depfunc.resourceGroupName)
valueToChange=depfunc.resourceGroupName
searchTermAgentInputs="pipeResourceGroupName"
depfunc.changeLineInFile(pathToAzdoProjectRepoBuildAutoInputs, searchTermAgentInputs, valueToChange)
print("Back in installPipelineSystem.py .")

print("pipeKeyVaultName in installPipelineSystem.py is: ", depfunc.pipeKeyVaultName)
valueToChange=depfunc.pipeKeyVaultName
searchTermAgentInputs="pipeKeyVaultName"
depfunc.changeLineInFile(pathToAzdoProjectRepoBuildAutoInputs, searchTermAgentInputs, valueToChange)
print("Back in installPipelineSystem.py .")


##############################################################################################
### Step Two: Apply the azure-pipelines-agent-vms-demo module
##############################################################################################
depfunc.runTerraformCommand(initCommand, pathToAgentCalls)
depfunc.runTerraformCommand(applyAgentCommand, pathToAgentCalls)
print("Back in installPipelineSystem.py .")



print("Inside installPipelineSystem.py script.")

import os
import sys 
import deploymentFunctions as depfunc

#The following are created/populated when you run  setup.sh at the time you download this repo.
pathToAgentAutoInputs='/home/aci-user/vars/agile-cloud-manager/inputs-agent-vms-auto.tfvars'
pathToAgentManualInputs='/home/aci-user/vars/agile-cloud-manager/inputs-agent-vms-manual.tfvars'
pathToAzdoProviderInputs='/home/aci-user/vars/agile-cloud-manager/inputs-azdo-provider.tfvars'
pathToAzurermProviderInputs='/home/aci-user/vars/agile-cloud-manager/inputs-azurerm-provider.tfvars'
pathToFoundationInputs='/home/aci-user/vars/agile-cloud-manager/inputs-foundation-demo.tfvars'
pathToAzdoProjectRepoBuildInputs='/home/aci-user/vars/agile-cloud-manager/inputs-project-repo-build.tfvars'

getAgentAutoInputs=' -var-file='+pathToAgentAutoInputs
getAgentManualInputs=' -var-file='+pathToAgentManualInputs
getAzdoProviderInputs=' -var-file='+pathToAzdoProviderInputs
getAzurermProviderInputs=' -var-file='+pathToAzurermProviderInputs
getFoundationInputs=' -var-file='+pathToFoundationInputs
getAzdoProjectRepoBuildInputs=' -var-file='+pathToAzdoProjectRepoBuildInputs

initCommand='terraform init'
destroyCommand='terraform destroy -auto-approve'
destroyFoundationCommand=destroyCommand+getAzurermProviderInputs+getFoundationInputs

#Environment variable set during cloud-init instantiation
acmRootDir=os.environ['ACM_ROOT_DIR']
pathToFoundationCalls = acmRootDir+"calls-to-modules/azure-pipelines-foundation-demo/"
pathToAgentCalls = acmRootDir+"/calls-to-modules/azure-pipelines-agent-vms-demo/"
destroyAgentCommand=destroyCommand+getAzurermProviderInputs+getAgentAutoInputs+getAgentManualInputs

print ('pathToFoundationInputs:', pathToFoundationInputs )
print ('pathToAgentAutoInputs:', pathToAgentAutoInputs )

##############################################################################################
### Step One: Destroy the azure-pipelines-agent-vms-demo module
##############################################################################################
depfunc.runTerraformCommand(initCommand, pathToAgentCalls)
depfunc.runTerraformCommand(destroyAgentCommand, pathToAgentCalls)
print("Back in destroyPipelineSystem.py .")

##############################################################################################
### Step Two: Destroy the azure-pipelines-foundation-demo module
##############################################################################################
depfunc.runTerraformCommand(initCommand, pathToFoundationCalls)
depfunc.runTerraformCommand(destroyFoundationCommand, pathToFoundationCalls)
print("Back in destroyPipelineSystem.py .")


print("Inside installPipelineSystem.py script.")

import sys 
import deploymentFunctions as depfunc

#/////////////////////////////////////////////////////////
pathToAgentAutoInputs='C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\inputs-agent-vms-auto.tfvars'
pathToAgentManualInputs='C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\inputs-agent-vms-manual.tfvars'
pathToAzdoProviderInputs='C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\inputs-azdo-provider.tfvars'
pathToAzurermProviderInputs='C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\inputs-azurerm-provider.tfvars'
pathToFoundationInputs='C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\inputs-foundation-demo.tfvars'
pathToAzdoProjectRepoBuildInputs='C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\inputs-project-repo-build.tfvars'

getAgentAutoInputs=' -var-file='+pathToAgentAutoInputs
getAgentManualInputs=' -var-file='+pathToAgentManualInputs
getAzdoProviderInputs=' -var-file='+pathToAzdoProviderInputs
getAzurermProviderInputs=' -var-file='+pathToAzurermProviderInputs
getFoundationInputs=' -var-file='+pathToFoundationInputs
getAzdoProjectRepoBuildInputs=' -var-file='+pathToAzdoProjectRepoBuildInputs

initCommand='terraform init'
destroyCommand='terraform destroy -auto-approve'
destroyFoundationCommand=destroyCommand+getAzurermProviderInputs+getFoundationInputs

pathToFoundationCalls = "C:\\projects\\terraform\\azure-pipelines-system\\calls-to-modules\\azure-pipelines-foundation-demo\\"
pathToAgentCalls = "C:\\projects\\terraform\\azure-pipelines-system\\calls-to-modules\\azure-pipelines-agent-vms-demo\\"
destroyAgentCommand=destroyCommand+getAzurermProviderInputs+getAgentAutoInputs+getAgentManualInputs
#/////////////////////////////////////////////////////////

#pathToFoundationInputs = 'C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\azure-pipelines-foundation\\inputs.tfvars'
#pathToAgentInputs = 'C:\\projects\\terraform\\tfvars\\agile-cloud-manager\\azure-pipelines-agent-vms\\inputs.tfvars'
#initCommand='terraform init'
#destroyCommand='terraform destroy -auto-approve -var-file='
#destroyFoundationCommand=destroyCommand+pathToFoundationInputs

#pathToFoundationCalls = "C:\\projects\\terraform\\azure-pipelines-system\\calls-to-modules\\azure-pipelines-foundation-demo\\"
#pathToAgentCalls = "C:\\projects\\terraform\\azure-pipelines-system\\calls-to-modules\\azure-pipelines-agent-vms-demo\\"
#destroyAgentCommand=destroyCommand+pathToAgentInputs

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

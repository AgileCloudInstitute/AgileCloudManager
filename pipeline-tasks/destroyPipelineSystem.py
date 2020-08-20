print("Inside installPipelineSystem.py script.")

import os
import sys 
import deploymentFunctions as depfunc

# #The following are created/populated when you run  setup.py
myYamlInputFile = '/home/aci-user/staging/enter-user-input-here-only.yaml'
foundationSecretsFile = '/home/aci-user/vars/agile-cloud-manager/foundation-secrets.tfvars'

#The awsCredFile is for the terraform backend that will store state for the azure infrastructure created for the agile cloud manager.
awsCredFile = '/home/aci-user/.aws/credentials'

initCommand='terraform init '

backendConfig = depfunc.getFoundationBackendConfig(myYamlInputFile, awsCredFile)
initBackendCommand = initCommand + backendConfig

destroyCommand='terraform destroy -auto-approve'
foundationVars = depfunc.getFoundationInputs(myYamlInputFile, foundationSecretsFile)
destroyFoundationCommand=destroyCommand+foundationVars

#Environment variable set during cloud-init instantiation
acmRootDir=os.environ['ACM_ROOT_DIR']
pathToFoundationCalls = acmRootDir+"calls-to-modules/azure-pipelines-foundation-demo/"

print ('foundationVars is: :', foundationVars )

##############################################################################################
### Step One: Destroy the azure-pipelines-foundation-demo module
##############################################################################################
depfunc.runTerraformCommand(initBackendCommand, pathToFoundationCalls)
depfunc.runTerraformCommand(destroyFoundationCommand, pathToFoundationCalls)
print("Back in destroyPipelineSystem.py .")

print("Inside installProjectRepoBuild.py script.")

import sys 
import deploymentFunctions as depfunc

##############################################################################################
### Step One:  Install azure devops extension for az client
##############################################################################################
import subprocess
import re

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def runShellCommand(commandToRun):
    print("Inside runShellCommand(..., ...) function. ")
    print("commandToRun is: " +commandToRun)

    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        print(decodedline)
      else:
        break
  
addExteensionCommand = 'az extension add --name azure-devops'
runShellCommand(addExteensionCommand)

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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
print("depfunc.resourceGroupLocation  is: ", depfunc.resourceGroupLocation)
print("depfunc.resourceGroupName  is: ", depfunc.resourceGroupName)
print("depfunc.nicName  is: ", depfunc.nicName)
print("depfunc.storName is: ", depfunc.storName)

##############################################################################################
### Step Two: Prepare the input variables for the azure-pipelines-project-repo-build-resources module
##############################################################################################
applyCommand='terraform apply -auto-approve'
prbVars = depfunc.getAgentsInputs(myYamlInputFile, foundationSecretsFile, depfunc.subscription_id, depfunc.tenant_id, depfunc.resourceGroupLocation, depfunc.resourceGroupName, depfunc.nicName, depfunc.storName )
applyPrbCommand=applyCommand+prbVars
pathToPrbCalls = acmRootDir+"calls-to-modules/azure-pipelines-project-repo-build-resources/"
print ('prbVars is: :', prbVars )
  
################################################################################################ 
### Step Three: Prepare the backend config for the azure-pipelines-project-repo-build-resources module
##############################################################################################
backendPrbConfig = depfunc.getAgentsBackendConfig(myYamlInputFile, awsCredFile)
initPrbCommand = initCommand + backendPrbConfig
print("backendPrbConfig is: ", backendPrbConfig)

##############################################################################################
### Step Five: Initialize the Terraform backend for the azure-pipelines-project-repo-build-resources module
##############################################################################################
depfunc.runTerraformCommand(initPrbCommand, pathToPrbCalls)
depfunc.runTerraformCommand(applyPrbCommand, pathToPrbCalls)
print("Back in installPipelineSystem.py .")

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

##############################################################################################
### Step Two: Apply The azure-pipelines-project-repo-build module
##############################################################################################

depfunc.runTerraformCommand(initCommand, pathToProjectRepoBuildCalls)
depfunc.runTerraformCommand(applyProjectRepoBuildCommand, pathToProjectRepoBuildCalls)

print("Back in installProjectRepoBuild.py .")

print("depfunc.azuredevops_project_name is: ", depfunc.azuredevops_project_name)
print("depfunc.azuredevops_git_repository_name is: ", depfunc.azuredevops_git_repository_name)



print("Inside installProjectRepoBuild.py script.")

import sys 
import deploymentFunctions as depfunc

pathToTempRepoStorageParent='/home/aci-user/cloned-repos/agile-cloud-manager/pipeline-scipts/'
tmpRepoStorageFolder='tmpRepoStorage'
sourceRepo='https://github.com/AgileCloudInstitute/terraform-aws-simple-example.git'

pathToAzdoProviderInputs='/home/aci-user/vars/agile-cloud-manager/inputs-azdo-provider.tfvars'
pathToAzurermProviderInputs='/home/aci-user/vars/agile-cloud-manager/inputs-azurerm-provider.tfvars'
pathToAzdoProjectRepoBuildAutoInputs='/home/aci-user/vars/agile-cloud-manager/inputs-project-repo-build-auto.tfvars'
pathToAzdoProjectRepoBuildManualInputs='/home/aci-user/vars/agile-cloud-manager/inputs-project-repo-build-manual.tfvars'

getAzdoProviderInputs=' -var-file='+pathToAzdoProviderInputs
getAzurermProviderInputs=' -var-file='+pathToAzurermProviderInputs
getAzdoProjectRepoBuildAutoInputs=' -var-file='+pathToAzdoProjectRepoBuildAutoInputs
getAzdoProjectRepoBuildManualInputs=' -var-file='+pathToAzdoProjectRepoBuildManualInputs

initCommand='terraform init'
applyCommand='terraform apply -auto-approve'

pathToProjectRepoBuildCalls = "/home/aci-user/cloned-repos/agile-cloud-manager/calls-to-modules/azure-pipelines-project-repo-build-resources/"
applyProjectRepoBuildCommand=applyCommand+getAzdoProviderInputs+getAzdoProjectRepoBuildAutoInputs+getAzdoProjectRepoBuildManualInputs+getAzurermProviderInputs

##############################################################################################
### Step One: Check to make sure that the azure devops terraform provider has been installed
##############################################################################################

#NEED TO ADD THIS.

##############################################################################################
### Step Two: Clone the source repo
##############################################################################################
#depfunc.cloneSourceRepoToLocal(pathToTempRepoStorageParent,tmpRepoStorageFolder, sourceRepo)

##############################################################################################
### Step Three: Apply The azure-pipelines-project-repo-build module
##############################################################################################

depfunc.runTerraformCommand(initCommand, pathToProjectRepoBuildCalls)
depfunc.runTerraformCommand(applyProjectRepoBuildCommand, pathToProjectRepoBuildCalls)

print("Back in installProjectRepoBuild.py .")

print("sourceRepo is: ", sourceRepo)
print("depfunc.azuredevops_project_name is: ", depfunc.azuredevops_project_name)
print("depfunc.azuredevops_git_repository_name is: ", depfunc.azuredevops_git_repository_name)


##############################################################################################
### Step Four: Destroy local cloned copy of source repo
##############################################################################################
#depfunc.destroyLocalCloneOfSourceRepo(pathToTempRepoStorageParent,tmpRepoStorageFolder)



##############################################################################################
### Step Five:  Install azure devops extension for az client
##############################################################################################
import subprocess
import re

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def runShellCommand(commandToRun, workingDir ):
    print("Inside runShellCommand(..., ...) function. ")
    print("commandToRun is: " +commandToRun)
    print("workingDir is: " +workingDir)

    proc = subprocess.Popen( commandToRun,stdout=subprocess.PIPE, shell=True)
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

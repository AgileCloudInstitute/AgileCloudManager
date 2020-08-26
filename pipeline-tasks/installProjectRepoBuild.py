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

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

myYamlInputFile = '/home/aci-user/staging/projectRepoBuildConfig.yaml'
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
print("depfunc.pipeKeyVaultName is: ", depfunc.pipeKeyVaultName)
print("depfunc.pipeSubnetId is: ", depfunc.pipeSubnetId)
print("depfunc.azuredevops_subscription_name is: ", depfunc.azuredevops_subscription_name)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# HOW SHOULD SECRETS FILES BE MANAGED?  foundationSecretsFile  awsCredFile
# HOW SHOULD MULTIPLE PROJECTREPOBUILD DEFINITIONS BE MANAGED?
# HOW SHOULD MULTIPLE BACKENDS BE MANAGED?  
# STILL NEED TO CREATE: depfunc.getProjectRepoBuildInputs(...)  AND depfunc.getProjectRepoBuildBackendConfig(...)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

##############################################################################################
### Step Two: Prepare the input variables for the azure-pipelines-project-repo-build-resources module
##############################################################################################

def loopProjectsReposBuilds(yamlInputFile):
  print("inside loopProjectsReposBuilds(...,...,...) function.")
  #Now populate the variables
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("projectRepoBuilds", item):
        projectRepoBuildsItems = topLevel_dict.get(item)
        for projectRepoBuildItem in projectRepoBuildsItems: 
          if re.match("name", projectRepoBuildItem):
            print(projectRepoBuildItem, " is: ", projectRepoBuildsItems.get(projectRepoBuildItem))

loopProjectsReposBuilds(myYamlInputFile)

## /////////////////////////////////////////////////////////////////////////////
## applyCommand='terraform apply -auto-approve'
## prbVars = depfunc.getProjectRepoBuildInputs(myYamlInputFile, foundationSecretsFile, depfunc.subscription_id, depfunc.tenant_id, depfunc.resourceGroupLocation, depfunc.resourceGroupName, depfunc.pipeKeyVaultName, depfunc.pipeSubnetId, depfunc.azuredevops_subscription_name)
## applyPrbCommand=applyCommand+prbVars
## pathToPrbCalls = acmRootDir+"calls-to-modules/azure-pipelines-project-repo-build-resources/"
## print ('prbVars is: :', prbVars )
  
## ################################################################################################ 
## ### Step Three: Prepare the backend config for the azure-pipelines-project-repo-build-resources module
## ##############################################################################################
## backendPrbConfig = depfunc.getProjectRepoBuildBackendConfig(myYamlInputFile, awsCredFile)
## initPrbCommand = initCommand + backendPrbConfig
## print("backendPrbConfig is: ", backendPrbConfig)

## ##############################################################################################
## ### Step Five: Initialize the Terraform backend for the azure-pipelines-project-repo-build-resources module
## ##############################################################################################
## depfunc.runTerraformCommand(initPrbCommand, pathToPrbCalls)
## depfunc.runTerraformCommand(applyPrbCommand, pathToPrbCalls)
## print("Back in installProjectRepoBuild.py .")

## THE INPUT VARIABLES FOR EACH PRB ARE:
# .awsPublicAccessKey
# .awsSecretAccessKey
# .s3BucketNameTF
# .s3BucketRegionTF
# .dynamoDbTableNameTF
# .moduleKeyProjectRepoBuild

# _/\subscriptionName
# _/\subscriptionId
# _/\tenantId
# .clientName
# .clientId
# .clientSecret
# .serviceConnectionName
# .storageAccountNameTerraformBackend
# .storageContainerNameTerraformBackend
# _/\pipeSubnetId
# _/\pipeResourceGroupRegion
# _/\pipeResourceGroupName
# _/\pipeKeyVaultName
# .azdoOrgPAT
# .azdoOrgServiceURL
# .sourceRepo
# .projectName
# .repoName
# .buildName
# .awsPublicAccessKey
# .awsSecretAccessKey

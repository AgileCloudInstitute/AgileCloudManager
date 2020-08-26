print("Inside installProjectRepoBuild.py script.")

import sys 
import deploymentFunctions as depfunc
import os 
import yaml 
  
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
def getBackendConfigStarter(yamlInputFile, awsCredFile):
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("awsBackendTF", item):
        awsBackendItems = topLevel_dict.get(item)
        for awsBackendItem in awsBackendItems: 
          if re.match("awsPublicAccessKey", awsBackendItem):
            print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
            awsPublicAccessKey = awsBackendItems.get(awsBackendItem)
          if re.match("awsSecretAccessKey", awsBackendItem):
            print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
            awsSecretAccessKey = awsBackendItems.get(awsBackendItem)
          if re.match("s3BucketNameTF", awsBackendItem):
            print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
            varsString = varsString + " -backend-config \"bucket=" + awsBackendItems.get(awsBackendItem) +"\""  
          if re.match("s3BucketRegionTF", awsBackendItem):
            print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
            varsString = varsString + " -backend-config \"region=" + awsBackendItems.get(awsBackendItem) +"\""  
          if re.match("dynamoDbTableNameTF", awsBackendItem):
            print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
            varsString = varsString + " -backend-config \"dynamodb_table=" + awsBackendItems.get(awsBackendItem) +"\""  
  if ((len(awsPublicAccessKey) > 3) and (len(awsSecretAccessKey) > 3)):  
    with open(awsCredFile, "w") as file:
      lineToAdd = '[default]\n'
      file.write(lineToAdd)
      lineToAdd = "aws_access_key_id="+awsPublicAccessKey+"\n"
      file.write(lineToAdd)
      lineToAdd = "aws_secret_access_key="+awsSecretAccessKey+"\n"
      file.write(lineToAdd)
  print("varsString is: ", varsString)
  return varsString

def loopProjectsReposBuilds(yamlInputFile, awsCredFile):
  print("inside loopProjectsReposBuilds(...,...,...) function.")
  awsPublicAccessKey = ''
  awsSecretAccessKey = ''
  #Now populate the variables
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("projectRepoBuilds", item):
        projectRepoBuildsItems = topLevel_dict.get(item)
        for projectRepoBuild in projectRepoBuildsItems: 
          backendVars = ''
          for projectRepoBuildProperty in projectRepoBuild:
            if re.match("moduleKeyProjectRepoBuild", projectRepoBuildProperty):
              print(projectRepoBuildProperty, " is: ", projectRepoBuild.get(projectRepoBuildProperty))
              backendVarsStarter = getBackendConfigStarter(yamlInputFile, awsCredFile)
              backendVars = backendVarsStarter + " -backend-config \"key=" + projectRepoBuild.get(projectRepoBuildProperty) +"\""  
          print("backendVars is: ", backendVars)

loopProjectsReposBuilds(myYamlInputFile, awsCredFile)

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

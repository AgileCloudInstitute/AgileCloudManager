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
prbSecretsFile = '/home/aci-user/vars/agile-cloud-manager/prb-secrets.tfvars'

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
  varsString = ''
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

def getProjectRepoBuildInputsStarter(yamlInputFile, prbSecretsFile):
  varsString = ''
  azdoOrgPAT = ''
  clientSecret = ''
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      print("item is: ", item)
      if re.match("azdoConnection", item):  
        connectionItems = topLevel_dict.get(item)  
        for connectionItem in connectionItems:
          if re.match("azdoOrgServiceURL", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
            varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
          if re.match("clientName", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
            varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
          if re.match("serviceConnectionName", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
            varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
          if re.match("clientId", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
            varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
          if re.match("azdoOrgPAT", connectionItem):
            azdoOrgPAT = connectionItems.get(connectionItem)
          if re.match("clientSecret", connectionItem):
            clientSecret = connectionItems.get(connectionItem)
  with open(prbSecretsFile, "w") as file:
    lineToAdd = "azdoOrgPAT=\""+azdoOrgPAT +"\"\n"
    file.write(lineToAdd)
    lineToAdd = "clientSecret=\""+clientSecret +"\"\n"
    file.write(lineToAdd)
    varsString = varsString + " -var-file=\""+ prbSecretsFile +"\""
  print("varsString is: ", varsString)
  return varsString

def loopProjectsReposBuilds(yamlInputFile, awsCredFile, prbSecretsFile):
  print("inside loopProjectsReposBuilds(...,...,...) function.")
  awsPublicAccessKey = ''
  awsSecretAccessKey = ''
  projectName = ''
  repoName = ''
  buildName = ''
  #Now populate the variables
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("projectRepoBuilds", item):
        projectRepoBuildsItems = topLevel_dict.get(item)
        for projectRepoBuild in projectRepoBuildsItems: 
          prbVarsStarter = getProjectRepoBuildInputsStarter(yamlInputFile, prbSecretsFile)
          prbVars = prbVarsStarter
          backendVars = ''
          for projectRepoBuildProperty in projectRepoBuild:
            if re.match("sourceRepo", projectRepoBuildProperty):
              print(projectRepoBuildProperty, " is: ", projectRepoBuild.get(projectRepoBuildProperty))
              prbVars = prbVars + " -var=\""+ projectRepoBuildProperty + "=" + projectRepoBuild.get(projectRepoBuildProperty) +"\""  
              nameStr = projectRepoBuild.get(projectRepoBuildProperty)
              nameStr = projectNameStr.replace(" ", "")
              if nameStr.endswith('.git'):
                repoName = nameStr[:-4]
              buildName = repoName
              projectName = repoName + "Project"
            if re.match("storageAccountNameTerraformBackend", projectRepoBuildProperty):
              print(projectRepoBuildProperty, " is: ", projectRepoBuild.get(projectRepoBuildProperty))
              prbVars = prbVars + " -var=\""+ projectRepoBuildProperty + "=" + projectRepoBuild.get(projectRepoBuildProperty) +"\""  
            if re.match("storageContainerNameTerraformBackend", projectRepoBuildProperty):
              print(projectRepoBuildProperty, " is: ", projectRepoBuild.get(projectRepoBuildProperty))
              prbVars = prbVars + " -var=\""+ projectRepoBuildProperty + "=" + projectRepoBuild.get(projectRepoBuildProperty) +"\""  
            if re.match("awsPublicAccessKey", projectRepoBuildProperty):
              awsPublicAccessKey = projectRepoBuild.get(projectRepoBuildProperty)
            if re.match("awsSecretAccessKey", projectRepoBuildProperty):
              awsSecretAccessKey = projectRepoBuild.get(projectRepoBuildProperty)
            if re.match("moduleKeyProjectRepoBuild", projectRepoBuildProperty):
              print(projectRepoBuildProperty, " is: ", projectRepoBuild.get(projectRepoBuildProperty))
              backendVarsStarter = getBackendConfigStarter(yamlInputFile, awsCredFile)
              backendVars = backendVarsStarter + " -backend-config \"key=" + projectRepoBuild.get(projectRepoBuildProperty) +"\""  
          prbVars = prbVars + " -var=\"projectName=" + projectName +"\""  
          prbVars = prbVars + " -var=\"repoName=" + repoName +"\""  
          prbVars = prbVars + " -var=\"buildName=" + buildName +"\""  
          print("prbVars is: ", prbVars)
          print("backendVars is: ", backendVars)

loopProjectsReposBuilds(myYamlInputFile, awsCredFile, prbSecretsFile)

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

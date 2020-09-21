print("Inside installProjectRepoBuild.py script.")
import sys 
import deploymentFunctions as depfunc
import os 
import yaml 
  
def createBackendConfigFileTerraform( dir_to_use ): 
  tfFileNameAndPath=dir_to_use+"/terraform.tf"
  print("tfFileNameAndPath is: ", tfFileNameAndPath)
  print("About to write 4 lines to a backend config file.")
  f = open(tfFileNameAndPath, "w")
  f.write("terraform {\n")
  f.write("  backend \"s3\" {\n")
  f.write("  }\n")
  f.write("}\n")
  f.close()
  
##############################################################################################
### Step One:  Install azure devops extension for az client
##############################################################################################
addExteensionCommand = 'az extension add --name azure-devops'
depfunc.runShellCommand(addExteensionCommand)

YamlPRBFileName=sys.argv[1]   
yamlConfigDir = '/home/agile-cloud/staging/'  
myYamlInputFile = yamlConfigDir + YamlPRBFileName  
print("myYamlInputFile is: ", myYamlInputFile)  
    
#foundationSecretsFile = '/home/agile-cloud/vars/agile-cloud-manager/foundation-secrets.tfvars'
prbSecretsFile = '/home/agile-cloud/vars/agile-cloud-manager/prb-secrets.tfvars'

#The awsCredFile is for the terraform backend that will store state for the azure infrastructure created for the agile cloud manager.
awsCredFile = '/home/agile-cloud/.aws/credentials'

##############################################################################################
### Step Two: Get Output from The azure-pipelines-foundation-demo module
##############################################################################################
initCommand='terraform init '
backendFoundationConfig = depfunc.getFoundationBackendConfig(myYamlInputFile, awsCredFile)
initBackendFoundationCommand = initCommand + backendFoundationConfig

outputCommand = 'terraform output '
#Environment variable set during cloud-init instantiation
acmRootDir=os.environ['ACM_ROOT_DIR']
pathToFoundationCalls = acmRootDir+"calls-to-modules/azure-pipelines-foundation-demo/"
  
depfunc.runTerraformCommand(initBackendFoundationCommand, pathToFoundationCalls)
depfunc.runTerraformCommand(outputCommand, pathToFoundationCalls)

print("depfunc.subscription_id  is: ", depfunc.subscription_id)
print("depfunc.tenant_id  is: ", depfunc.tenant_id)
print("depfunc.resourceGroupLocation  is: ", depfunc.resourceGroupLocation)
print("depfunc.resourceGroupName  is: ", depfunc.resourceGroupName)
print("depfunc.pipeSubnetId is: ", depfunc.pipeSubnetId)
print("depfunc.azuredevops_subscription_name is: ", depfunc.azuredevops_subscription_name)
print("depfunc.subscription_name is: ", depfunc.subscription_name)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# HOW SHOULD SECRETS FILES BE MANAGED?  foundationSecretsFile  awsCredFile
# HOW SHOULD MULTIPLE PROJECTREPOBUILD DEFINITIONS BE MANAGED?
# HOW SHOULD MULTIPLE BACKENDS BE MANAGED?  
# STILL NEED TO CREATE: depfunc.getProjectRepoBuildInputs(...)  AND depfunc.getProjectRepoBuildBackendConfig(...)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

##############################################################################################
### Step Three: Get Project Name from YAML
##############################################################################################
import re
def getProjectName(yamlInputFile):
  print("inside getProjectName(...) function.")
  projectName = ''
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      print("item is: ", item)
      if re.match("projectRepoBuild", item):
        projectRepoBuild = topLevel_dict.get(item)
        for prbItem in projectRepoBuild:
            if re.match("projectName", prbItem):
              print(prbItem, " is: ", projectRepoBuild.get(prbItem))
              projectName = projectRepoBuild.get(prbItem)
  print("projectName is: ", projectName)
  return projectName
  
project_name = getProjectName(myYamlInputFile)
#Create new directory for call to this specific project
call_name = "call-to-" + project_name  
call_to_project_dir = acmRootDir+"calls-to-modules/instances/"+call_name
print("call_to_project_dir is: ", call_to_project_dir)
if not os.path.exists('call_to_project_dir'):
    os.makedirs('call_to_project_dir')

# ##############################################################################################
# ### Step Three: Prepare the input variables for the azure-pipelines-project-repo-build-resources module
# ##############################################################################################

# prbBackendConfig = depfunc.getProjectRepoBuildBackendConfig(myYamlInputFile, awsCredFile)
# prbInputs = depfunc.getProjectsReposBuildInputs(myYamlInputFile, awsCredFile, prbSecretsFile, depfunc.subscription_id, depfunc.tenant_id, depfunc.resourceGroupLocation, depfunc.resourceGroupName, depfunc.pipeSubnetId, depfunc.subscription_name )  
  
# print("prbBackendConfig is: ", prbBackendConfig)  
# print("prbInputs is: ", prbInputs)  
  
# applyCommand='terraform apply -auto-approve'
# applyPrbCommand=applyCommand+prbInputs
# pathToPrbCalls = acmRootDir+"calls-to-modules/azure-pipelines-project-repo-build-resources/"
# ## print ('prbVars is: :', prbVars )
  
# ################################################################################################ 
# ### Step Three: Prepare the backend config for the azure-pipelines-project-repo-build-resources module
# ##############################################################################################
# ## backendPrbConfig = depfunc.getProjectRepoBuildBackendConfig(myYamlInputFile, awsCredFile)
# initPrbCommand = initCommand + prbBackendConfig
# ## print("backendPrbConfig is: ", backendPrbConfig)

# ##############################################################################################
# ### Step Five: Initialize the Terraform backend for the azure-pipelines-project-repo-build-resources module
# ##############################################################################################
# depfunc.runTerraformCommand(initPrbCommand, pathToPrbCalls)
# depfunc.runTerraformCommand(applyPrbCommand, pathToPrbCalls)
# print("Back in installProjectRepoBuild.py .")
# #About to remove prbSecrets file so that it can be refreshed every time it is used, and thus avoid cross-contamination with other prb variants.  
# os.remove(prbSecretsFile)  
  

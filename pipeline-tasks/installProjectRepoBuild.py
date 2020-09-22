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

def getListOfSourceRepos(yamlInputFile):
  print("inside getListOfSourceRepos(...) function.")
  reposList = []
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      #print("item is: ", item)
      if re.match("projectRepoBuild", item):
        projectRepoBuild = topLevel_dict.get(item)
        for prbItem in projectRepoBuild:
          if re.match("sourceRepositories", prbItem):
            sourceRepositories = projectRepoBuild.get(prbItem)
            for sourceRepo in sourceRepositories:
              print("sourceRepo is: ", sourceRepo)
              #print(sourceRepositories.get(sourceRepo))
              reposList.append(sourceRepo)
  print("reposList is: ", reposList)
  return reposList

import shutil

def deleteContentsOfDirectoryRecursively(call_to_project_dir):  
    if [f for f in os.listdir(call_to_project_dir) if not f.startswith('.')] == []:  
        print(call_to_project_dir, " is empty. ")  
    else: 
        print(call_to_project_dir, " is NOT empty.  Deleting contents now, but consider backup strategy in case you do not want this auto-delete in your processes.  Currently, YAML input files are the source of truth for this demo.  You must decide where you want the source of truth to be in your system.  ")  
        for the_file in os.listdir(call_to_project_dir):
            file_path = os.path.join(call_to_project_dir, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

import os
#from shutil import *
def copyContentsOfDirectoryRecursively(src, dst, symlinks=False, ignore=None):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()
    if not os.path.isdir(dst): # This one line does the trick
        os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                shutil.copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Exception as err:  
            errors.extend(err.args[0])  
        except EnvironmentError as why:  
            errors.append((srcname, dstname, str(why)))  
    try:  
        shutil.copystat(src, dst)  
    except OSError as why:  
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Exception(errors)

# python3 code to search text in line and replace that line with other line in file 
#, backup ='.bak'
import fileinput 
def changePointerLineInCallToModule(fileName, searchTerm, newPointerLine): 
  with fileinput.FileInput(fileName, inplace = True) as f: 
    for line in f: 
      if searchTerm in line: 
        print(newPointerLine, end ='\n') 
      else: 
        print(line, end ='') 

def getProjectBackendConfig(yamlInputFile, awsCredFile):
  varsString = ''
  awsPublicAccessKey = ''
  awsSecretAccessKey = ''
  projectName = ''
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("projectRepoBuild", item):
        prbItems = topLevel_dict.get(item)
        for prbItem in prbItems: 
          if re.match("projectName", prbItem):
            projectName = prbItems.get(prbItem)
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
          if re.match("moduleKeyProject", awsBackendItem):
            print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
            keyVal = awsBackendItems.get(awsBackendItem) + projectName + ".tfstate"
            varsString = varsString + " -backend-config \"key=" + keyVal +"\""  
  #REPLACE THE FOLLOWING BLOCK WITH MORE ADVANCED VERSION CAPABLE OF HANDLING MULTIPLE ACCOUNTS
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

def getProjectInputs(yamlInputFile, awsCredFile, prbSecretsFile, subscriptionId, tenantId):  
  print("inside getProjectsReposBuildInputs(...,...,...) function.")
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
          if re.match("subscriptionName", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
            varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
          if re.match("clientName", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
            varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
          if re.match("clientId", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
            varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
          if re.match("azdoOrgPAT", connectionItem):
            azdoOrgPAT = connectionItems.get(connectionItem)
          if re.match("clientSecret", connectionItem):
            clientSecret = connectionItems.get(connectionItem)
      if re.match("projectRepoBuild", item):
        projectRepoBuild = topLevel_dict.get(item)
        for prbItem in projectRepoBuild:
          if re.match("projectName", prbItem):
            print(prbItem, " is: ", projectRepoBuild.get(prbItem))
            varsString = varsString + " -var=\""+ prbItem + "=" + projectRepoBuild.get(prbItem) +"\""  
  if len(subscriptionId) > 2: 
    varsString = varsString + " -var=\"subscriptionId=" + subscriptionId +"\""  
  if len(tenantId) > 2: 
    varsString = varsString + " -var=\"tenantId=" + tenantId +"\""  
  if len(azdoOrgPAT)>2 or len(clientSecret)>2 :  
    with open(prbSecretsFile, "w") as file:
      if len(azdoOrgPAT) > 2:
        lineToAdd = "azdoOrgPAT=\""+azdoOrgPAT +"\"\n"
        file.write(lineToAdd)
      if len(clientSecret) > 2: 
        lineToAdd = "clientSecret=\""+clientSecret +"\"\n"
        file.write(lineToAdd)
    varsString = varsString + " -var-file=\""+ prbSecretsFile +"\""
  print("varsString is: ", varsString)
  return varsString

def getRepoName(repoURL):
  repoName = repoURL.replace(" ", "")
  if repoName.endswith('.git'):
    repoName = repoName[:-4]
  repoName = repoName.rpartition('/')[2]
  print("repoName after cleaning is: ", repoName)
  return repoName

def getRepoBuildBackendConfig(repoName, yamlInputFile, awsCredFile):
  varsString = ''
  awsPublicAccessKey = ''
  awsSecretAccessKey = ''
  projectName = ''
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("projectRepoBuild", item):
        prbItems = topLevel_dict.get(item)
        for prbItem in prbItems: 
          if re.match("projectName", prbItem):
            projectName = prbItems.get(prbItem)
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
          if re.match("moduleKeyProject", awsBackendItem):
            print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
            keyRoot = awsBackendItems.get(awsBackendItem)
            if keyRoot[-1:] == "/":
              print("keyRoot ends with valid character. ")
            else: 
              print("About to add / to end of keyRoot.  ")
              keyRoot = keyRoot + "/"
            keyVal = keyRoot + projectName + "/repos/" + repoName + ".tfstate"
            varsString = varsString + " -backend-config \"key=" + keyVal +"\""  
  #REPLACE THE FOLLOWING BLOCK WITH MORE ADVANCED VERSION CAPABLE OF HANDLING MULTIPLE ACCOUNTS
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

def getRepoBuildInputs(yamlInputFile, awsCredFile, rbSecretsFile, projectName, sourceRepo, repoName):
  print("inside getRepoBuildInputs(...,...,...) function.")
  buildName = repoName
  varsString = ''
  azdoOrgPAT = ''
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
          if re.match("azdoOrgPAT", connectionItem):
            azdoOrgPAT = connectionItems.get(connectionItem)
  varsString = varsString + " -var=\"projectName=" + projectName +"\""  
  varsString = varsString + " -var=\"sourceRepo=" + sourceRepo +"\""  
  varsString = varsString + " -var=\"repoName=" + repoName +"\""  
  varsString = varsString + " -var=\"buildName=" + buildName +"\""  
  if len(azdoOrgPAT)>2 :  
    with open(rbSecretsFile, "w") as file:
      if len(azdoOrgPAT) > 2:
        lineToAdd = "azdoOrgPAT=\""+azdoOrgPAT +"\"\n"
        file.write(lineToAdd)
    varsString = varsString + " -var-file=\""+ rbSecretsFile +"\""
  print("varsString is: ", varsString)
  return varsString

def createInstanceOfTemplateCallToModule(call_to_project_dir, sourceDirOfTemplate, searchTerm, newPointerLine):
  if not os.path.exists(call_to_project_dir):
    os.makedirs(call_to_project_dir)
  #Check whether directory is empty or not.  If it is NOT empty, then delete the contents  
  deleteContentsOfDirectoryRecursively(call_to_project_dir)
  print("Now confirming that directory is empty before moving on.  ")
  deleteContentsOfDirectoryRecursively(call_to_project_dir)
  print("Now going to copy the template of the call to the project module into the new instance directory.")
  copyContentsOfDirectoryRecursively(sourceDirOfTemplate, call_to_project_dir, symlinks=False, ignore=None)
  print("Now going to change main.tf to point the call to the correct module directory.  ")
  fileName = call_to_project_dir + "/main.tf"
  changePointerLineInCallToModule(fileName, searchTerm, newPointerLine)
  print("Now going to create the terraform.tf file that will point to the remote backend. ")
  createBackendConfigFileTerraform( call_to_project_dir )

##############################################################################################
### Step One:  Install azure devops extension for az client
##############################################################################################
addExteensionCommand = 'az extension add --name azure-devops'
depfunc.runShellCommand(addExteensionCommand)

YamlPRBFileName=sys.argv[1]   
yamlConfigDir = '/home/agile-cloud/staging/'  
myYamlInputFile = yamlConfigDir + YamlPRBFileName  
print("myYamlInputFile is: ", myYamlInputFile)  
    
# #foundationSecretsFile = '/home/agile-cloud/vars/agile-cloud-manager/foundation-secrets.tfvars'

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
# #print("depfunc.resourceGroupLocation  is: ", depfunc.resourceGroupLocation)
# #print("depfunc.resourceGroupName  is: ", depfunc.resourceGroupName)
# #print("depfunc.pipeSubnetId is: ", depfunc.pipeSubnetId)
# #print("depfunc.azuredevops_subscription_name is: ", depfunc.azuredevops_subscription_name)
# #print("depfunc.subscription_name is: ", depfunc.subscription_name)

# #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# # HOW SHOULD SECRETS FILES BE MANAGED?  foundationSecretsFile  awsCredFile
# # HOW SHOULD MULTIPLE PROJECTREPOBUILD DEFINITIONS BE MANAGED?
# # HOW SHOULD MULTIPLE BACKENDS BE MANAGED?  
# # STILL NEED TO CREATE: depfunc.getProjectRepoBuildInputs(...)  AND depfunc.getProjectRepoBuildBackendConfig(...)
# #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

##########################################################################################################
### Step Three: Get Project Name from YAML.  
###             Then instantiate call to project module for this project by creating new 
###                     instance directory and copying the call template into the new directory.
##########################################################################################################

project_name = getProjectName(myYamlInputFile)
projectSecretsFile = '/home/agile-cloud/vars/agile-cloud-manager/'+project_name+'-project-secrets.tfvars'
project_calls_root = acmRootDir+"calls-to-modules/instances/projects/"+project_name+'/'

call_name = "call-to-" + project_name  
call_to_project_dir = project_calls_root+call_name  
print("call_to_project_dir is: ", call_to_project_dir)
sourceDirOfTemplate = "../calls-to-modules/azdo-templates/azure-devops-project/"  
newPointerLine="  source = \"../../../../../modules/azure-devops-project/\""
searchTerm = "/modules/azure-devops-project"  
createInstanceOfTemplateCallToModule(call_to_project_dir, sourceDirOfTemplate, searchTerm, newPointerLine)

##########################################################################################################
### Step Four:  Init and Apply the Project
##########################################################################################################

backendProjectConfig = getProjectBackendConfig(myYamlInputFile, awsCredFile)
initBackendProjectCommand = initCommand + backendProjectConfig
print("initBackendProjectCommand is: ", initBackendProjectCommand)
projectVars = getProjectInputs(myYamlInputFile, awsCredFile, projectSecretsFile, depfunc.subscription_id, depfunc.tenant_id )
print("projectVars is: ", projectVars)
applyProjectCommand = 'terraform apply -auto-approve ' + projectVars

depfunc.runTerraformCommand(initBackendProjectCommand, call_to_project_dir)
#Uncomment the following when you want to create
depfunc.runTerraformCommand(applyProjectCommand, call_to_project_dir)

#Comment out the following when you do not want to delete.
#destroyProjectCommand = 'terraform destroy -auto-approve ' + projectVars
#depfunc.runTerraformCommand(destroyProjectCommand, call_to_project_dir)

##########################################################################################################
### Step Five:  Get list of source repositories
##########################################################################################################
sourceReposList = getListOfSourceRepos(myYamlInputFile)  
print("sourceReposList is: ", sourceReposList)  

if len(sourceReposList) > 0:
  print(len(sourceReposList), " source repository URLs were imported from YAML input.  Going to process each now.  ")
  for sourceRepo in sourceReposList:
    print("sourceRepo before call to getRepoName() is: ", sourceRepo)
    nameOfRepo = getRepoName(sourceRepo)
    print("nameOfRepo returned by getNameRepo() is: ", nameOfRepo)
    #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    call_name = "call-to-" + nameOfRepo  
    call_to_repobuild_dir = project_calls_root+ "repo-builds/" + call_name  
    print("call_to_repobuild_dir is: ", call_to_repobuild_dir)
    sourceDirOfTemplate = "../calls-to-modules/azdo-templates/azure-devops-repo-build/"
    newPointerLine="  source = \"../../../../../../modules/azure-devops-repo-build/\""
    searchTerm = "/modules/azure-devops-repo-build"
    createInstanceOfTemplateCallToModule(call_to_repobuild_dir, sourceDirOfTemplate, searchTerm, newPointerLine)
    #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    backendConfigRepo = getRepoBuildBackendConfig(nameOfRepo, myYamlInputFile, awsCredFile)
    print("backendConfigRepo is: ", backendConfigRepo)
    initBackendRepoBuildCommand = initCommand + backendConfigRepo
    print("initBackendRepoBuildCommand is: ", initBackendRepoBuildCommand)

    rbSecretsFile = '/home/agile-cloud/vars/agile-cloud-manager/'+project_name+'-'+ nameOfRepo + '-repoBuild-secrets.tfvars'
    inputsRepoBuild = getRepoBuildInputs(myYamlInputFile, awsCredFile, rbSecretsFile, project_name, sourceRepo, nameOfRepo)
    print("inputsRepoBuild is: ", inputsRepoBuild)
    applyRepoBuildCommand = 'terraform apply -auto-approve ' + inputsRepoBuild
    print("applyRepoBuildCommand is: ", applyRepoBuildCommand)

    depfunc.runTerraformCommand(initBackendRepoBuildCommand, call_to_repobuild_dir)
    depfunc.runTerraformCommand(applyRepoBuildCommand, call_to_repobuild_dir)

    print("........................................................................................................")
else:
  print("Zero source repository URLs were imported from the YAML input.  ")

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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
  

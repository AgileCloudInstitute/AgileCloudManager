print("Inside installProjectRepoBuild.py script.")
import sys 
import deploymentFunctions as depfunc
import os 
import yaml 

##############################################################################################
### Step One:  Install azure devops extension for az client
##############################################################################################
addExteensionCommand = 'az extension add --name azure-devops'
depfunc.runShellCommand(addExteensionCommand)

##############################################################################################
### Step Two:  Populate the input variables
##############################################################################################
YamlPRBFileName=sys.argv[1]   
myYamlInputFile = '/home/agile-cloud/staging/' + YamlPRBFileName  
print("myYamlInputFile is: ", myYamlInputFile)  
#The awsCredFile is for the terraform backend that will store state for the azure infrastructure created for the agile cloud manager.
awsCredFile = '/home/agile-cloud/.aws/credentials'
#Environment variable set during cloud-init instantiation
acmRootDir=os.environ['ACM_ROOT_DIR']

##############################################################################################
### Step Three: Instantiate call to project module for this project by creating new 
###                     instance directory and copying the call template into the new directory.
##########################################################################################################
depfunc.instantiateProjectCall(myYamlInputFile, acmRootDir)

##########################################################################################################
### Step Four:  Apply Option
##########################################################################################################
crudOperation = "apply"
#First Apply the Project
depfunc.manageProject(crudOperation, myYamlInputFile, acmRootDir, awsCredFile, projectSecretsFile)
#Then Apply the Repo-Builds
sourceReposList = depfunc.getListOfSourceRepos(myYamlInputFile)  
depfunc.manageRepoBuilds(crudOperation, sourceReposList, project_calls_root, myYamlInputFile, awsCredFile, project_name)

# ##########################################################################################################
# ### Destroy Option
# ##########################################################################################################
# crudOperation = "destroy"
# #First Destroy The Repo-Builds
# sourceReposList = depfunc.getListOfSourceRepos(myYamlInputFile)  
# depfunc.manageRepoBuilds(crudOperation, sourceReposList, project_calls_root, myYamlInputFile, awsCredFile, project_name)
# #Then Destroy the Project
# manageProject(crudOperation, myYamlInputFile, acmRootDir, awsCredFile, projectSecretsFile, depfunc.subscription_id, depfunc.tenant_id)


##Destroy stuff.  Keeping the following line for now to remind us to later go throu and make sure every item is 
##destroyed after use so that everything must always be recreated by automation.    
# os.remove(prbSecretsFile)  
  

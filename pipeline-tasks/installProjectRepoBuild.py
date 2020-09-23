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

YamlPRBFileName=sys.argv[1]   
yamlConfigDir = '/home/agile-cloud/staging/'  
myYamlInputFile = yamlConfigDir + YamlPRBFileName  
print("myYamlInputFile is: ", myYamlInputFile)  

#The awsCredFile is for the terraform backend that will store state for the azure infrastructure created for the agile cloud manager.
awsCredFile = '/home/agile-cloud/.aws/credentials'
#Environment variable set during cloud-init instantiation
acmRootDir=os.environ['ACM_ROOT_DIR']

##############################################################################################
### Step Two: Get Output from The azure-pipelines-foundation-demo module
##############################################################################################
initCommand='terraform init '
backendFoundationConfig = depfunc.getFoundationBackendConfig(myYamlInputFile, awsCredFile)
initBackendFoundationCommand = initCommand + backendFoundationConfig

outputCommand = 'terraform output '
pathToFoundationCalls = acmRootDir+"calls-to-modules/azure-pipelines-foundation-demo/"
  
depfunc.runTerraformCommand(initBackendFoundationCommand, pathToFoundationCalls)
depfunc.runTerraformCommand(outputCommand, pathToFoundationCalls)

print("depfunc.subscription_id  is: ", depfunc.subscription_id)
print("depfunc.tenant_id  is: ", depfunc.tenant_id)

##########################################################################################################
### Step Three: Get Project Name from YAML.  
###             Then instantiate call to project module for this project by creating new 
###                     instance directory and copying the call template into the new directory.
##########################################################################################################

project_name = depfunc.getProjectName(myYamlInputFile)
projectSecretsFile = '/home/agile-cloud/vars/agile-cloud-manager/'+project_name+'-project-secrets.tfvars'
project_calls_root = acmRootDir+"calls-to-modules/instances/projects/"+project_name+'/'

call_name = "call-to-" + project_name  
call_to_project_dir = project_calls_root+call_name  
print("call_to_project_dir is: ", call_to_project_dir)
sourceDirOfTemplate = "../calls-to-modules/azdo-templates/azure-devops-project/"  
newPointerLine="  source = \"../../../../../modules/azure-devops-project/\""
searchTerm = "/modules/azure-devops-project"  
depfunc.createInstanceOfTemplateCallToModule(call_to_project_dir, sourceDirOfTemplate, searchTerm, newPointerLine)

##########################################################################################################
### Step Four:  Init and Apply the Project
##########################################################################################################

backendProjectConfig = depfunc.getProjectBackendConfig(myYamlInputFile, awsCredFile)
initBackendProjectCommand = initCommand + backendProjectConfig
print("initBackendProjectCommand is: ", initBackendProjectCommand)
projectVars = depfunc.getProjectInputs(myYamlInputFile, awsCredFile, projectSecretsFile, depfunc.subscription_id, depfunc.tenant_id )
print("projectVars is: ", projectVars)
applyProjectCommand = 'terraform apply -auto-approve ' + projectVars

depfunc.runTerraformCommand(initBackendProjectCommand, call_to_project_dir)
#Uncomment the following when you want to create
depfunc.runTerraformCommand(applyProjectCommand, call_to_project_dir)


##########################################################################################################
### Step Five:  Get list of source repositories, then instantiate repos and builds for each source repo
##########################################################################################################
sourceReposList = depfunc.getListOfSourceRepos(myYamlInputFile)  
print("sourceReposList is: ", sourceReposList)  
#Toggle the crudOperation values to either apply or destroy.  Note to destroy any repo-builds before destroying the parent project.  
crudOperation = "apply"
#crudOperation = "destroy"
depfunc.manageRepoBuilds(crudOperation, sourceReposList, project_calls_root, myYamlInputFile, awsCredFile, initCommand, project_name)

#Comment out the following when you do not want to delete.
#destroyProjectCommand = 'terraform destroy -auto-approve ' + projectVars
#depfunc.runTerraformCommand(destroyProjectCommand, call_to_project_dir)


##Destroy stuff.  Keeping the following line for now to remind us to later go throu and make sure every item is 
##destroyed after use so that everything must always be recreated by automation.    
# os.remove(prbSecretsFile)  
  

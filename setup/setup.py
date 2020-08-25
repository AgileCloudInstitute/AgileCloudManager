import fileinput
import sys
import subprocess
import re

import pip
failed = pip.main(["install", 'requests'])
print("status of requests install: ", failed)
failed = pip.main(["install", 'pyyaml'])
print("status of pyyaml install: ", failed)

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

# #Declare the directory and file name variables
fileEnterUserInputHereOnly = "/home/aci-user/staging/launchpadConfig.yaml"  
pathToVarFiles='/home/aci-user/vars/agile-cloud-manager/'
fileAzEnvVars = pathToVarFiles+'set-local-az-client-environment-vars.sh'  
  
def runShellCommand(commandToRun, workingDir ):
    print("Inside runShellCommand(..., ...) function. ")
    print("commandToRun is: " +commandToRun)
    print("workingDir is: " +workingDir)

    proc = subprocess.Popen( commandToRun,cwd=workingDir,stdout=subprocess.PIPE, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        print(decodedline)
      else:
        break
  
def validateVariableValues():
    print("Need to add some validation logic here.")  

def updateVarFileAzureProvider(fileName):
    print("inside deploymentFunctions.py script and updateVarFileAzureProvider(...,...,...) function.")
    print("fileName is: ", fileName)
    for line in fileinput.input(fileName, inplace=True):
        if "subscriptionId" in line:
            line = "subscriptionId=\""+subscriptionId+"\""
        if "tenantId" in line:
            line = "tenantId=\""+tenantId+"\""
        if "clientId" in line:
            line = "clientId=\""+clientId+"\""
        if "clientSecret" in line:
            line = "clientSecret=\""+clientSecret+"\""
        print('{}'.format(line))

def updateVarFileAzureDevOpsProvider(fileName):
    print("inside deploymentFunctions.py script and updateVarFileAzureDevOpsProvider(...,...,...) function.")
    print("fileName is: ", fileName)
    for line in fileinput.input(fileName, inplace=True):
        if "azdoOrgPAT" in line:
            line = "azdoOrgPAT=\""+azdoOrgPAT+"\""
        if "azdoOrgServiceURL" in line:
            line = "azdoOrgServiceURL=\""+azdoOrgServiceURL+"\""
        print('{}'.format(line))

def updateVarFileAzurePipesFoundation(fileName):
    print("inside deploymentFunctions.py script and updateVarFileAzurePipesFoundation(...,...,...) function.")
    print("fileName is: ", fileName)
    for line in fileinput.input(fileName, inplace=True):
        if "pipeAzureRegion" in line:
            line = "pipeAzureRegion=\""+pipeAzureRegion+"\""
        print('{}'.format(line))

def updateVarFileAzurePipesAgents(fileName):
    print("inside deploymentFunctions.py script and updateVarFileAzurePipesAgents(...,...,...) function.")
    print("fileName is: ", fileName)
    for line in fileinput.input(fileName, inplace=True):
        if "adminUser" in line:
            line = "adminUser=\""+adminUser+"\""
        if "adminPwd" in line:
            line = "adminPwd=\""+adminPwd+"\""
        if "pathToCloudInitScript" in line:
            line = "pathToCloudInitScript=\""+pathToCloudInitScript+"\""
        print('{}'.format(line))
  
def updateVarFileAzureDevOpsProjectRepoBuild(fileName):
    print("inside deploymentFunctions.py script and updateVarFileAzureDevOpsProjectRepoBuild(...,...,...) function.")
    print("fileName is: ", fileName)
    repoName='check-setup-py-for-error'
    buildName='check-setup-py-for-error'
    for line in fileinput.input(fileName, inplace=True):
        if "subscriptionName" in line:
            line = "subscriptionName=\""+subscriptionName+"\""
        if "clientName" in line:
            line = "clientName=\""+clientName+"\""
        if "serviceConnectionName" in line:
            line = "serviceConnectionName=\""+serviceConnectionName+"\""
        if "storageAccountNameTerraformBackend" in line:
            line = "storageAccountNameTerraformBackend=\""+storageAccountNameTerraformBackend+"\""
        if "storageContainerNameTerraformBackend" in line:
            line = "storageContainerNameTerraformBackend=\""+storageContainerNameTerraformBackend+"\""
        if "awsPublicAccessKey" in line:
            line = "awsPublicAccessKey=\""+awsPublicAccessKey+"\""
        if "awsSecretAccessKey" in line:
            line = "awsSecretAccessKey=\""+awsSecretAccessKey+"\""
        if "sourceRepo" in line:
            line = "sourceRepo=\""+sourceRepo+"\""
        if "repoName" in line:
            fragment=sourceRepo[sourceRepo.rfind('/')+1:]
            repoName=fragment.split('.')[0]
            line = "repoName=\""+repoName+"\""
        if "buildName" in line:
            fragment=sourceRepo[sourceRepo.rfind('/')+1:]
            buildName=fragment.split('.')[0]
            line = "buildName=\""+buildName+"\""
        if "projectName" in line:
            fragment=sourceRepo[sourceRepo.rfind('/')+1:]
            repoName=fragment.split('.')[0]
            line = "projectName=\""+repoName+"-project"+"\""
        print('{}'.format(line))

def updateVarFileAzurePipesAgentsStartUpScript(fileName):
    print("inside deploymentFunctions.py script and updateVarFileAzurePipesAgentStartupScript(...,...,...) function.")
    print("fileName is: ", fileName)
    for line in fileinput.input(fileName, inplace=True):
        trailingCharacters=len(line)-line.find('=')
        if "export AZ_PASS=" in line:
          if "echo" not in line:
            if trailingCharacters < 3:
              line = line.replace("export AZ_PASS=","export AZ_PASS="+clientSecret)
          if "echo" in line:
            if trailingCharacters < 25:
              line = line.replace("export AZ_PASS=","export AZ_PASS="+clientSecret)
        if "export AZ_CLIENT=" in line:
          if "echo" not in line:
            if trailingCharacters < 3:
              line = line.replace("export AZ_CLIENT=","export AZ_CLIENT="+clientId)
          if "echo" in line:
            if trailingCharacters < 25:
              line = line.replace("export AZ_CLIENT=","export AZ_CLIENT="+clientId)
        if "export AZ_TENANT=" in line:
          if "echo" not in line:
            if trailingCharacters < 3:
              line = line.replace("export AZ_TENANT=","export AZ_TENANT="+tenantId)
          if "echo" in line:
            if trailingCharacters < 25:
              line = line.replace("export AZ_TENANT=","export AZ_TENANT="+tenantId)
        if "export AZ_PAT=" in line:
          if "echo" not in line:
            if trailingCharacters < 3:
              line = line.replace("export AZ_PAT=","export AZ_PAT="+azdoOrgPAT)
          if "echo" in line:
            if trailingCharacters < 25:
              line = line.replace("export AZ_PAT=","export AZ_PAT="+azdoOrgPAT)
        if "export AZ_SERVER=" in line:
          if "echo" not in line:
            if trailingCharacters < 3:
              line = line.replace("export AZ_SERVER=","export AZ_SERVER="+azdoOrgServiceURL)
          if "echo" in line:
            if trailingCharacters < 25:
              line = line.replace("export AZ_SERVER=","export AZ_SERVER="+azdoOrgServiceURL)

        if "export AZURE_DEVOPS_EXT_PAT=" in line:
          if "echo" not in line:
            if trailingCharacters < 3:
              line = line.replace("export AZURE_DEVOPS_EXT_PAT=","export AZURE_DEVOPS_EXT_PAT="+azdoOrgPAT)
          if "echo" in line:
            if trailingCharacters < 25:
              line = line.replace("export AZURE_DEVOPS_EXT_PAT=","export AZURE_DEVOPS_EXT_PAT="+azdoOrgPAT)
        print('{}'.format(line))

#Now call the functions
#First do some provisioning
chmodCommand = "chmod +x provisioning.sh"
scriptsDir = "/home/aci-user/cloned-repos/agile-cloud-manager/setup/" 
setupCommand = "sudo ./provisioning.sh"
runShellCommand(chmodCommand, scriptsDir)
runShellCommand(setupCommand, scriptsDir)

###################################################################################################################################
###################################################################################################################################
### Now add the new stuff
sys.path.insert(0, '/home/aci-user/cloned-repos/agile-cloud-manager/pipeline-tasks/')
import deploymentFunctions as depfunc

depfunc.setEnvironmentVars(fileEnterUserInputHereOnly, fileAzEnvVars)

### Finished adding the new stuff
###################################################################################################################################
###################################################################################################################################

#Third set local environment variables
varsDir = "/home/aci-user/vars/agile-cloud-manager/"
newChmodCommand = "chmod +x /home/aci-user/vars/agile-cloud-manager/set-local-az-client-environment-vars.sh"  
setVarsCommand = "sudo /home/aci-user/vars/agile-cloud-manager/set-local-az-client-environment-vars.sh"  
runShellCommand(newChmodCommand, varsDir )
runShellCommand(setVarsCommand, varsDir )

# #Fourth chown the file to aci-user to avoid risk of being owned by root
cmdChownVarFileAzurePipesAgentsStartUpScript = "sudo chown aci-user:aci-user " + fileAzEnvVars

runShellCommand(cmdChownVarFileAzurePipesAgentsStartUpScript, varsDir )

#Consider further locking down the yaml config files

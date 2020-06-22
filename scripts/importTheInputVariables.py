import fileinput
import sys

#Declare all the input variables
subscriptionId=''
tenantId=''
clientId=''
clientSecret=''
pipeAzureRegion=''
storageAccountNameTerraformBackend=''
storageContainerNameTerraformBackend=''
awsPublicAccessKey=''
awsSecretAccessKey=''
adminUser=''
adminPwd=''
pathToCloudInitScript=''
azdoOrgPAT=''
azdoOrgServiceURL=''

#Declare the directory and file name variables
pathToVarFiles='/home/aci-user/vars/agile-cloud-manager/'
fileEnterUserInputHereOnly = pathToVarFiles+'enter-user-input-here-only.txt'
fileInputsAgentVmsAuto = pathToVarFiles+'inputs-agent-vms-auto.tfvars'
fileInputsAgentVmsManual = pathToVarFiles+'inputs-agent-vms-manual.tfvars'
fileInputsAzdoProvider = pathToVarFiles+'inputs-azdo-provider.tfvars'
fileInputsAzurermProvider = pathToVarFiles+'inputs-azurerm-provider.tfvars'
fileInputsFoundationDemo = pathToVarFiles+'inputs-foundation-demo.tfvars'
fileInputsProjectRepoBuildAuto = pathToVarFiles+'inputs-project-repo-build-auto.tfvars'
fileInputsProjectRepoBuildManual = pathToVarFiles+'inputs-project-repo-build-manual.tfvars'
fileStartupScript = pathToVarFiles+'startup-script.sh'

def getTheValue(lineToParse):
    print("lineToParse is: ", lineToParse)
    lineToParse = lineToParse[lineToParse.find('=')+1:]
    if "\"" in lineToParse:
      if lineToParse.count('\"') >= 2:
        lineToParse = lineToParse[lineToParse.find("\"")+1:]
        lineToParse = lineToParse[:lineToParse.rfind("\"")]
      if lineToParse.count('\"') == 1:
        print("There is only a one quotation mark. ")
    return lineToParse

def loadDataFromFile(fileName):
    print("inside deploymentFunctions.py script and loadDataFromFile(...,...,...) function.")
    print("fileName is: ", fileName)

    with open(fileName) as file_in:
      for line in file_in:
        if 'subscriptionId' in line:
            global subscriptionId
            subscriptionId = getTheValue(line)
            print("subscriptionId is: ", subscriptionId)
        if 'tenantId' in line:
            global tenantId
            tenantId = getTheValue(line)
            print("tenantId is: ", tenantId)
        if 'clientId' in line:
            global clientId
            clientId = getTheValue(line)
            print("clientId is: ", clientId)
        if 'clientSecret' in line:
            global clientSecret
            clientSecret = getTheValue(line)
            print("clientSecret is: ", clientSecret)
        if 'pipeAzureRegion' in line:
            global pipeAzureRegion
            pipeAzureRegion = getTheValue(line)
            print("pipeAzureRegion is: ", pipeAzureRegion)
        if 'storageAccountNameTerraformBackend' in line:
            global storageAccountNameTerraformBackend
            storageAccountNameTerraformBackend = getTheValue(line)
            print("storageAccountNameTerraformBackend is: ", storageAccountNameTerraformBackend)
        if 'storageContainerNameTerraformBackend' in line:
            global storageContainerNameTerraformBackend
            storageContainerNameTerraformBackend = getTheValue(line)
            print("storageContainerNameTerraformBackend is: ", storageContainerNameTerraformBackend)
        if 'awsPublicAccessKey' in line:
            global awsPublicAccessKey
            awsPublicAccessKey = getTheValue(line)
            print("awsPublicAccessKey is: ", awsPublicAccessKey)
        if 'awsSecretAccessKey' in line:
            global awsSecretAccessKey
            awsSecretAccessKey = getTheValue(line)
            print("awsSecretAccessKey is: ", awsSecretAccessKey)
        if 'adminUser' in line:
            global adminUser
            adminUser = getTheValue(line)
            print("adminUser is: ", adminUser)
        if 'adminPwd' in line:
            global adminPwd
            adminPwd = getTheValue(line)
            print("adminPwd is: ", adminPwd)
        if 'pathToCloudInitScript' in line:
            global pathToCloudInitScript
            pathToCloudInitScript = getTheValue(line)
            print("pathToCloudInitScript is: ", pathToCloudInitScript)
        if 'azdoOrgPAT' in line:
            global azdoOrgPAT
            azdoOrgPAT = getTheValue(line)
            print("azdoOrgPAT is: ", azdoOrgPAT)
        if 'azdoOrgServiceURL' in line:
            global azdoOrgServiceURL
            azdoOrgServiceURL = getTheValue(line)
            print("azdoOrgServiceURL is: ", azdoOrgServiceURL)

def validateVariableValues():
    print("Need to add some validation logic here.")  

def updateVarFileAzureProvider(fileName):
    print("inside deploymentFunctions.py script and updateVarFileAzureProvider(...,...,...) function.")
    print("fileName is: ", fileName)
    with open(fileName, 'r+') as file_in:
      for line in file_in:
        print("line at start is: ", line)
        if "subscriptionId" in line:
            line = "subscriptionId=\""+subscriptionId+"\""
            print("line in middle is: ", line)
        print("line at end is: ", line)
        if "tenantId" in line:
            line = "tenantId=\""+tenantId+"\""
            print("line in middle is: ", line)
        print("line at end is: ", line)
        if "clientId" in line:
            line = "clientId=\""+clientId+"\""
            print("line in middle is: ", line)
        print("line at end is: ", line)
        if "clientSecret" in line:
            line = "clientSecret=\""+clientSecret+"\""
            print("line in middle is: ", line)
        print("line at end is: ", line)

def updateVarFileAzureDevOpsProvider(fileName):
    print("inside deploymentFunctions.py script and updateVarFileAzureDevOpsProvider(...,...,...) function.")
    print("fileName is: ", fileName)
    with open(fileName, 'r+') as file_in:
      for line in file_in:
        print("line at start is: ", line)
        if "azdoOrgPAT" in line:
            line = "azdoOrgPAT=\""+azdoOrgPAT+"\""
            print("line in middle is: ", line)
        print("line at end is: ", line)
        if "azdoOrgServiceURL" in line:
            line = "azdoOrgServiceURL=\""+azdoOrgServiceURL+"\""
            print("line in middle is: ", line)
        print("line at end is: ", line)

def updateVarFileAzurePipesFoundation(fileName):
    print("inside deploymentFunctions.py script and updateVarFileAzurePipesFoundation(...,...,...) function.")
    print("fileName is: ", fileName)
    with open(fileName, 'r+') as file_in:
      for line in file_in:
        print("line at start is: ", line)
        if "storageAccountNameTerraformBackend" in line:
            line = "storageAccountNameTerraformBackend=\""+storageAccountNameTerraformBackend+"\""
            print("line in middle is: ", line)
        print("line at end is: ", line)
        if "pipeAzureRegion" in line:
            line = "pipeAzureRegion=\""+pipeAzureRegion+"\""
            print("line in middle is: ", line)
        print("line at end is: ", line)

def updateVarFileAzurePipesAgents():
    print("Need to add something here to update this var file. ")

def updateVarFileAzureDevOpsProjectRepoBuild():
    print("Need to add something here to update this var file. ")

def updateVarFileAzurePipesAgentsStartUpScript():
    print("Need to add something here to update this var file. ")

#Now call the functions
loadDataFromFile(fileEnterUserInputHereOnly)

updateVarFileAzureProvider(fileInputsAzurermProvider)

updateVarFileAzureDevOpsProvider(fileInputsAzdoProvider)

updateVarFileAzurePipesFoundation(fileInputsFoundationDemo)

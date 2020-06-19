
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
#= 'enter-user-input-here-only.txt'
#= 'inputs-agent-vms-auto.tfvars'
#= 'inputs-agent-vms-manual.tfvars'
#= 'inputs-azdo-provider.tfvars'
#= 'inputs-azurerm-provider.tfvars'
#= 'inputs-foundation-demo.tfvars'
#= 'inputs-project-repo-build-auto.tfvars'
#= 'inputs-project-repo-build-manual.tfvars'
#= 'startup-script.sh'


def getTheValue(lineToParse):
    print("lineToParse is: ", lineToParse)
    lineToParse = lineToParse[lineToParse.lindex('=')+1:]
    print("everything to the right of first quote is: ", lineToParse)
    lineToParse = lineToParse[lineToParse.rindex('=')+1:]
    print("everything to the left of last quote is: ", lineToParse)
    return lineToParse

def loadDataFromFile(fileName):
    print("inside deploymentFunctions.py script and loadDataFromFile(...,...,...) function.")
    print("fileName is: ", fileName)

    for line in fileinput.input(fileName, inplace=1):
        if 'subscriptionId' in line:
            subscriptionId = getTheValue(line)
            print("subscriptionId is: ", subscriptionId)
        if 'tenantId' in line:
            tenantId = getTheValue(line)
            print("tenantId is: ", tenantId)
        if 'clientId' in line:
            clientId = getTheValue(line)
            print("clientId is: ", clientId)
        if 'clientSecret' in line:
            clientSecret = getTheValue(line)
            print("clientSecret is: ", clientSecret)
        if 'pipeAzureRegion' in line:
            pipeAzureRegion = getTheValue(line)
            print("pipeAzureRegion is: ", pipeAzureRegion)
        if 'storageAccountNameTerraformBackend' in line:
            storageAccountNameTerraformBackend = getTheValue(line)
            print("storageAccountNameTerraformBackend is: ", storageAccountNameTerraformBackend)
        if 'storageContainerNameTerraformBackend' in line:
            storageContainerNameTerraformBackend = getTheValue(line)
            print("storageContainerNameTerraformBackend is: ", storageContainerNameTerraformBackend)
        if 'awsPublicAccessKey' in line:
            awsPublicAccessKey = getTheValue(line)
            print("awsPublicAccessKey is: ", awsPublicAccessKey)
        if 'awsSecretAccessKey' in line:
            awsSecretAccessKey = getTheValue(line)
            print("awsSecretAccessKey is: ", awsSecretAccessKey)
        if 'adminUser' in line:
            adminUser = getTheValue(line)
            print("adminUser is: ", adminUser)
        if 'adminPwd' in line:
            adminPwd = getTheValue(line)
            print("adminPwd is: ", adminPwd)
        if 'pathToCloudInitScript' in line:
            pathToCloudInitScript = getTheValue(line)
            print("pathToCloudInitScript is: ", pathToCloudInitScript)
        if 'azdoOrgPAT' in line:
            azdoOrgPAT = getTheValue(line)
            print("azdoOrgPAT is: ", azdoOrgPAT)
        if 'azdoOrgServiceURL' in line:
            azdoOrgServiceURL = getTheValue(line)
            print("azdoOrgServiceURL is: ", azdoOrgServiceURL)

def validateVariableValues():
    print("Need to add some validation logic here.")  

def updateVarFileAzureProvider():
    print("Need to add something here to update this var file. ")

def updateVarFileAzureDevOpsProvider():
    print("Need to add something here to update this var file. ")

def updateVarFileAzurePipesFoundation():
    print("Need to add something here to update this var file. ")

def updateVarFileAzurePipesAgents():
    print("Need to add something here to update this var file. ")

def updateVarFileAzureDevOpsProjectRepoBuild():
    print("Need to add something here to update this var file. ")

def updateVarFileAzurePipesAgentsStartUpScript():
    print("Need to add something here to update this var file. ")


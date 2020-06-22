
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

def updateVarFileAzureProvider(fileName):
    print("inside deploymentFunctions.py script and updateVarFileAzureProvider(...,...,...) function.")
    print("fileName is: ", fileName)

    with open(fileName) as file_in:
      for line in file_in:
        print("line is: ", line)
    
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

#Now call the functions
loadDataFromFile(fileEnterUserInputHereOnly)

updateVarFileAzureProvider(fileInputsAzdoProvider)

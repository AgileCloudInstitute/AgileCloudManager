import fileinput
import sys

#Declare all the input variables
subscriptionName=''
subscriptionId=''
tenantId=''
clientName=''
clientId=''
clientSecret=''
serviceConnectionName=''
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
sourceRepo=''

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
fileAzEnvVars = pathToVarFiles+'set-local-az-client-environment-vars.sh'

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
        if 'subscriptionName' in line:
            global subscriptionName
            subscriptionName = getTheValue(line)
            print("subscriptionName is: ", subscriptionName)
        if 'subscriptionId' in line:
            global subscriptionId
            subscriptionId = getTheValue(line)
            print("subscriptionId is: ", subscriptionId)
        if 'tenantId' in line:
            global tenantId
            tenantId = getTheValue(line)
            print("tenantId is: ", tenantId)
        if 'clientName' in line:
            global clientName
            clientName = getTheValue(line)
            print("clientName is: ", clientName)
        if 'clientId' in line:
            global clientId
            clientId = getTheValue(line)
            print("clientId is: ", clientId)
        if 'clientSecret' in line:
            global clientSecret
            clientSecret = getTheValue(line)
            print("clientSecret is: ", clientSecret)
        if 'serviceConnectionName' in line:
            global serviceConnectionName
            serviceConnectionName = getTheValue(line)
            print("serviceConnectionName is: ", serviceConnectionName)
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
        if 'sourceRepo' in line:
            global sourceRepo
            sourceRepo = getTheValue(line)
            print("sourceRepo is: ", sourceRepo)

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
        if "storageAccountNameTerraformBackend" in line:
            line = "storageAccountNameTerraformBackend=\""+storageAccountNameTerraformBackend+"\""
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
loadDataFromFile(fileEnterUserInputHereOnly)

updateVarFileAzureProvider(fileInputsAzurermProvider)

updateVarFileAzureDevOpsProvider(fileInputsAzdoProvider)

updateVarFileAzurePipesFoundation(fileInputsFoundationDemo)

updateVarFileAzurePipesAgents(fileInputsAgentVmsManual)

updateVarFileAzureDevOpsProjectRepoBuild(fileInputsProjectRepoBuildManual)
#This next function call is for the cloud-init startup script that will run on the Azure Pipelines agent that will be created.
updateVarFileAzurePipesAgentsStartUpScript(fileStartupScript)
#This next function call will set vars on the local machine to use with the az client
updateVarFileAzurePipesAgentsStartUpScript(fileAzEnvVars)

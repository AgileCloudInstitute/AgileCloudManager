import subprocess
import re
import fileinput
import sys
import os 
import shutil
import base64
import json 

#Adding these next 5 lines to avert an error that occurs when this is imported into setup.py.  There should be a better way of handling the pip installs than adding the double check as follows:
import pip
failed = pip.main(["install", 'requests'])
print("status of requests install: ", failed)
failed = pip.main(["install", 'pyyaml'])
print("status of pyyaml install: ", failed)

import requests
import yaml

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
storName = ''
nicName = ''
resourceGroupName = ''
resourceGroupLocation = ''
storageAccountNameTerraformBackend = ''
pipeKeyVaultName = ''
pipeSubnetId = '' 
azuredevops_build_definition_id = ''
azuredevops_git_repository_id = ''
azuredevops_git_repository_name = ''
azuredevops_project_name = ''
azuredevops_project_id = ''
azuredevops_organization_service_url = ''
azuredevops_key_vault_name = ''  
azuredevops_subscription_name = ''    
azuredevops_subscription_id = ''
azuredevops_client_name = ''    
azuredevops_service_connection_name = ''    
azuredevops_service_connection_id = ''  
subscription_name = '' 
subscription_id = ''  
tenant_id = '' 
  
azuredevops_organization_name = ''

def updateOrganizationName():
    global azuredevops_organization_name
    if len(azuredevops_organization_service_url) >2:  
        azuredevops_organization_name_prep = azuredevops_organization_service_url.split("azure.com/",1)[1]
        azuredevops_organization_name = azuredevops_organization_name_prep.replace("/","")
    print("azuredevops_organization_name in deploymentFunctions.py is: ", azuredevops_organization_name)
    #return azuredevops_organization_name

def runTerraformCommand(commandToRun, workingDir ):
    print("Inside deploymentFunctions.py script and runTerraformCommand(..., ...) function. ")
    print("commandToRun is: " +commandToRun)
    print("workingDir is: " +workingDir)

    proc = subprocess.Popen( commandToRun,cwd=workingDir,stdout=subprocess.PIPE, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        print(decodedline)
        if "Outputs:" in decodedline:  
          print("Reached \"Outputs\" section: ")
          print("decodedline is: " +decodedline)
        if "storageAccountDiagName" in decodedline:
          print("Found storageAccountDiagName!")
          global storName
          storName=decodedline[25:]
          print("storName in deploymentFunctions.py is: ", storName)
        if "nicName" in decodedline:
          print("Found nicName!")
          global nicName
          nicName=decodedline[10:]
          print("nicName in deploymentFunctions.py is: ", nicName)
        if "pipes_resource_group_name" in decodedline:
          print("Found resourceGroupName!")
          global resourceGroupName
          resourceGroupName=decodedline[28:]
          print("resourceGroupName in deploymentFunctions.py is: ", resourceGroupName)
        if "pipes_resource_group_region" in decodedline:
          print("Found resourceGroupLocation!")
          global resourceGroupLocation
          resourceGroupLocation=decodedline[30:]
          print("resourceGroupLocation in deploymentFunctions.py is: ", resourceGroupLocation)
        if "pipes_storage_account_name" in decodedline:
          print("Found storageAccountNameTerraformBackend!")
          global storageAccountNameTerraformBackend
          storageAccountNameTerraformBackend=decodedline[29:]
          print("storageAccountNameTerraformBackend in deploymentFunctions.py is: ", storageAccountNameTerraformBackend)
        if "pipeKeyVaultName" in decodedline:
          print("Found pipeKeyVaultName!")
          global pipeKeyVaultName
          pipeKeyVaultName=decodedline[19:]
          print("pipeKeyVaultName in deploymentFunctions.py is: ", pipeKeyVaultName)
        if "pipes_subnet_id" in decodedline:
          print("Found pipes_subnet_id!")
          global pipeSubnetId
          pipeSubnetId=decodedline[18:]
          print("pipeSubnetId in deploymentFunctions.py is: ", pipeSubnetId)
        if "azuredevops_build_definition_id" in decodedline:
          print("Found azuredevops_build_definition_id!")
          global azuredevops_build_definition_id
          azuredevops_build_definition_id=decodedline[34:]
          print("azuredevops_build_definition_id in deploymentFunctions.py is: ", azuredevops_build_definition_id)
        if "azuredevops_git_repository_id" in decodedline:
          print("Found azuredevops_git_repository_id!")
          global azuredevops_git_repository_id
          azuredevops_git_repository_id=decodedline[32:]
          print("azuredevops_git_repository_id in deploymentFunctions.py is: ", azuredevops_git_repository_id)
        if "azuredevops_git_repository_name" in decodedline:
          print("Found azuredevops_git_repository_name!")
          global azuredevops_git_repository_name
          azuredevops_git_repository_name=decodedline[34:]
          print("azuredevops_git_repository_name in deploymentFunctions.py is: ", azuredevops_git_repository_name)
        if "azuredevops_project_id" in decodedline:
          print("Found azuredevops_project_id!")
          global azuredevops_project_id
          azuredevops_project_id=decodedline[25:]
          print("azuredevops_project_id in deploymentFunctions.py is: ", azuredevops_project_id)
        if "azuredevops_project_name" in decodedline:
          print("Found azuredevops_project_name!")
          global azuredevops_project_name
          azuredevops_project_name=decodedline[27:]
          print("azuredevops_project_name in deploymentFunctions.py is: ", azuredevops_project_name)
        if "azuredevops_organization_service_url" in decodedline:
          print("Found azuredevops_organization_service_url!")
          global azuredevops_organization_service_url
          azuredevops_organization_service_url=decodedline[39:]
          print("azuredevops_organization_service_url in deploymentFunctions.py is: ", azuredevops_organization_service_url)
          updateOrganizationName()
        if "azuredevops_key_vault_name" in decodedline:
          print("Found azuredevops_key_vault_name!")
          global azuredevops_key_vault_name
          azuredevops_key_vault_name=decodedline[29:]
          print("azuredevops_key_vault_name in deploymentFunctions.py is: ", azuredevops_key_vault_name)
        if "azuredevops_subscription_name" in decodedline:
          print("Found azuredevops_subscription_name!")
          global azuredevops_subscription_name
          azuredevops_subscription_name=decodedline[32:]
          print("azuredevops_subscription_name in deploymentFunctions.py is: ", azuredevops_subscription_name)
        if "azuredevops_subscription_id" in decodedline:
          print("Found azuredevops_subscription_id!")
          global azuredevops_subscription_id
          azuredevops_subscription_id=decodedline[30:]
          print("azuredevops_subscription_id in deploymentFunctions.py is: ", azuredevops_subscription_id)
        if "azuredevops_client_name" in decodedline:
          print("Found azuredevops_client_name!")
          global azuredevops_client_name
          azuredevops_client_name=decodedline[26:]
          print("azuredevops_client_name in deploymentFunctions.py is: ", azuredevops_client_name)
        if "azuredevops_service_connection_name" in decodedline:
          print("Found azuredevops_service_connection_name!")
          global azuredevops_service_connection_name
          azuredevops_service_connection_name=decodedline[38:]
          print("azuredevops_service_connection_name in deploymentFunctions.py is: ", azuredevops_service_connection_name)
        if "azuredevops_service_connection_id" in decodedline:
          print("Found azuredevops_service_connection_id!")
          global azuredevops_service_connection_id
          azuredevops_service_connection_id=decodedline[36:]
          print("azuredevops_service_connection_id in deploymentFunctions.py is: ", azuredevops_service_connection_id)
        if "subscription_name" in decodedline:
          print("Found subscription_name!")
          global subscription_name
          subscription_name=decodedline[20:]
          print("subscription_name in deploymentFunctions.py is: ", subscription_name)
        if "subscription_id" in decodedline:
          print("Found subscription_id!")
          global subscription_id
          subscription_id=decodedline[18:]
          print("subscription_id in deploymentFunctions.py is: ", subscription_id)
        if "tenant_id" in decodedline:
          print("Found tenant_id!")
          global tenant_id
          tenant_id=decodedline[12:]
          print("tenant_id in deploymentFunctions.py is: ", tenant_id)
      else:
        break

def changeLineInFile(fileName, searchTerm, valueToChange):
    print("inside deploymentFunctions.py script and changeLineInFile(...,...,...) function.")
    print("fileName is: ", fileName)
    print("searchTerm is: ", searchTerm)
    print("valueToChange is: ", valueToChange)

    for line in fileinput.input(fileName, inplace=1):
        if searchTerm in line:
            line = searchTerm+"=\""+valueToChange+"\"\n"
        sys.stdout.write(line)

def getPoolQueueIdApiRequest(orgName, projId, qName):  
    print("inside deploymentFunctions.py script and getPoolQueueIdApiRequest(...,...,...) function.")
    #Assemble headers  
    personal_access_token = ":"+os.environ["AZ_PAT"]  
    headers = {}  
    headers['Content-type'] = "application/json"  
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))  
    #Assemble the endpoint URL
    #Get the Agent Pool Queues whose name matches the search criteria.  This should only be one queue because name should be a unique key.  
    api_version_p = "5.1-preview.1"
    #GET https://dev.azure.com/{organization}/{project}/_apis/distributedtask/queues?queueName={queueName}&actionFilter={actionFilter}&api-version=5.1-preview.1
    queues_url = ("https://dev.azure.com/%s/%s/_apis/distributedtask/queues?queueName=%s&api-version=%s" % (orgName, projId, qName, api_version_p))
    print("-------------------------------------------------------------")
    #Make the request    
    r = requests.get(queues_url, headers=headers)
    print("r.status_code is: ", r.status_code)
    #Add some better error handling here to handle various response codes.  We are assuming that a 200 response is received in order to continue here.  
    myQueuesData = r.json()
    print("myQueuesData is: ", myQueuesData)
    #Using index 0 here because queue_name should be a unique key that brings only one result in this response
    poolQueueId = myQueuesData['value'][0]['id']
    return poolQueueId

def createReleaseDefinitionApiRequest(templateFile, azdo_organization_name, azdo_project_id, azdo_project_name, azdo_build_definition_id, 
                                      azdo_git_repository_name, azdo_organization_service_url, queue_id, artifact_alias, azdo_service_connection_id, 
                                      scriptInputVars, releaseDefName, environName ):
    personal_access_token = ":"+os.environ["AZ_PAT"]
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
    api_version = "5.1"
    url = ("https://vsrm.dev.azure.com/%s/%s/_apis/release/definitions?api-version=%s" % (azdo_organization_name, azdo_project_id, api_version))
    with open(templateFile, 'r') as json_file:
      print("json_file is: ", json_file)
      data = json.load(json_file)
      print("---------------------------------------------------------")
      print("name is: ", data['name'])
      data['name'] = releaseDefName
      print("name is now: ", data['name'])
      print("variables is: ", data['variables'])
      data['variables'] = {"aws-region":{"value":"us-west-2"}}
      print("variables is now: ", data['variables'])

      print("environment name is: ", data['environments'][0]['name'])
      data['environments'][0]['name'] = environName 
      print("environment name is now: ", data['environments'][0]['name'])
      print("alias is: ", data['environments'][0]['deployPhases'][0]['deploymentInput']['artifactsDownloadInput']['downloadInputs'][0]['alias'])
      data['environments'][0]['deployPhases'][0]['deploymentInput']['artifactsDownloadInput']['downloadInputs'][0]['alias'] = artifact_alias
      print("alias is now: ", data['environments'][0]['deployPhases'][0]['deploymentInput']['artifactsDownloadInput']['downloadInputs'][0]['alias'])
      print("queueId is: ", data['environments'][0]['deployPhases'][0]['deploymentInput']['queueId'])
      data['environments'][0]['deployPhases'][0]['deploymentInput']['queueId'] = queue_id
      print("queueId is now: ", data['environments'][0]['deployPhases'][0]['deploymentInput']['queueId'])
      print("---------------------------------------------------------")
      print("[\'artifacts\'][\'sourceId\'] is: ", data['artifacts'][0]['sourceId'])
      print("[\'artifacts\'][\'artifactSourceDefinitionUrl\'][\'id\'] is: ", data['artifacts'][0]['artifactSourceDefinitionUrl']['id'])
      print("[\'artifacts\'][\'alias\'] is: ", data['artifacts'][0]['alias'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['definition']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['definition']['name'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['project']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['project']['name'])
      print("---------------------------------------------------------")
      data['artifacts'][0]['sourceId'] = azdo_project_id + ":1"
      data['artifacts'][0]['artifactSourceDefinitionUrl']['id'] = azdo_organization_service_url + azdo_project_name + "/_build?definitionId=" + str(azdo_build_definition_id)
      data['artifacts'][0]['alias'] = artifact_alias
      data['artifacts'][0]['definitionReference']['definition']['id'] = azdo_build_definition_id
      data['artifacts'][0]['definitionReference']['definition']['name'] = azdo_git_repository_name
      data['artifacts'][0]['definitionReference']['project']['id'] = azdo_project_id
      data['artifacts'][0]['definitionReference']['project']['name'] = azdo_project_name
      print("---------------------------------------------------------")
      print("[\'artifacts\'][\'sourceId\'] is: ", data['artifacts'][0]['sourceId'])
      print("[\'artifacts\'][\'artifactSourceDefinitionUrl\'][\'id\'] is: ", data['artifacts'][0]['artifactSourceDefinitionUrl']['id'])
      print("[\'artifacts\'][\'alias\'] is: ", data['artifacts'][0]['alias'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['definition']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['definition']['name'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['project']['id'])
      print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['project']['name'])

      print("-------------------------------------------------------------------")
      myIdx = 0
      for item in data['environments'][0]['deployPhases'][0]['workflowTasks']:
          #print("item is: ", item)
          print("item[taskId] is: ", item['taskId'])
          print("name of task is: ", data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['name'])
          if item['taskId'] == '6392f95f-7e76-4a18-b3c7-7f078d2f7700':
            print("This is a Python script task. ")
            print("About to set the variables to be imported into the script.")
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['name'] = "Python script"
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['scriptPath'] = "$(System.DefaultWorkingDirectory)/_terraform-aws-simple-example/drop/pipeline-scripts/createSimpleExample.py"
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['arguments'] = scriptInputVars            
          if item['taskId'] == '6c731c3c-3c68-459a-a5c9-bde6e6595b5b':
            print("This is a Bash script task. ")
            print("About to set the variables to be imported into the script.")
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['name'] = "Run a Bash Script"
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['filePath'] = "$(System.DefaultWorkingDirectory)/_terraform-aws-simple-example/drop/pipeline-scripts/bashExample.sh"
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['arguments'] = scriptInputVars            
          if item['taskId'] == '1e244d32-2dd4-4165-96fb-b7441ca9331e':
            print("This is a Key Vault script task.  ")
            print("ConnectedServiceName is: ", data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['ConnectedServiceName'])
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['name'] = "Azure Key Vault: testvlt789"
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['ConnectedServiceName'] = azdo_service_connection_id
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['KeyVaultName'] = "testvlt789"
            print("KeyVaultName is: ", data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['KeyVaultName'])
          myIdx += 1
      print("-------------------------------------------------------------------")

      print("---------------------------------------------------------")
      print("url is: ", url)
      print("---------------------------------------------------------")
      print("revised data is: ", data)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    respCode = r.status_code
    print("r.status_code is: ", respCode)
    print("r.json() is: ", r.json())
    return respCode
   
###################################################################################################################################33
#####################################################################################################################################
### Now add the new stuff

def setEnvironmentVars(yamlInputFile, setEnvironmentVarsFile):
  print("inside deploymentFunctions.py script and setEnvironmentVars(...,...,...) function.")
  #First declare the variables
  clientSecret = ''
  clientId = ''
  tenantId = ''
  azdoOrgPAT = ''
  azdoOrgServiceURL = ''
  #Now populate the variables
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("azureMeta", item):
        metaItems = topLevel_dict.get(item)
        for metaItem in metaItems: 
          if re.match("tenantId", metaItem):
            tenantId = metaItems.get(metaItem)
            print("tenantId is: ", tenantId)
      if re.match("azdoConnection", item):  
        connectionItems = topLevel_dict.get(item)  
        for connectionItem in connectionItems:
          if re.match("azdoOrgServiceURL", connectionItem):
            azdoOrgServiceURL = connectionItems.get(connectionItem)
            print("azdoOrgServiceURL is: ", azdoOrgServiceURL)
          if re.match("clientId", connectionItem):
            clientId = connectionItems.get(connectionItem)
            print("clientId is: ", clientId)
          if re.match("clientSecret", connectionItem):
            clientSecret = connectionItems.get(connectionItem)
            print("clientSecret is: ", clientSecret)
          if re.match("azdoOrgPAT", connectionItem):
            azdoOrgPAT = connectionItems.get(connectionItem)
            print("azdoOrgPAT is: ", azdoOrgPAT)
  #Now put the vars into the target file
  print("setEnvironmentVarsFile is: ", setEnvironmentVarsFile)
  for line in fileinput.input(setEnvironmentVarsFile, inplace=True):
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

def getFoundationInputs(yamlInputFile, foundationSecretsFile):  
  varsString = '' 
  clientSecret = '' 
  awsPublicAccessKey = '' 
  awsSecretAccessKey = '' 
  with open(yamlInputFile) as f:  
    topLevel_dict = yaml.safe_load(f)  
    for item in topLevel_dict:  
      print("item is: ", item)  
      if re.match("azureMeta", item):  
        metaItems = topLevel_dict.get(item)  
        for metaItem in metaItems:  
          if re.match("subscriptionId", metaItem):  
            print(metaItem, " is: ", metaItems.get(metaItem))  
            varsString = varsString + " -var=\""+ metaItem + "=" + metaItems.get(metaItem) +"\""   
          if re.match("tenantId", metaItem):  
            print(metaItem, " is: ", metaItems.get(metaItem))
            varsString = varsString + " -var=\""+ metaItem + "=" + metaItems.get(metaItem) +"\""  
          if re.match("pipeAzureRegion", metaItem):
            print(metaItem, " is: ", metaItems.get(metaItem))
            varsString = varsString + " -var=\""+ metaItem + "=" + metaItems.get(metaItem) +"\""  
      if re.match("azdoConnection", item):  
        connectionItems = topLevel_dict.get(item)  
        for connectionItem in connectionItems:
          if re.match("clientId", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
            varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
          if re.match("clientSecret", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
            with open(foundationSecretsFile, "w") as file:
              lineToAdd = connectionItem+"=\""+connectionItems.get(connectionItem) +"\"\n"
              file.write(lineToAdd)
              varsString = varsString + " -var-file=\""+ foundationSecretsFile +"\""

      if re.match("awsConnection", item):  
        awsItems = topLevel_dict.get(item)  
        for awsItem in awsItems:  
          if re.match("awsPublicAccessKey", awsItem):  
            awsPublicAccessKey = awsItems.get(awsItem)  
          if re.match("subscriptionId", awsItem):  
            awsSecretAccessKey = awsItems.get(awsItem)  

  clientSecret
  awsPublicAccessKey
  awsSecretAccessKey

  print("varsString is: ", varsString)
  return varsString

def getAgentsInputs(yamlInputFile, foundationSecretsFile, subscriptionId, tenantId, pipes_resource_group_region, pipes_resource_group_name, nicName, storageAccountDiagName):
  varsString = ''
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      print("item is: ", item)
      if re.match("azdoConnection", item):  
        connectionItems = topLevel_dict.get(item)  
        for connectionItem in connectionItems:
          if re.match("clientId", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
            varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
          if re.match("clientSecret", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
            with open(foundationSecretsFile, "w") as file:
              lineToAdd = connectionItem+"=\""+connectionItems.get(connectionItem) +"\"\n"
              file.write(lineToAdd)
              varsString = varsString + " -var-file=\""+ foundationSecretsFile +"\""
      if re.match("agents", item):  
        agentsItems = topLevel_dict.get(item)  
        for agentsItem in agentsItems:
          if re.match("adminUser", agentsItem):
            print(agentsItem, " is: ", agentsItems.get(agentsItem))
            varsString = varsString + " -var=\""+ agentsItem + "=" + agentsItems.get(agentsItem) +"\""  
          if re.match("adminPwd", agentsItem):
            print(agentsItem, " is: ", agentsItems.get(agentsItem))
            varsString = varsString + " -var=\""+ agentsItem + "=" + agentsItems.get(agentsItem) +"\""  
          if re.match("pathToCloudInitScript", agentsItem):
            print(agentsItem, " is: ", agentsItems.get(agentsItem))
            varsString = varsString + " -var=\""+ agentsItem + "=" + agentsItems.get(agentsItem) +"\""  
  varsString = varsString + " -var=\"subscriptionId=" + subscriptionId +"\""  
  varsString = varsString + " -var=\"tenantId=" + tenantId +"\""  
  varsString = varsString + " -var=\"resourceGroupLocation=" + pipes_resource_group_region +"\""  
  varsString = varsString + " -var=\"resourceGroupName=" + pipes_resource_group_name +"\""  
  varsString = varsString + " -var=\"nicName=" + nicName +"\""  
  varsString = varsString + " -var=\"storageAccountDiagName=" + storageAccountDiagName +"\""  
  print("varsString is: ", varsString)
  return varsString  
  
def getCloudInitLocation(yamlInputFile):  
  pathToCloudInitStartup = ''  
  with open(yamlInputFile) as f:  
    topLevel_dict = yaml.safe_load(f)  
    for item in topLevel_dict:  
      if re.match("agents", item):  
        agentsItems = topLevel_dict.get(item)  
        for agentsItem in agentsItems:  
          if re.match("pathToCloudInitScript", agentsItem):  
            print(agentsItem, " is: ", agentsItems.get(agentsItem))  
            pathToCloudInitStartup = agentsItems.get(agentsItem)  
  print("pathToCloudInitStartup is: ", pathToCloudInitStartup)  
  return pathToCloudInitStartup  
  
def getFoundationBackendConfig(yamlInputFile, awsCredFile):
  varsString = ''
  awsPublicAccessKey = ''
  awsSecretAccessKey = ''
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("awsBackendTF", item):
        awsBackendItems = topLevel_dict.get(item)
        #for projectRepoBuild in projectRepoBuildCollections:
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
            if re.match("moduleKeyFoundation", awsBackendItem):
              print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
              varsString = varsString + " -backend-config \"key=" + awsBackendItems.get(awsBackendItem) +"\""    
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

def getAgentsBackendConfig(yamlInputFile, awsCredFile):
  varsString = ''
  awsPublicAccessKey = ''
  awsSecretAccessKey = ''
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
          if re.match("moduleKeyAgents", awsBackendItem):  
            print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
            varsString = varsString + " -backend-config \"key=" + awsBackendItems.get(awsBackendItem) +"\""  
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

def getProjectRepoBuildBackendConfig(yamlInputFile, awsCredFile):
  varsString = ''
  awsPublicAccessKey = ''
  awsSecretAccessKey = ''
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
          if re.match("moduleKeyProjectRepoBuild", awsBackendItem):
            print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
            varsString = varsString + " -backend-config \"key=" + awsBackendItems.get(awsBackendItem) +"\""  
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
  
def getProjectsReposBuildInputs(yamlInputFile, awsCredFile, prbSecretsFile, subscriptionId, tenantId, resourceGroupLocation, resourceGroupName, subnetId, subscriptionName):
  print("inside getProjectsReposBuildInputs(...,...,...) function.")
  awsPublicAccessKey = ''
  awsSecretAccessKey = ''
  projectName = ''
  repoName = ''
  buildName = ''
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
      if re.match("projectRepoBuild", item):
        projectRepoBuild = topLevel_dict.get(item)
        for prbItem in projectRepoBuild:
            if re.match("sourceRepo", prbItem):
              print(prbItem, " is: ", projectRepoBuild.get(prbItem))
              varsString = varsString + " -var=\""+ prbItem + "=" + projectRepoBuild.get(prbItem) +"\""  
              nameStr = projectRepoBuild.get(prbItem)
              nameStr = nameStr.replace(" ", "")
              if nameStr.endswith('.git'):
                nameStr = nameStr[:-4]
              nameStr = nameStr.rpartition('/')[2]
              repoName = nameStr
              buildName = repoName
              projectName = repoName + "Project"
  varsString = varsString + " -var=\"projectName=" + projectName +"\""  
  varsString = varsString + " -var=\"repoName=" + repoName +"\""  
  varsString = varsString + " -var=\"buildName=" + buildName +"\""  
  if len(subscriptionId) > 2: 
    varsString = varsString + " -var=\"subscriptionId=" + subscriptionId +"\""  
  if len(tenantId) > 2: 
    varsString = varsString + " -var=\"tenantId=" + tenantId +"\""  
  if len(resourceGroupLocation) > 2: 
    varsString = varsString + " -var=\"resourceGroupLocation=" + resourceGroupLocation +"\""  
  if len(resourceGroupName) > 2: 
    varsString = varsString + " -var=\"resourceGroupName=" + resourceGroupName +"\""  
  if len(subnetId) > 2: 
    varsString = varsString + " -var=\"subnetId=" + subnetId +"\""  
  if len(subscriptionName) > 2: 
    varsString = varsString + " -var=\"subscriptionName=" + subscriptionName +"\""  
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
  
### End of the new stuff
#####################################################################################################################################
#####################################################################################################################################

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
            clientSecret = connectionItems.get(connectionItem)
      if re.match("awsConnection", item):  
        awsItems = topLevel_dict.get(item)  
        for awsItem in awsItems:  
          if re.match("awsPublicAccessKey", awsItem):  
            awsPublicAccessKey = awsItems.get(awsItem)  
          if re.match("awsSecretAccessKey", awsItem):  
            awsSecretAccessKey = awsItems.get(awsItem)  
  if len(clientSecret)>2 or len(awsPublicAccessKey)>2 or len(awsSecretAccessKey)>2 :  
    with open(foundationSecretsFile, "w") as file:
      if len(clientSecret) > 2:
        lineToAdd = "clientSecret=\""+clientSecret +"\"\n"
        file.write(lineToAdd)
      if len(awsPublicAccessKey) > 2:
        lineToAdd = "awsPublicAccessKey=\""+awsPublicAccessKey +"\"\n"
        file.write(lineToAdd)
      if len(awsSecretAccessKey) > 2:
        lineToAdd = "awsSecretAccessKey=\""+awsSecretAccessKey +"\"\n"
        file.write(lineToAdd)
    varsString = varsString + " -var-file=\""+ foundationSecretsFile +"\""
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

# def getProjectRepoBuildBackendConfig(yamlInputFile, awsCredFile):
#   varsString = ''
#   awsPublicAccessKey = ''
#   awsSecretAccessKey = ''
#   with open(yamlInputFile) as f:
#     topLevel_dict = yaml.safe_load(f)
#     for item in topLevel_dict:
#       if re.match("awsBackendTF", item):
#         awsBackendItems = topLevel_dict.get(item)
#         for awsBackendItem in awsBackendItems: 
#           if re.match("awsPublicAccessKey", awsBackendItem):
#             print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
#             awsPublicAccessKey = awsBackendItems.get(awsBackendItem)
#           if re.match("awsSecretAccessKey", awsBackendItem):
#             print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
#             awsSecretAccessKey = awsBackendItems.get(awsBackendItem)
#           if re.match("s3BucketNameTF", awsBackendItem):
#             print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
#             varsString = varsString + " -backend-config \"bucket=" + awsBackendItems.get(awsBackendItem) +"\""  
#           if re.match("s3BucketRegionTF", awsBackendItem):
#             print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
#             varsString = varsString + " -backend-config \"region=" + awsBackendItems.get(awsBackendItem) +"\""  
#           if re.match("dynamoDbTableNameTF", awsBackendItem):
#             print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
#             varsString = varsString + " -backend-config \"dynamodb_table=" + awsBackendItems.get(awsBackendItem) +"\""  
#           if re.match("moduleKeyProjectRepoBuild", awsBackendItem):
#             print(awsBackendItem, " is: ", awsBackendItems.get(awsBackendItem))
#             varsString = varsString + " -backend-config \"key=" + awsBackendItems.get(awsBackendItem) +"\""  
#   #REPLACE THE FOLLOWING BLOCK WITH MORE ADVANCED VERSION CAPABLE OF HANDLING MULTIPLE ACCOUNTS
#   if ((len(awsPublicAccessKey) > 3) and (len(awsSecretAccessKey) > 3)):  
#     with open(awsCredFile, "w") as file:
#       lineToAdd = '[default]\n'
#       file.write(lineToAdd)
#       lineToAdd = "aws_access_key_id="+awsPublicAccessKey+"\n"
#       file.write(lineToAdd)
#       lineToAdd = "aws_secret_access_key="+awsSecretAccessKey+"\n"
#       file.write(lineToAdd)
#   print("varsString is: ", varsString)
#   return varsString  
  
# def getProjectsReposBuildInputs(yamlInputFile, awsCredFile, prbSecretsFile, subscriptionId, tenantId, resourceGroupLocation, resourceGroupName, subnetId, subscriptionName):
#   print("inside getProjectsReposBuildInputs(...,...,...) function.")
#   awsPublicAccessKey = ''
#   awsSecretAccessKey = ''
#   projectName = ''
#   repoName = ''
#   buildName = ''
#   varsString = ''
#   azdoOrgPAT = ''
#   clientSecret = ''
#   with open(yamlInputFile) as f:
#     topLevel_dict = yaml.safe_load(f)
#     for item in topLevel_dict:
#       print("item is: ", item)
#       if re.match("azdoConnection", item):  
#         connectionItems = topLevel_dict.get(item)  
#         for connectionItem in connectionItems:
#           if re.match("azdoOrgServiceURL", connectionItem):
#             print(connectionItem, " is: ", connectionItems.get(connectionItem))
#             varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
#           if re.match("clientName", connectionItem):
#             print(connectionItem, " is: ", connectionItems.get(connectionItem))
#             varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
#           if re.match("serviceConnectionName", connectionItem):
#             print(connectionItem, " is: ", connectionItems.get(connectionItem))
#             varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
#           if re.match("clientId", connectionItem):
#             print(connectionItem, " is: ", connectionItems.get(connectionItem))
#             varsString = varsString + " -var=\""+ connectionItem + "=" + connectionItems.get(connectionItem) +"\""  
#           if re.match("azdoOrgPAT", connectionItem):
#             azdoOrgPAT = connectionItems.get(connectionItem)
#           if re.match("clientSecret", connectionItem):
#             clientSecret = connectionItems.get(connectionItem)
#       if re.match("projectRepoBuild", item):
#         projectRepoBuild = topLevel_dict.get(item)
#         for prbItem in projectRepoBuild:
#             if re.match("sourceRepo", prbItem):
#               print(prbItem, " is: ", projectRepoBuild.get(prbItem))
#               varsString = varsString + " -var=\""+ prbItem + "=" + projectRepoBuild.get(prbItem) +"\""  
#               nameStr = projectRepoBuild.get(prbItem)
#               nameStr = nameStr.replace(" ", "")
#               if nameStr.endswith('.git'):
#                 nameStr = nameStr[:-4]
#               nameStr = nameStr.rpartition('/')[2]
#               repoName = nameStr
#               buildName = repoName
#               projectName = repoName + "Project"
#   varsString = varsString + " -var=\"projectName=" + projectName +"\""  
#   varsString = varsString + " -var=\"repoName=" + repoName +"\""  
#   varsString = varsString + " -var=\"buildName=" + buildName +"\""  
#   if len(subscriptionId) > 2: 
#     varsString = varsString + " -var=\"subscriptionId=" + subscriptionId +"\""  
#   if len(tenantId) > 2: 
#     varsString = varsString + " -var=\"tenantId=" + tenantId +"\""  
#   if len(resourceGroupLocation) > 2: 
#     varsString = varsString + " -var=\"resourceGroupLocation=" + resourceGroupLocation +"\""  
#   if len(resourceGroupName) > 2: 
#     varsString = varsString + " -var=\"resourceGroupName=" + resourceGroupName +"\""  
#   if len(subnetId) > 2: 
#     varsString = varsString + " -var=\"subnetId=" + subnetId +"\""  
#   if len(subscriptionName) > 2: 
#     varsString = varsString + " -var=\"subscriptionName=" + subscriptionName +"\""  
#   if len(azdoOrgPAT)>2 or len(clientSecret)>2 :  
#     with open(prbSecretsFile, "w") as file:
#       if len(azdoOrgPAT) > 2:
#         lineToAdd = "azdoOrgPAT=\""+azdoOrgPAT +"\"\n"
#         file.write(lineToAdd)
#       if len(clientSecret) > 2: 
#         lineToAdd = "clientSecret=\""+clientSecret +"\"\n"
#         file.write(lineToAdd)
#     varsString = varsString + " -var-file=\""+ prbSecretsFile +"\""
#   print("varsString is: ", varsString)
#   return varsString
  
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
  

#####################################################################################################################################
#####################################################################################################################################
### Start of new stuff  

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
  
def manageRepoBuilds(operation, sourceReposList, project_calls_root, myYamlInputFile, awsCredFile, initCommand, project_name): 
  crudCommand = '' 
  if operation == "apply":
    crudCommand = 'terraform apply -auto-approve '
  elif operation == "destroy":
    crudCommand = 'terraform destroy -auto-approve '
  else:
    print("INVALID OPERATION.  The only acceptable values are \"apply\" or \"destroy\" . ")
    sys.exit(1)
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
      crudRepoBuildCommand = crudCommand + inputsRepoBuild
      print("crudRepoBuildCommand is: ", crudRepoBuildCommand)
      depfunc.runTerraformCommand(initBackendRepoBuildCommand, call_to_repobuild_dir)
      depfunc.runTerraformCommand(crudRepoBuildCommand, call_to_repobuild_dir)
      print("........................................................................................................")
  else:
    print("Zero source repository URLs were imported from the YAML input.  ")

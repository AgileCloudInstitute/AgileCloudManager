import subprocess
import re
import fileinput
import sys
import os 
import shutil
import base64
import requests

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
          azuredevops_key_vault_name=decodedline[39:]
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

def createReleaseDefinitionApiRequest(templateFile, azdo_organization_name, azdo_project_id, azdo_project_name, azdo_build_definition_id, azdo_git_repository_name, azdo_organization_service_url, queue_id, artifact_alias, azdo_service_connection_id, scriptInputVars, releaseDefName, environName ):
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
      data['artifacts'][0]['alias'] = artifactAlias
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
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['arguments'] = scriptInputVars            
          if item['taskId'] == '6c731c3c-3c68-459a-a5c9-bde6e6595b5b':
            print("This is a Bash script task. ")
            print("About to set the variables to be imported into the script.")
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['arguments'] = scriptInputVars            
          if item['taskId'] == '1e244d32-2dd4-4165-96fb-b7441ca9331e':
            print("This is a Key Vault script task.  ")
            print("ConnectedServiceName is: ", data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['ConnectedServiceName'])
            data['environments'][0]['deployPhases'][0]['workflowTasks'][myIdx]['inputs']['ConnectedServiceName'] = azdo_service_connection_id
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
   

import subprocess
import re
import fileinput
import sys
import os 
import shutil

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
storName = ''
nicName = ''
resourceGroupName = ''
resourceGroupLocation = ''
storageAccountNameTerraformBackend = ''
pipeKeyVaultName = ''
azuredevops_build_definition_id = ''
azuredevops_git_repository_id = ''
azuredevops_git_repository_name = ''
azuredevops_project_name = ''
azuredevops_project_id = ''
azuredevops_organization_service_url = ''
azuredevops_key_vault_name = ''  
azuredevops_subscription_name = ''    
azuredevops_client_name = ''    
azuredevops_service_connection_name = ''    

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
          azuredevops_subscription_name=decodedline[39:]
          print("azuredevops_subscription_name in deploymentFunctions.py is: ", azuredevops_subscription_name)
        if "azuredevops_client_name" in decodedline:
          print("Found azuredevops_client_name!")
          global azuredevops_client_name
          azuredevops_client_name=decodedline[39:]
          print("azuredevops_client_name in deploymentFunctions.py is: ", azuredevops_client_name)
        if "azuredevops_service_connection_name" in decodedline:
          print("Found azuredevops_service_connection_name!")
          global azuredevops_service_connection_name
          azuredevops_service_connection_name=decodedline[39:]
          print("azuredevops_service_connection_name in deploymentFunctions.py is: ", azuredevops_service_connection_name)
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

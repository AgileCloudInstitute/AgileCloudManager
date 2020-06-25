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
azuredevops_project_name = ''
azuredevops_git_repository_name = ''

def runTerraformCommand(commandToRun, workingDir ):
    print("Inside deploymentFunctions.py script and runTerraformCommand(..., ...) function. ")
    print("commandToRun is: " +commandToRun)
    print("workingDir is: " +workingDir)

    proc = subprocess.Popen( commandToRun,cwd=workingDir,stdout=subprocess.PIPE, shell=True)
    inOutputs='false'
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
     
        print(decodedline)
        if "Outputs:" in decodedline:  
          print("Reached \"Outputs\" section: ")
          print("decodedline is: " +decodedline)
          inOutputs='true'
        if 'true' in inOutputs:
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

          if "azuredevops_project_name" in decodedline:
            print("Found azuredevops_project_name!")
            global azuredevops_project_name
            azuredevops_project_name=decodedline[27:]
            print("azuredevops_project_name in deploymentFunctions.py is: ", azuredevops_project_name)
          if "azuredevops_git_repository_name" in decodedline:
            print("Found azuredevops_git_repository_name!")
            global azuredevops_git_repository_name
            azuredevops_git_repository_name=decodedline[34:]
            print("azuredevops_git_repository_name in deploymentFunctions.py is: ", azuredevops_git_repository_name)
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

def cloneSourceRepoToLocal(pathToTempRepoStorageParent, tmpRepoStorageFolder, sourceRepo):
  print("inside deploymentFunctions.py script and cloneSourceToLocal(...) function. ")
  newpath=pathToTempRepoStorageParent+tmpRepoStorageFolder
  print("Test 1")
  if not os.path.exists(newpath):
    os.makedirs(newpath)
  print("Test 2")
  cloneCommand='git clone --progress '+sourceRepo
  proc = subprocess.check_call(cloneCommand, stdout=subprocess.PIPE, shell=True, cwd=newpath, timeout=None)
  print("Test 3")
	
def destroyLocalCloneOfSourceRepo(pathToTempRepoStorageParent, tmpRepoStorageFolder):
  print("inside deploymentFunctions.py script and destroyLocalCloneOfSourceRepo(...) function. ")
  newpath=pathToTempRepoStorageParent+tmpRepoStorageFolder
  print("newpath is: ", newpath)
  deleteCommand="rmdir "+newpath+" /Q/S"
  proc = subprocess.Popen( deleteCommand,cwd=pathToTempRepoStorageParent,stdout=subprocess.PIPE, shell=True)
  success='false'
  while True:
    line = proc.stdout.readline()
    if line:
      thetext=line.decode('utf-8').rstrip('\r|\n')
      decodedline=ansi_escape.sub('', thetext)
      print(decodedline)
    else:
      break

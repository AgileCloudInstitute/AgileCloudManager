## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import os 
from distutils.dir_util import copy_tree 
from pathlib import Path 
import time
import pathlib
import shutil 
import commandRunner 
import configReader 
import requests 
import platform
import zipfile
import tarfile

def downloadAndExtractBinary(url, dependencies_binaries_path):
  url_elements = url.split("/")
  file = url_elements[-1]
  print("url is: ", url)
  print("file is: ", file)
  file_name = dependencies_binaries_path + file
  print("file_name is: ", file_name)
  with open(file_name, "wb") as file:
    response = requests.get(url)
    file.write(response.content)
  if file_name.endswith(".zip"):
    with zipfile.ZipFile(file_name,"r") as zip_ref:
      zip_ref.extractall(dependencies_binaries_path)
  elif file_name.endswith("tar.gz"):
    print("about to untar")
    with tarfile.open(file_name) as tar:
      tar.extractall(dependencies_binaries_path)
    print("finished untar")
  else:
    quit("ERROR: Unsupported file extension on one of your dependencies.  Binaries must either end with .zip or .tar.gz.  If you would like to support other options, submit a feature request. ")
  os.remove(file_name)


def getDependencies(**inputVars):
  configPath = inputVars.get('dirOfYamlFile') 
  yaml_setup_config_file_and_path = configPath +"\\"+"setupConfig.yaml"
  dependencies_binaries_path = inputVars.get('dependenciesBinariesPath')
  if platform.system() == "Windows":
    propName = "download-link-windows"
  else:
    propName = "download-link-linux"

#>  url_git = configReader.getDependencyProperty(yaml_setup_config_file_and_path, "dependencies", "git", propName)
#>  print("url_git is: ", url_git)
#>  downloadAndExtractBinary(url_git, dependencies_binaries_path)

  url_terraform = configReader.getDependencyProperty(yaml_setup_config_file_and_path, "dependencies", "terraform", propName)
  downloadAndExtractBinary(url_terraform, dependencies_binaries_path)
  url_packer = configReader.getDependencyProperty(yaml_setup_config_file_and_path, "dependencies", "packer", propName)
  downloadAndExtractBinary(url_packer, dependencies_binaries_path)


def checkDependencies(**inputVars):
  print("Checking to see if required dependencies are installed...")
  configPath = inputVars.get('dirOfYamlFile') 
  yaml_setup_config_file_and_path = configPath +"\\"+"setupConfig.yaml"  
  dependencies_binaries_path = inputVars.get('dependenciesBinariesPath')

  #Terraform
  tfVers = configReader.getDependencyVersion(yaml_setup_config_file_and_path, 'terraform')
  print("tfVers is: ", tfVers)
  if tfVers.count('.') == 1:
    tfVers = 'v' + tfVers + '.'
  else:
    quit('ERROR: The value you entered for terraform version in infrastructureConfig.yaml is not valid.  Only the first two blocks are accepted, as in \"x.y\" ')
  tfCheck = None
  tfDependencyCheckCommand = dependencies_binaries_path + "terraform --version"
  tfResult = commandRunner.checkIfInstalled(tfDependencyCheckCommand, tfVers)
  if 'Dependency is installed' in tfResult:
    tfCheck = True
  if 'NOT installed' in tfResult:
    tfCheck = False
  #ADD CHECK FOR SUCCESS TO MAKE TRUE
  print("tfCheck is: ", tfCheck)

  #packer
  pkrVers = configReader.getDependencyVersion(yaml_setup_config_file_and_path, 'packer')
  if pkrVers.count('.') != 1:
    quit('ERROR: The value you entered for packer version in infrastructureConfig.yaml is not valid.  Only the first two blocks are accepted, as in \"x.y\" ')
  if pkrVers.count('.') == 1:
    pkrVers = pkrVers + '.'
  pkrCheck = None
  pkrDependencyCheckCommand = dependencies_binaries_path + "packer --version"
  pkrResult = commandRunner.checkIfInstalled(pkrDependencyCheckCommand, pkrVers)
  if 'Dependency is installed' in tfResult:
    pkrCheck = True
  if 'NOT installed' in pkrResult:
    pkrCheck = False
  #ADD CHECK FOR SUCCESS TO MAKE TRUE
  print("pkrCheck is: ", pkrCheck)

#  quit("stop it!")

  #Azure CLI
  azVers = configReader.getDependencyVersion(yaml_setup_config_file_and_path, 'azure-cli')
#  print("azVers is: ", azVers)
  azCheck = None
  azDependencyCheckCmd = "az version"
  azResult = commandRunner.checkIfAzInstalled(azDependencyCheckCmd, azVers)
#  print("azResult is: ", azResult)
  if 'Dependency is installed' in azResult:
    azCheck = True
  if 'NOT installed' in azResult:
    azCheck = False
  #ADD CHECK FOR SUCCESS TO MAKE TRUE
  print("azCheck is: ", azCheck)

  #Azure-Devops CLI extension
  azdoVers = configReader.getDependencyVersionSecondLevel(yaml_setup_config_file_and_path, 'dependencies', 'azure-cli', 'modules', 'azure-cli-ext-azure-devops')
#  print("azdoVers is: ", azdoVers)
  azdoCheck = None
  azDependencyCheckCmd = "az version"
  azdoResult = commandRunner.checkIfAzdoInstalled(azDependencyCheckCmd, azdoVers)
#  print("azdoResult is: ", azdoResult)
  if 'Dependency is installed' in azdoResult:
    azdoCheck = True
  if 'NOT installed' in azdoResult:
    azdoCheck = False
  #ADD CHECK FOR SUCCESS TO MAKE TRUE
  print("azdoCheck is: ", azdoCheck)

  #git check
  gitVers = configReader.getDependencyVersion(yaml_setup_config_file_and_path, 'git')
  if gitVers.count('.') != 1:
    quit('ERROR: The value you entered for git version in infrastructureConfig.yaml is not valid.  Only the first two blocks are accepted, as in \"x.y\" ')
  if gitVers.count('.') == 1:
    gitVers = gitVers + '.'
  gitCheck = None
  gitDependencyCheckCommand = "git --version"
  gitResult = commandRunner.checkIfInstalled(gitDependencyCheckCommand, gitVers)
  if 'Dependency is installed' in gitResult:
    gitCheck = True
  if 'NOT installed' in gitResult:
    gitCheck = False
  #ADD CHECK FOR SUCCESS TO MAKE TRUE
  print("gitCheck is: ", gitCheck)

  print("-------------------------------------------------------------------------")
  if azCheck == True:
    azCheckPassStr = "az cli version " + azVers + ":                              INSTALLED"
    print(azCheckPassStr)
  elif (azCheck == False) or (azCheck == None):
    azCheckFailStr = "az cli version " + azVers + ":                              MISSING"
    print(azCheckFailStr)

  if azdoCheck == True:
    azdoCheckPassStr = "azure-devops extension version " + azdoVers + " for az cli:   INSTALLED"
    print(azdoCheckPassStr)
  elif (azCheck == False) or (azCheck == None):
    azdoCheckFailStr = "azure-devops extension version " + azdoVers + " for az cli:   MISSING"
    print(azdoCheckFailStr)

  if gitCheck == True:
    gitCheckPassStr = "git version " + gitVers + ":                                INSTALLED"
    print(gitCheckPassStr)
  elif (gitCheck == False) or (gitCheck == None):
    gitCheckFailStr = "git version " + gitVers + ":                                MISSING"

  if tfCheck == True:
    tfCheckPassStr = "terraform version " + tfVers + ":                         INSTALLED"
    print(tfCheckPassStr)
  elif (tfCheck == False) or (tfCheck == None):
    tfCheckFailStr = "terraform version " + tfVers + ":                         MISSING"
    print(tfCheckFailStr)

  if pkrCheck == True:
    pkrCheckPassStr = "packer version " + pkrVers + ":                              INSTALLED"
    print(pkrCheckPassStr)
  elif (pkrCheck == False) or (pkrCheck == None):
    pkrCheckFailStr = "packer version " + pkrVers + ":                              MISSING"
    print(pkrCheckFailStr)
  print("-------------------------------------------------------------------------")

  if (azCheck != True) or (azdoCheck != True) or (gitCheck != True) or (tfCheck != True) or (pkrCheck != True): 
    quit("ERROR:  Your system is missing one or more of the dependencies listed above.  Please make sure that the dependencies are properly installed and then re-run the setup on command. ")

def cloneTheSourceCode(**inputVars):
  configPath = inputVars.get('dirOfYamlFile') 
  yaml_infra_config_file_and_path = configPath +"\\"+"infrastructureConfig.yaml"  
  appParentPath = inputVars.get('app_parent_path')
  yaml_git_cred = appParentPath + "\\config-outside-acm-path\\vars\\admin\\gitCred.yaml"
  sourceRepoInstanceNames = configReader.getInstanceNames(yaml_infra_config_file_and_path, 'source')
  print("sourceRepoInstanceNames is: ", sourceRepoInstanceNames)
  pword = configReader.getFirstLevelValue(yaml_git_cred, 'gitPAT')

  for sourceRepoInstance in sourceRepoInstanceNames:
    repoUrl = configReader.getSourceCodeProperty(yaml_infra_config_file_and_path, 'source', sourceRepoInstance, 'repo')
    print("repoUrl is: ", repoUrl)
    repoUrlStart = repoUrl.split("//")[0] + "//"
    repoUrlEnd = "@" + repoUrl.split("//")[1]
    print("repoUrlStart is: ", repoUrlStart)
    print("repoUrlEnd is: ", repoUrlEnd)
    repoUrlCred = repoUrlStart + pword + repoUrlEnd
    repoBranch = configReader.getSourceCodeProperty(yaml_infra_config_file_and_path, 'source', sourceRepoInstance, 'branch')
    print("repoBranch is: ", repoBranch)
    gitCloneCommand = "git clone -b " + repoBranch + " " + repoUrlCred
#>>    print("gitCloneCommand is: ", gitCloneCommand)
    print("appParentPath is: ", appParentPath)

#>>    quit("debug git credentials")

    commandRunner.runShellCommandInWorkingDir(gitCloneCommand, appParentPath)
  #RETURN FAILURE QUIT IF ANY DEPENDENCY IS MISSING.  INCLUDE MESSAGE STATING WHICH DEPENDENCY IS MISSING.

def writeTerraformRC(terraformRC):
  with open(terraformRC, 'w') as filetowrite:
    #filetowrite.write('new content')
    print("provider_installation {")
    print("  filesystem_mirror {")
    print("    path    = \"C:\\projects\\terraform\\providers\"")
    print("    include = [\"*/*\"]")
    print("  }")
    print("  direct {")
    print("    exclude = [\"*/*\"]")
    print("  }")
    print("}")

def runSetup(**inputVars):
  app_parent_path = os.path.dirname(os.path.realpath("..\\"))
  from_path = app_parent_path+"\\agile-cloud-manager"+"\\"+"move-to-directory-outside-app-path\\"
  dest_path = app_parent_path+"\\config-outside-acm-path\\"
  #Create destination directory if it does not already exist 
  Path(dest_path).mkdir(parents=True, exist_ok=True)
  #Copy config and secret templates outside app path before they can be safely populated
  copy_tree(from_path, dest_path)
  #Copy actual credentials into their destination.
  if inputVars.get("keysDir") == '':
    #Git credentials
    gitCredFileSrc = app_parent_path + "\\gitCred.yaml"
    #azure credentials
    azCredFileSrc = app_parent_path + "\\adUserKeys.yaml"
    print("gitCredFileSrc is: ", gitCredFileSrc)
    print("azCredFileSrc is: ", azCredFileSrc)
  else:
    #Git credentials
    gitCredFileSrc = inputVars.get("keysDir") + "\\gitCred.yaml"
    #azure credentials
    azCredFileSrc = inputVars.get("keysDir") + "\\adUserKeys.yaml"
  print("gitCredFileSrc is: ", gitCredFileSrc)
  print("azCredFileSrc is: ", azCredFileSrc)
  gitCredFileDest = app_parent_path + "\\config-outside-acm-path\\vars\\admin\\gitCred.yaml"
  azCredFileDest = app_parent_path + "\\config-outside-acm-path\\vars\\admin\\adUserKeys.yaml"

  if os.path.exists(gitCredFileSrc): shutil.copyfile(gitCredFileSrc, gitCredFileDest)
  if os.path.exists(azCredFileSrc): shutil.copyfile(azCredFileSrc, azCredFileDest)

  getDependencies(**inputVars)
  checkDependencies(**inputVars)
  cloneTheSourceCode(**inputVars)

#>>  quit("breakpoint to debug dependencies download")

#>>KEEP THE FOLLOWING BLOCK TO ADD WHEN USING LOCAL COPIES OF PROVIDERS.  FOR NOW, WE ARE COMMENTING IT OUT TO TEST DOWNLOADING REMOTE COPIES OF PROVIDERS.
#>>  providersPath = os.path.join( inputVars.get('dependenciesPath') , ".terraform\\providers")
#>>  providersPath = providersPath.replace("\\", "\\\\")
#>>  appData = os.getenv('APPDATA').strip()
#>>  terraformRC = os.path.join( appData, "terraform.rc")
#>>  terraformRC = terraformRC.replace("\\", "\\\\")
#>>  print("About to write terraformRC to: ", terraformRC)
#>>  try: 
#>>    with open(terraformRC, 'w') as f:
#>>      f.write('provider_installation {\n')
#>>      f.write('  filesystem_mirror {\n')
#>>      f.write('    path    = "' + providersPath + '"\n')
#>>      f.write('    include = ["*/*"]\n')
#>>      f.write('  }\n')
#>>      f.write('\n')
#>>      f.write('  direct {\n')
#>>      f.write('    exclude = ["*/*"]\n')
#>>      f.write('  }\n')
#>>      f.write('}\n')
#>>  except (Exception) as e:
#>>    print(e)

#The next 2 lines are here for placekeeping.  make sure to move them to the appropriate place.
#  addExteensionCommand = 'az extension add --name azure-devops'
#  commandRunner.runShellCommand(addExteensionCommand)


def undoSetup(**inputVars):
  app_parent_path = os.path.dirname(os.path.realpath("..\\"))
  dest_path = app_parent_path+"\\config-outside-acm-path\\"
  try:
    shutil.rmtree(dest_path, ignore_errors=True)
  except FileNotFoundError:
    print("The config-outside-acm-path directory does not exist.  It may have already been deleted.")
  commandRunner.runShellCommandInWorkingDir("dir", app_parent_path)
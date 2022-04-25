## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import os 
from distutils.dir_util import copy_tree 
from pathlib import Path 
import time
import pathlib
import shutil 
import sys

import command_builder
import command_runner 
import config_fileprocessor 
import config_cliprocessor
import logWriter

import requests 
import platform
import zipfile
import tarfile
import shutil

def writeKeyFiles(keysDir):
  with open(keysDir+'keys.yaml', 'w') as file:
    file.write('secretsType: master\n')
    file.write('name: <put-actual-secret-value-here>\n')
    file.write('clientName: <put-actual-secret-value-here>\n')
    file.write('clientId: <put-actual-secret-value-here>\n')
    file.write('clientSecret: <put-actual-secret-value-here>\n')
    file.write('subscriptionId: <put-actual-secret-value-here>\n')
    file.write('subscriptionName: <put-actual-secret-value-here>\n')
    file.write('tenantId: <put-actual-secret-value-here>\n')
    file.write('azdoOrgPAT: <put-actual-secret-value-here>\n')
    file.write('azdoOrgServiceURL: <put-actual-secret-value-here>\n')
    file.write('gitUsername: <put-actual-secret-value-here>\n')
    file.write('gitPass: <put-actual-secret-value-here>\n')
  with open(keysDir+'gitCred.yaml', 'w') as file:
    file.write('gitUsername: <store-username-here>\n')
    file.write('gitPassword: <store-password-here>\n')
  with open(keysDir+'IamUserKeys.yaml', 'w') as file:
    file.write('keyPairs:\n')
    file.write('  - name: iamUserKeyPair\n')
    file.write('    _public_access_key: <put-actual-secret-value-here>\n')
    file.write('    _secret_access_key: <put-actual-secret-value-here>\n')

def createDirectoryStructure():
  acmAdminPath = config_cliprocessor.inputVars.get('acmAdminPath')
  keysParentPath = config_cliprocessor.inputVars.get('dirOfOutput')
  keysStarterPath = config_cliprocessor.inputVars.get('dirOfYamlKeys')
  varsPath = config_cliprocessor.inputVars.get('varsPath')
  dynamicVarsPath = config_cliprocessor.inputVars.get('dynamicVarsPath')
#  otherVarsPath = config_cliprocessor.inputVars.get('otherVarsPath')
  binariesPath = config_cliprocessor.inputVars.get('dependenciesBinariesPath')
  logsPath = config_cliprocessor.inputVars.get('verboseLogFilePath')

  adminPath = Path(acmAdminPath)
  if not os.path.exists(adminPath):
    os.mkdir(adminPath)

  keysPath = Path(keysParentPath)
  if not os.path.exists(keysPath):
    os.mkdir(keysPath)

  keysStarterPath = Path(keysStarterPath)
  if not os.path.exists(keysStarterPath):
    os.mkdir(keysStarterPath)
#    keysPathPlusSlash = str(keysStarterPath)+command_builder.getSlashForOS() 
#    keysPathPlusSlash = command_builder.formatPathForOS(keysPathPlusSlash)
#    writeKeyFiles(keysPathPlusSlash)

  binariesPath = Path(binariesPath)
  if not os.path.exists(binariesPath):
    if platform.system() == 'Windows':
      os.mkdir(binariesPath)
    elif platform.system() == 'Linux':
      #WORK ITEM: Make username in next line dynamic so that acm config can specify usernames other than packer
      print('binariesPath is: ', str(binariesPath))
      binariesCommand = 'sudo mkdir '+str(binariesPath)
      command_runner.runShellCommand(binariesCommand)
      chownCommand = 'sudo chown -R packer:packer '+str(binariesPath)
      command_runner.runShellCommand(chownCommand)

  varsPath = Path(varsPath)
  if not os.path.exists(varsPath):
    os.mkdir(varsPath)

  dynamicVarsPath = Path(dynamicVarsPath)
  if not os.path.exists(dynamicVarsPath):
    os.mkdir(dynamicVarsPath)

#  otherVarsPath = Path(otherVarsPath)
#  print('.....++++  otherVarsPath is: ', otherVarsPath)
#  if not os.path.exists(otherVarsPath):
#    os.mkdir(otherVarsPath)

  logsPath = Path(logsPath)
  if not os.path.exists(logsPath):
    if platform.system() == 'Windows':
      os.mkdir(logsPath)
    elif platform.system() == 'Linux':
      logsCommand = 'sudo mkdir '+str(logsPath)
      command_runner.runShellCommand(logsCommand)
      #WORK ITEM: Make username in next line dynamic so that acm config can specify usernames other than packer
      chownCommand = 'sudo chown -R packer:packer '+str(logsPath)
      command_runner.runShellCommand(chownCommand)
      print('logsPath is: ', str(logsPath))
#      quit('!!')

  print('Contents of acmAdmin directory are: ')
  for item in os.listdir(adminPath):
    print('... ', item)

  print('Contents of keys directory are: ')
  for item in os.listdir(keysPath):
    print('... ', item)

def recursiveDelete(startingPath):
  for root, dirs, files in os.walk(startingPath):
    for name in files:
            print(os.path.join(root, name)) 
            os.remove(os.path.join(root, name))
    for name in dirs:
            print(os.path.join(root, name))
            shutil.rmtree(os.path.join(root, name))
  if os.path.exists(startingPath):
    shutil.rmtree(startingPath)

def downloadAndExtractBinary(url, dependencies_binaries_path):
  url_elements = url.split("/")
  file = url_elements[-1]
  file_name = dependencies_binaries_path + file
  print('file_name is: ', file_name)
#  quit('c4')
  with open(file_name, "wb") as file:
    response = requests.get(url)
    file.write(response.content)
  if file_name.endswith(".zip"):
    with zipfile.ZipFile(file_name,"r") as zip_ref:
      zip_ref.extractall(dependencies_binaries_path)
  elif file_name.endswith("tar.gz"):
    with tarfile.open(file_name) as tar:
      tar.extractall(dependencies_binaries_path)
  else:
    logString = "ERROR: Unsupported file extension on one of your dependencies.  Binaries must either end with .zip or .tar.gz.  If you would like to support other options, submit a feature request. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  os.remove(file_name)


def getDependencies():
#  userCallingDir = os.path.abspath(".")
  configPath = config_cliprocessor.inputVars.get('acmConfigPath') #os.path.abspath(".") #config_cliprocessor.inputVars.get('dirOfYamlFile') 
  yaml_setup_config_file_and_path = configPath + command_builder.getSlashForOS() + "setupConfig.yaml"
  yaml_setup_config_file_and_path = command_builder.formatPathForOS(yaml_setup_config_file_and_path)
#  if 'ACM_SHARED_KEYS' in os.environ:
#    dependencies_binaries_path = os.environ['ACM_SHARED_KEYS']+'\\' #config_cliprocessor.inputVars.get('dependenciesBinariesPath')
#  else:
  userCallingDir = os.path.abspath(".")
  path = Path(userCallingDir)
  parentPath = path.parent
  dependencies_binaries_path = config_cliprocessor.inputVars.get('dependenciesBinariesPath')
  dependencies_binaries_path = command_builder.formatPathForOS(dependencies_binaries_path)
  if platform.system() == "Windows":
    propName = "download-link-windows"
  else:
    propName = "download-link-linux"
  print("configPath is: ", configPath)
  print("yaml_setup_config_file_and_path is: ", yaml_setup_config_file_and_path)
  print("dependencies_binaries_path is: ", dependencies_binaries_path)
  print("propName is: ", propName)
  url_terraform = config_fileprocessor.getDependencyProperty(yaml_setup_config_file_and_path, "dependencies", "terraform", propName)
  print("url_terraform is: ", url_terraform)
  downloadAndExtractBinary(url_terraform, dependencies_binaries_path)
#  quit('ccc')
  url_packer = config_fileprocessor.getDependencyProperty(yaml_setup_config_file_and_path, "dependencies", "packer", propName)
  downloadAndExtractBinary(url_packer, dependencies_binaries_path)
  if platform.system() == 'Linux':
    #import stat
    fullyQualifiedPath = dependencies_binaries_path + 'terraform'
    myCmd = 'chmod +x ' + fullyQualifiedPath
    command_runner.runShellCommand(myCmd)
#    st = os.stat(fullyQualifiedPath)
#    os.chmod(fullyQualifiedPath, st.st_mode | stat.S_IEXEC)
    fullyQualifiedPath = dependencies_binaries_path + 'packer'
    myCmd = 'chmod +x ' + fullyQualifiedPath
    command_runner.runShellCommand(myCmd)
#    st = os.stat(fullyQualifiedPath)
#    os.chmod(fullyQualifiedPath, st.st_mode | stat.S_IEXEC)


def checkDependencies():
  logString = "Checking to see if required dependencies are installed..."
  logWriter.writeLogVerbose("acm", logString)
  configPath = config_cliprocessor.inputVars.get('acmConfigPath') #os.path.abspath(".") #config_cliprocessor.inputVars.get('dirOfYamlFile') 
  yaml_setup_config_file_and_path = configPath +command_builder.getSlashForOS() + "setupConfig.yaml"  
  yaml_setup_config_file_and_path = command_builder.formatPathForOS(yaml_setup_config_file_and_path)
  dependencies_binaries_path = config_cliprocessor.inputVars.get('dependenciesBinariesPath')
  dependencies_binaries_path = command_builder.formatPathForOS(dependencies_binaries_path)
  print('::: dependencies_binaries_path is: ', dependencies_binaries_path)
  #Terraform
  tfVers = config_fileprocessor.getDependencyVersion(yaml_setup_config_file_and_path, 'terraform')
  if tfVers.count('.') == 1:
    tfVers = 'v' + tfVers + '.'
  else:
    logString = 'ERROR: The value you entered for terraform version in infrastructureConfig.yaml is not valid.  Only the first two blocks are accepted, as in \"x.y\" '
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  tfCheck = None
  tfDependencyCheckCommand = dependencies_binaries_path + "terraform --version"
  tfResult = command_runner.checkIfInstalled(tfDependencyCheckCommand, tfVers)
  print('+++   tfResult is: ', tfResult)
  if 'Dependency is installed' in tfResult:
    tfCheck = True
  if 'NOT installed' in tfResult:
    tfCheck = False
  #ADD CHECK FOR SUCCESS TO MAKE TRUE

  #packer
  pkrVers = config_fileprocessor.getDependencyVersion(yaml_setup_config_file_and_path, 'packer')
  if pkrVers.count('.') != 1:
    logString = 'ERROR: The value you entered for packer version in infrastructureConfig.yaml is not valid.  Only the first two blocks are accepted, as in \"x.y\" '
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  if pkrVers.count('.') == 1:
    pkrVers = pkrVers + '.'
  pkrCheck = None
  pkrDependencyCheckCommand = dependencies_binaries_path + "packer --version"
  pkrResult = command_runner.checkIfInstalled(pkrDependencyCheckCommand, pkrVers)
  if 'Dependency is installed' in tfResult:
    pkrCheck = True
  if 'NOT installed' in pkrResult:
    pkrCheck = False
  #ADD CHECK FOR SUCCESS TO MAKE TRUE

  #Azure CLI
  azVers = config_fileprocessor.getDependencyVersion(yaml_setup_config_file_and_path, 'azure-cli')
  azCheck = None
  azDependencyCheckCmd = "az version"
  azResult = command_runner.checkIfAzInstalled(azDependencyCheckCmd, azVers)
  if 'Dependency is installed' in azResult:
    azCheck = True
  if 'NOT installed' in azResult:
    azCheck = False
  #ADD CHECK FOR SUCCESS TO MAKE TRUE

  #Azure-Devops CLI extension
  azdoVers = config_fileprocessor.getDependencyVersionSecondLevel(yaml_setup_config_file_and_path, 'dependencies', 'azure-cli', 'modules', 'azure-cli-ext-azure-devops')
  azdoCheck = None
  azDependencyCheckCmd = "az version"
  azdoResult = command_runner.checkIfAzdoInstalled(azDependencyCheckCmd, azdoVers)
  if 'Dependency is installed' in azdoResult:
    azdoCheck = True
  if 'NOT installed' in azdoResult:
    azdoCheck = False
  #ADD CHECK FOR SUCCESS TO MAKE TRUE
#  print('azdoVers is: ', azdoVers)
#  print('azdoResult is: ', str(azdoResult))
#  print('azdoCheck is: ', azdoCheck)
#  quit('!mm!')

  #git check
  gitVers = config_fileprocessor.getDependencyVersion(yaml_setup_config_file_and_path, 'git')
  if gitVers.count('.') != 0:
    logString = 'ERROR: The value you entered for git version in infrastructureConfig.yaml is not valid.  Only the first block is accepted, as in \"x\" '
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  if gitVers.count('.') == 0:
    gitVers = gitVers + '.'
  gitCheck = None
  gitDependencyCheckCommand = "git --version"
  gitResult = command_runner.checkIfInstalled(gitDependencyCheckCommand, gitVers)
  if 'Dependency is installed' in gitResult:
    gitCheck = True
  if 'NOT installed' in gitResult:
    gitCheck = False
  #ADD CHECK FOR SUCCESS TO MAKE TRUE

  logString = "-------------------------------------------------------------------------"
  logWriter.writeLogVerbose("acm", logString)
  if azCheck == True:
    azCheckPassStr = "az cli version " + azVers + ":                              INSTALLED"
    logString = azCheckPassStr
    logWriter.writeLogVerbose("acm", logString)
  elif (azCheck == False) or (azCheck == None):
    azCheckFailStr = "az cli version " + azVers + ":                              MISSING"
    logString = azCheckFailStr
    logWriter.writeLogVerbose("acm", logString)

  if azdoCheck == True:
    azdoCheckPassStr = "azure-devops extension version " + azdoVers + " for az cli:   INSTALLED"
    logString = azdoCheckPassStr
    logWriter.writeLogVerbose("acm", logString)
  elif (azCheck == False) or (azCheck == None):
    azdoCheckFailStr = "azure-devops extension version " + azdoVers + " for az cli:   MISSING"
    logString = azdoCheckFailStr
    logWriter.writeLogVerbose("acm", logString)

  if gitCheck == True:
    gitCheckPassStr = "git version " + gitVers + ":                                INSTALLED"
    logString = gitCheckPassStr
    logWriter.writeLogVerbose("acm", logString)
  elif (gitCheck == False) or (gitCheck == None):
    gitCheckFailStr = "git version " + gitVers + ":                                MISSING"
    logString = gitCheckFailStr
    logWriter.writeLogVerbose("acm", logString)

  if tfCheck == True:
    tfCheckPassStr = "terraform version " + tfVers + ":                         INSTALLED"
    logString = tfCheckPassStr
    logWriter.writeLogVerbose("acm", logString)
  elif (tfCheck == False) or (tfCheck == None):
    tfCheckFailStr = "terraform version " + tfVers + ":                         MISSING"
    logString = tfCheckFailStr
    logWriter.writeLogVerbose("acm", logString)

  if pkrCheck == True:
    pkrCheckPassStr = "packer version " + pkrVers + ":                              INSTALLED"
    logString = pkrCheckPassStr
    logWriter.writeLogVerbose("acm", logString)
  elif (pkrCheck == False) or (pkrCheck == None):
    pkrCheckFailStr = "packer version " + pkrVers + ":                              MISSING"
    logString = pkrCheckFailStr
    logWriter.writeLogVerbose("acm", logString)
  logString = "-------------------------------------------------------------------------"
  logWriter.writeLogVerbose("acm", logString)

  if (azCheck != True) or (azdoCheck != True) or (gitCheck != True) or (tfCheck != True) or (pkrCheck != True): 
    print("azCheck is: ", azCheck)
    print("azdoCheck is: ", azdoCheck)
    print("gitCheck is: ", gitCheck)
    print("tfCheck is: ", tfCheck)
    print("pkrCheck is: ", pkrCheck)
    logString = "ERROR:  Your system is missing one or more of the dependencies listed above.  Please make sure that the dependencies are properly installed and then re-run the setup on command. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)

def cloneTheSourceCode():
#  configPath = os.path.abspath(".") #config_cliprocessor.inputVars.get('dirOfYamlFile') 
  configPath = config_cliprocessor.inputVars.get('acmConfigPath') #os.path.abspath(".") #config_cliprocessor.inputVars.get('dirOfYamlFile') 
  yaml_infra_config_file_and_path = configPath +command_builder.getSlashForOS() + "setupConfig.yaml"  
  yaml_infra_config_file_and_path = command_builder.formatPathForOS(yaml_infra_config_file_and_path)
  userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
  sourceRepoInstanceNames = config_fileprocessor.getInstanceNames(yaml_infra_config_file_and_path, 'source')
#  path = Path(userCallingDir)
#  parentPath = path.parent
  acmAdmin = userCallingDir + command_builder.getSlashForOS() + 'acmAdmin'
  acmAdmin = command_builder.formatPathForOS(acmAdmin)
  keys = acmAdmin + command_builder.getSlashForOS() + 'keys' + command_builder.getSlashForOS() + 'starter'
  keys = command_builder.formatPathForOS(keys)
  keysPathPlusSlash = keys+command_builder.getSlashForOS() 
  keysPathPlusSlash = command_builder.formatPathForOS(keysPathPlusSlash)
  #WORK ITEM: Change the following line to make the file name cloud-agnostic
  keys_file_and_path = keysPathPlusSlash+'keys.yaml'
  pword = config_fileprocessor.getFirstLevelValue(keys_file_and_path, 'gitPass')
  for sourceRepoInstance in sourceRepoInstanceNames:
    repoUrl = config_fileprocessor.getSourceCodeProperty(yaml_infra_config_file_and_path, 'source', sourceRepoInstance, 'repo')
    repoUrlStart = repoUrl.split("//")[0] + "//"
    repoUrlEnd = "@" + repoUrl.split("//")[1]
    repoUrlCred = repoUrlStart + pword + repoUrlEnd
    repoBranch = config_fileprocessor.getSourceCodeProperty(yaml_infra_config_file_and_path, 'source', sourceRepoInstance, 'branch')
    gitCloneCommand = "git clone -b " + repoBranch + " " + repoUrlCred
    command_runner.runShellCommandInWorkingDir(gitCloneCommand, userCallingDir)
  #RETURN FAILURE QUIT IF ANY DEPENDENCY IS MISSING.  INCLUDE MESSAGE STATING WHICH DEPENDENCY IS MISSING.

def writeTerraformRC(terraformRC):
  with open(terraformRC, 'w') as filetowrite:
    print("provider_installation {")
    print("  filesystem_mirror {")
    print("    path    = \"C:\\projects\\terraform\\providers\"")
    print("    include = [\"*/*\"]")
    print("  }")
    print("  direct {")
    print("    exclude = [\"*/*\"]")
    print("  }")
    print("}")

def runConfigure():
  getDependencies()
  checkDependencies()
  cloneTheSourceCode()

#>>KEEP THE FOLLOWING BLOCK TO ADD WHEN USING LOCAL COPIES OF PROVIDERS.  FOR NOW, WE ARE COMMENTING IT OUT TO TEST DOWNLOADING REMOTE COPIES OF PROVIDERS.
#>>  providersPath = os.path.join( config_cliprocessor.inputVars.get('dependenciesPath') , ".terraform\\providers")
#>>  providersPath = providersPath.replace("\\", "\\\\")
#>>  appData = os.getenv('APPDATA').strip()
#>>  terraformRC = os.path.join( appData, "terraform.rc")
#>>  terraformRC = terraformRC.replace("\\", "\\\\")
#>>  logString = "About to write terraformRC to: " + terraformRC
#>>  logWriter.writeLogVerbose("acm", logString)
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
#>>    logString = str(e)
#>>    logWriter.writeLogVerbose("acm", logString)



def undoConfigure():
  admin_path = config_cliprocessor.inputVars.get('acmAdminPath')
  print('admin_path is: ', admin_path)
  deleteLocalCopiesOfGitRepos()
  admin_path = config_cliprocessor.inputVars.get('acmAdminPath')
  print('admin_path is: ', admin_path)
  try:
    shutil.rmtree(admin_path, ignore_errors=True)
  except FileNotFoundError:
    logString = "The acmAdmin directory does not exist.  It may have already been deleted."
    logWriter.writeLogVerbose("acm", logString)
  if platform.system() == 'Linux':
    binaries_path = '/opt/acm/'
    try:
      shutil.rmtree(binaries_path, ignore_errors=True)
    except FileNotFoundError:
      logString = "The /opt/acm/ directory does not exist.  It may have already been deleted."
      logWriter.writeLogVerbose("acm", logString)
    command_runner.runShellCommandInWorkingDir("dir", '/opt')
  userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
  callsToModulesDir = userCallingDir + command_builder.getSlashForOS() + 'calls-to-modules'
  try:
    shutil.rmtree(callsToModulesDir, ignore_errors=True)
  except FileNotFoundError:
    logString = "The calls-to-modules directory does not exist.  It may have already been deleted."
    logWriter.writeLogVerbose("acm", logString)

def deleteLocalCopiesOfGitRepos():
  config_path = config_cliprocessor.inputVars.get('acmConfigPath')
  print('config_path is: ', config_path)
  if platform.system() == 'Linux':
    gitRemoveCmd = 'rm -rf .git'
  if platform.system() == 'Windows':
    gitRemoveCmd = 'rmdir /s /q .git'
  #Now get the names of all the repos that were imported. 
  yaml_infra_config_file_and_path = config_path +command_builder.getSlashForOS() + "setupConfig.yaml"  
  yaml_infra_config_file_and_path = command_builder.formatPathForOS(yaml_infra_config_file_and_path)
  userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
  sourceRepoInstanceNames = config_fileprocessor.getInstanceNames(yaml_infra_config_file_and_path, 'source')
  #Now delete the local copy of each imported repo.
  for sourceRepoInstance in sourceRepoInstanceNames:
    repoUrl = config_fileprocessor.getSourceCodeProperty(yaml_infra_config_file_and_path, 'source', sourceRepoInstance, 'repo')
    repoUrlEnd = repoUrl.split("//")[1]
    repoName = repoUrlEnd.split('/')[-1].replace('.git','')
    repoPath = userCallingDir + command_builder.getSlashForOS() + repoName
    print('repoPath is: ', repoPath)
    command_runner.runShellCommandInWorkingDir(gitRemoveCmd, repoPath)
    try:
      shutil.rmtree(repoPath)
    except FileNotFoundError:
      logString = "The "+repoName+" directory does not exist.  It may have already been deleted."
      logWriter.writeLogVerbose("acm", logString)
  #No delete the acmConfig directory
  command_runner.runShellCommandInWorkingDir(gitRemoveCmd, config_path)
  try:
    shutil.rmtree(config_path)
  except FileNotFoundError:
    logString = "The acmConfig directory does not exist.  It may have already been deleted."
    logWriter.writeLogVerbose("acm", logString)

def runSetup():
  addExtensionCommand = 'az extension add --name azure-devops'
  command_runner.runShellCommand(addExtensionCommand)
  addAccountExtensionCommand = 'az extension add --upgrade -n account'
  command_runner.runShellCommand(addAccountExtensionCommand)

  createDirectoryStructure()
  sourceKeys = config_cliprocessor.inputVars.get('sourceKeys') + command_builder.getSlashForOS() + 'keys.yaml'
  gitPass = config_fileprocessor.getGitPassFromSourceKeys(sourceKeys)
  sourceRepo = config_cliprocessor.inputVars.get('sourceRepo')
  sourceRepo = command_builder.assembleSourceRepo(gitPass, sourceRepo)
  cloneCommand = command_builder.assembleCloneCommand(sourceRepo)
  print('gitPass is: ', gitPass)
  print('sourceRepo is: ', sourceRepo)
  print('cloneCommand is: ', cloneCommand)
#  quit('y!.')
  command_runner.runShellCommand(cloneCommand)
  sourceRepoDestinationDir = sourceRepo.split('/')[-1].replace('.git','')
  sourceRepoDestinationDir = config_cliprocessor.inputVars.get('userCallingDir') + sourceRepoDestinationDir
  sourceRepoDestinationDir = command_builder.formatPathForOS(sourceRepoDestinationDir)
  acmConfigPath = config_cliprocessor.inputVars.get('acmConfigPath')
  acmConfigPath = command_builder.formatPathForOS(acmConfigPath)
  print('sourceRepoDestinationDir is: ', sourceRepoDestinationDir)
  print('acmConfigPath is: ', acmConfigPath)
  os.rename(sourceRepoDestinationDir, acmConfigPath)
  keysStarterPath = config_cliprocessor.inputVars.get('dirOfYamlKeys')
  print('keysStarterPath is: ', keysStarterPath)
  destinationKeys = keysStarterPath +command_builder.getSlashForOS()+'keys.yaml'
#  shutil.copy(sourceKeys, keysStarterPath)
  shutil.copy(sourceKeys, destinationKeys)
  runConfigure()
#  quit('BREAKPOINT to debug runSetup()')

def undoSetup():
  undoConfigure()
#  quit('BREAKPOINT to debug undoSetup()')
#  removeDirectoryStructure()


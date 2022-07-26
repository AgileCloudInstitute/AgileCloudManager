## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import command_runner 
import command_formatter
import config_fileprocessor 
import config_cliprocessor
import log_writer

import os
from pathlib import Path 
import shutil 
import sys
import requests 
import platform
import zipfile
import tarfile
import shutil
import yaml
import re

class workflow_setup:
  
  def __init__(self):  
    pass

  #@private
  def createDirectoryStructure(self):
    acmAdminPath = config_cliprocessor.inputVars.get('acmAdminPath')
    keysParentPath = config_cliprocessor.inputVars.get('dirOfOutput')
    keysStarterPath = config_cliprocessor.inputVars.get('dirOfYamlKeys')
    varsPath = config_cliprocessor.inputVars.get('varsPath')
    dynamicVarsPath = config_cliprocessor.inputVars.get('dynamicVarsPath')
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

    print('Contents of acmAdmin directory are: ')
    for item in os.listdir(adminPath):
      print('... ', item)

    print('Contents of keys directory are: ')
    for item in os.listdir(keysPath):
      print('... ', item)

  #@private
  def downloadAndExtractBinary(self, url, dependencies_binaries_path):
    url_elements = url.split("/")
    file = url_elements[-1]
    file_name = dependencies_binaries_path + file
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
      log_writer.writeLogVerbose("acm", logString)
      sys.exit(1)
    os.remove(file_name)

  #@private
  def getDependencies(self):
    configPath = config_cliprocessor.inputVars.get('acmConfigPath') 
    yaml_setup_config_file_and_path = configPath + command_formatter.getSlashForOS() + "setupConfig.yaml"
    yaml_setup_config_file_and_path = command_formatter.formatPathForOS(yaml_setup_config_file_and_path)
    dependencies_binaries_path = config_cliprocessor.inputVars.get('dependenciesBinariesPath')
    dependencies_binaries_path = command_formatter.formatPathForOS(dependencies_binaries_path)
    if platform.system() == "Windows":
      propName = "download-link-windows"
    else:
      propName = "download-link-linux"
    url_terraform = self.getDependencyProperty(yaml_setup_config_file_and_path, "dependencies", "terraform", propName)
    self.downloadAndExtractBinary(url_terraform, dependencies_binaries_path)
    url_packer = self.getDependencyProperty(yaml_setup_config_file_and_path, "dependencies", "packer", propName)
    self.downloadAndExtractBinary(url_packer, dependencies_binaries_path)
    if platform.system() == 'Linux':
      #import stat
      fullyQualifiedPath = dependencies_binaries_path + 'terraform'
      myCmd = 'chmod +x ' + fullyQualifiedPath
      command_runner.runShellCommand(myCmd)
      fullyQualifiedPath = dependencies_binaries_path + 'packer'
      myCmd = 'chmod +x ' + fullyQualifiedPath
      command_runner.runShellCommand(myCmd)

  #@private
  def checkDependencies(self):
    logString = "Checking to see if required dependencies are installed..."
    log_writer.writeLogVerbose("acm", logString)
    configPath = config_cliprocessor.inputVars.get('acmConfigPath') #os.path.abspath(".") #config_cliprocessor.inputVars.get('dirOfYamlFile') 
    yaml_setup_config_file_and_path = configPath +command_formatter.getSlashForOS() + "setupConfig.yaml"  
    yaml_setup_config_file_and_path = command_formatter.formatPathForOS(yaml_setup_config_file_and_path)
    dependencies_binaries_path = config_cliprocessor.inputVars.get('dependenciesBinariesPath')
    dependencies_binaries_path = command_formatter.formatPathForOS(dependencies_binaries_path)
    print('::: dependencies_binaries_path is: ', dependencies_binaries_path)
    #Terraform
    tfVers = self.getDependencyVersion(yaml_setup_config_file_and_path, 'terraform')
    if tfVers.count('.') == 1:
      tfVers = 'v' + tfVers + '.'
    else:
      logString = 'ERROR: The value you entered for terraform version in infrastructureConfig.yaml is not valid.  Only the first two blocks are accepted, as in \"x.y\" '
      log_writer.writeLogVerbose("acm", logString)
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
    pkrVers = self.getDependencyVersion(yaml_setup_config_file_and_path, 'packer')
    if pkrVers.count('.') != 1:
      logString = 'ERROR: The value you entered for packer version in infrastructureConfig.yaml is not valid.  Only the first two blocks are accepted, as in \"x.y\" '
      log_writer.writeLogVerbose("acm", logString)
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
    azVers = self.getDependencyVersion(yaml_setup_config_file_and_path, 'azure-cli')
    azCheck = None
    azDependencyCheckCmd = "az version"
    azResult = command_runner.checkIfAzInstalled(azDependencyCheckCmd, azVers)
    if 'Dependency is installed' in azResult:
      azCheck = True
    if 'NOT installed' in azResult:
      azCheck = False
    #ADD CHECK FOR SUCCESS TO MAKE TRUE

    #Azure-Devops CLI extension
    azdoVers = self.getDependencyVersionSecondLevel(yaml_setup_config_file_and_path, 'dependencies', 'azure-cli', 'modules', 'azure-cli-ext-azure-devops')
    azdoCheck = None
    azDependencyCheckCmd = "az version"
    azdoResult = command_runner.checkIfAzdoInstalled(azDependencyCheckCmd, azdoVers)
    if 'Dependency is installed' in azdoResult:
      azdoCheck = True
    if 'NOT installed' in azdoResult:
      azdoCheck = False
    #ADD CHECK FOR SUCCESS TO MAKE TRUE

    #git check
    gitVers = self.getDependencyVersion(yaml_setup_config_file_and_path, 'git')
    if gitVers.count('.') != 0:
      logString = 'ERROR: The value you entered for git version in infrastructureConfig.yaml is not valid.  Only the first block is accepted, as in \"x\" '
      log_writer.writeLogVerbose("acm", logString)
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
    log_writer.writeLogVerbose("acm", logString)
    if azCheck == True:
      azCheckPassStr = "az cli version " + azVers + ":                              INSTALLED"
      logString = azCheckPassStr
      log_writer.writeLogVerbose("acm", logString)
    elif (azCheck == False) or (azCheck == None):
      azCheckFailStr = "az cli version " + azVers + ":                              MISSING"
      logString = azCheckFailStr
      log_writer.writeLogVerbose("acm", logString)
    if azdoCheck == True:
      azdoCheckPassStr = "azure-devops extension version " + azdoVers + " for az cli:   INSTALLED"
      logString = azdoCheckPassStr
      log_writer.writeLogVerbose("acm", logString)
    elif (azCheck == False) or (azCheck == None):
      azdoCheckFailStr = "azure-devops extension version " + azdoVers + " for az cli:   MISSING"
      logString = azdoCheckFailStr
      log_writer.writeLogVerbose("acm", logString)
    if gitCheck == True:
      gitCheckPassStr = "git version " + gitVers + ":                                INSTALLED"
      logString = gitCheckPassStr
      log_writer.writeLogVerbose("acm", logString)
    elif (gitCheck == False) or (gitCheck == None):
      gitCheckFailStr = "git version " + gitVers + ":                                MISSING"
      logString = gitCheckFailStr
      log_writer.writeLogVerbose("acm", logString)
    if tfCheck == True:
      tfCheckPassStr = "terraform version " + tfVers + ":                         INSTALLED"
      logString = tfCheckPassStr
      log_writer.writeLogVerbose("acm", logString)
    elif (tfCheck == False) or (tfCheck == None):
      tfCheckFailStr = "terraform version " + tfVers + ":                         MISSING"
      logString = tfCheckFailStr
      log_writer.writeLogVerbose("acm", logString)
    if pkrCheck == True:
      pkrCheckPassStr = "packer version " + pkrVers + ":                              INSTALLED"
      logString = pkrCheckPassStr
      log_writer.writeLogVerbose("acm", logString)
    elif (pkrCheck == False) or (pkrCheck == None):
      pkrCheckFailStr = "packer version " + pkrVers + ":                              MISSING"
      logString = pkrCheckFailStr
      log_writer.writeLogVerbose("acm", logString)
    logString = "-------------------------------------------------------------------------"
    log_writer.writeLogVerbose("acm", logString)
    if (azCheck != True) or (azdoCheck != True) or (gitCheck != True) or (tfCheck != True) or (pkrCheck != True): 
      print("azCheck is: ", azCheck)
      print("azdoCheck is: ", azdoCheck)
      print("gitCheck is: ", gitCheck)
      print("tfCheck is: ", tfCheck)
      print("pkrCheck is: ", pkrCheck)
      logString = "ERROR:  Your system is missing one or more of the dependencies listed above.  Please make sure that the dependencies are properly installed and then re-run the setup on command. "
      log_writer.writeLogVerbose("acm", logString)
      sys.exit(1)

  #@private
  def cloneTheSourceCode(self):
    configPath = config_cliprocessor.inputVars.get('acmConfigPath') 
    yaml_setup_config_file_and_path = configPath +command_formatter.getSlashForOS() + "setupConfig.yaml"  
    yaml_setup_config_file_and_path = command_formatter.formatPathForOS(yaml_setup_config_file_and_path)
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    sourceRepoInstanceNames = self.getInstanceNames(yaml_setup_config_file_and_path, 'source')
    acmAdmin = userCallingDir + command_formatter.getSlashForOS() + 'acmAdmin'
    acmAdmin = command_formatter.formatPathForOS(acmAdmin)
    keys = config_cliprocessor.inputVars.get('dirOfYamlKeys')
    keys = command_formatter.formatPathForOS(keys)
    keysPathPlusSlash = keys+command_formatter.getSlashForOS() 
    keysPathPlusSlash = command_formatter.formatPathForOS(keysPathPlusSlash)
    #WORK ITEM: Change the following line to make the file name cloud-agnostic
    keys_file_and_path = keysPathPlusSlash+'keys.yaml'
    pword = config_fileprocessor.getFirstLevelValue(keys_file_and_path, 'gitPass')
    for sourceRepoInstance in sourceRepoInstanceNames:
      repoUrl = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'repo')
      repoUrlStart = repoUrl.split("//")[0] + "//"
      repoUrlEnd = "@" + repoUrl.split("//")[1]
      repoUrlCred = repoUrlStart + pword + repoUrlEnd
      repoBranch = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'branch')
      gitCloneCommand = "git clone -b " + repoBranch + " " + repoUrlCred
      command_runner.runShellCommandInWorkingDir(gitCloneCommand, userCallingDir)
    #RETURN FAILURE QUIT IF ANY DEPENDENCY IS MISSING.  INCLUDE MESSAGE STATING WHICH DEPENDENCY IS MISSING.

  #THIS FUNCTION IS NOT USED YET.  KEEPING IT HERE FOR WHEN LOCAL TERRAFORM REGISTRIES GET MANAGED BY THIS PROCESS.
  #@private
  def writeTerraformRC(self, terraformRC):
    pathToLocalTerraformRegistry = "C:\\projects\\terraform\\providers"
    with open(terraformRC, 'w') as filetowrite:
      print("provider_installation {")
      print("  filesystem_mirror {")
      print("    path    = \""+pathToLocalTerraformRegistry+"\"")
      print("    include = [\"*/*\"]")
      print("  }")
      print("  direct {")
      print("    exclude = [\"*/*\"]")
      print("  }")
      print("}")

  #@private
  def runConfigure(self):
    self.getDependencies()
    self.checkDependencies()
    self.cloneTheSourceCode()

  #@private
  def undoConfigure(self):
    admin_path = config_cliprocessor.inputVars.get('acmAdminPath')
    self.deleteLocalCopiesOfGitRepos()
    admin_path = config_cliprocessor.inputVars.get('acmAdminPath')
    try:
      shutil.rmtree(admin_path, ignore_errors=True)
    except FileNotFoundError:
      logString = "The acmAdmin directory does not exist.  It may have already been deleted."
      log_writer.writeLogVerbose("acm", logString)
    if platform.system() == 'Linux':
      binaries_path = '/opt/acm/'
      try:
        shutil.rmtree(binaries_path, ignore_errors=True)
      except FileNotFoundError:
        logString = "The /opt/acm/ directory does not exist.  It may have already been deleted."
        log_writer.writeLogVerbose("acm", logString)
      command_runner.runShellCommandInWorkingDir("dir", '/opt')
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    callsToModulesDir = userCallingDir + command_formatter.getSlashForOS() + 'calls-to-modules'
    try:
      shutil.rmtree(callsToModulesDir, ignore_errors=True)
    except FileNotFoundError:
      logString = "The calls-to-modules directory does not exist.  It may have already been deleted."
      log_writer.writeLogVerbose("acm", logString)

  #@private
  def deleteLocalCopiesOfGitRepos(self):
    config_path = config_cliprocessor.inputVars.get('acmConfigPath')
    print('config_path is: ', config_path)
    if platform.system() == 'Linux':
      gitRemoveCmd = 'rm -rf .git'
    if platform.system() == 'Windows':
      gitRemoveCmd = 'rmdir /s /q .git'
    #Now get the names of all the repos that were imported. 
    yaml_setup_config_file_and_path = config_path +command_formatter.getSlashForOS() + "setupConfig.yaml"  
    yaml_setup_config_file_and_path = command_formatter.formatPathForOS(yaml_setup_config_file_and_path)
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    sourceRepoInstanceNames = self.getInstanceNames(yaml_setup_config_file_and_path, 'source')
    #Now delete the local copy of each imported repo.
    for sourceRepoInstance in sourceRepoInstanceNames:
      repoUrl = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'repo')
      repoUrlEnd = repoUrl.split("//")[1]
      repoName = repoUrlEnd.split('/')[-1].replace('.git','')
      repoPath = userCallingDir + command_formatter.getSlashForOS() + repoName
      #Delete the repo if it exists locally.  This handles case where repo was NOT cloned locally due to incomplete setup. 
      if os.path.exists(repoPath):
        command_runner.runShellCommandInWorkingDir(gitRemoveCmd, repoPath)
        try:
          shutil.rmtree(repoPath)
        except FileNotFoundError:
          logString = "The "+repoName+" directory does not exist.  It may have already been deleted."
          log_writer.writeLogVerbose("acm", logString)
    #No delete the acmConfig directory
    command_runner.runShellCommandInWorkingDir(gitRemoveCmd, config_path)
    try:
      shutil.rmtree(config_path)
    except FileNotFoundError:
      logString = "The acmConfig directory does not exist.  It may have already been deleted."
      log_writer.writeLogVerbose("acm", logString)

  #@private
  def getDependencyProperty(self, yamlConfigFileAndPath, typeParent, instanceName, propertyName):
    propertyValue = ''
    with open(yamlConfigFileAndPath) as f:  
      my_dict = yaml.safe_load(f)
      for key, value in my_dict.items():  
        if (typeParent == 'dependencies'):
          if key == typeParent:
            childTypes = my_dict.get(key)
            for instanceOfType in childTypes: 
              if instanceOfType.get("name") == instanceName:
                propertyValue = instanceOfType.get(propertyName)
        else:  
          logString = "The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation."
          print(logString)
    return propertyValue

  #@private
  def getDependencyVersion(self, yamlFileAndPath, dependency):
    version = ""  
    match = False  
    with open(yamlFileAndPath) as f:  
      topLevel_dict = yaml.safe_load(f)  
      for item in topLevel_dict:  
        if re.match("dependencies", item):    
          deps = topLevel_dict.get(item)  
          for dep in deps: 
            if dependency == dep.get("name"):
              version = dep.get("version")  
              match = True  
    if match == True:
      return version
    else: 
      quit("ERROR: The dependency is not listed in the config file.  Halting program so you can look for the root cause of the problem before proceeding. ")

  #@private
  def getDependencyVersionSecondLevel(self, yamlConfigFileAndPath, typeParent, instanceName, propertyName, grandChild):
    propertyValue = ''
    with open(yamlConfigFileAndPath) as f:  
      my_dict = yaml.safe_load(f)
      for key, value in my_dict.items():  
        if (typeParent == 'dependencies'):
          if key == typeParent:
            childTypes = my_dict.get(key)
            for instanceOfType in childTypes: 
              if instanceOfType.get("name") == instanceName:
                propertyValue = instanceOfType.get(propertyName)
                if type(propertyValue) is list:
                  for myListItem in propertyValue:
                    if myListItem.get('name') == grandChild:
                      propertyValue = myListItem.get('version')
                else:
                  quit("ERROR: Invalid dependency configuration in infrastructureConfig.yaml.  Halting program so you can diagnose the source of the problem.  ")
        else:  
          logString = "The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation."
          log_writer.writeLogVerbose("acm", logString)
    return propertyValue

  #@private
  def getInstanceNames(self, yamlFileAndPath, typeName):
    instanceNames = []
    with open(yamlFileAndPath) as f:  
      topLevel_dict = yaml.safe_load(f)
      for item in topLevel_dict:
        if re.match(typeName, item):
          items = topLevel_dict.get(item)
          for instance in items: 
            if type(instance) == str:
              if instance == 'instanceName':
                instanceName = items.get(instance)
                if len(instanceName) > 0:
                  instanceNames.append(instanceName)
            elif type(instance) == dict:
              instanceName = instance.get("instanceName")
              if len(instanceName) > 0:
                instanceNames.append(instanceName)
    return instanceNames

  #@private
  def getSourceCodeProperty(self, yamlConfigFileAndPath, typeParent, instanceName, propertyName):
    propertyValue = ''
    with open(yamlConfigFileAndPath) as f:  
      my_dict = yaml.safe_load(f)
      for key, value in my_dict.items():  
        if (typeParent == 'source'):
          if key == typeParent:
            childTypes = my_dict.get(key)
            for instanceOfType in childTypes: 
              if instanceOfType.get("instanceName") == instanceName:
                propertyValue = instanceOfType.get(propertyName)
        else:  
          logString = "The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation."
          log_writer.writeLogVerbose("acm", logString)
    return propertyValue

  #@private
  def getGitPassFromSourceKeys(self, sourceKeys):
    ### Get gitPass variable from the file indicated by the sourceKeys variable.  
    gitPassCount = 0
    gitPass = None
    if sourceKeys != None:
      with open(sourceKeys) as file:
        for item in file:
          itemParts = item.split(':')
          if itemParts[0].replace(' ','') == 'gitPass':
            gitPass = itemParts[1].replace(' ','')
            gitPassCount += 1
    else:
      logString = "ERROR: ACM_SOURCE_KEYS environment variable was not found."
      log_writer.writeLogVerbose("acm", logString)
      sys.exit(1)
    if gitPassCount == 0:
      logString = "ERROR: gitPass variable not found in sourceKeys file. "
      log_writer.writeLogVerbose("acm", logString)
      sys.exit(1)
    elif gitPassCount > 1:
      logString = "ERROR: Multiple values for gitPass were found in sourceKeys file.  Only one record for gitPass is allowed as input."
      log_writer.writeLogVerbose("acm", logString)
      sys.exit(1)
    elif gitPassCount == 1:
      pass
    return gitPass

  #@private
  def assembleSourceRepo(self, gitPass, sourceRepo):
    ### Assemble the URL to use to clone the repo that contains the configurtion.  
    if len(sourceRepo) == 0:
      logString = 'ERROR: sourceRepo parameter must be properly included in your command.'
      log_writer.writeLogVerbose("acm", logString)
      sys.exit(1)
    if sourceRepo[0:8] != 'https://':
      logString = 'ERROR: the sourceRepo parameter must begin with https://'
      log_writer.writeLogVerbose("acm", logString)
      sys.exit(1)
    else:
      if gitPass != None:
        sourceRepo = 'https://'+gitPass.strip()+'@'+sourceRepo[8:].strip()
    return sourceRepo

  #@private
  def assembleCloneCommand(self, sourceRepo):
    repoBranch = config_cliprocessor.inputVars.get('repoBranch')
    if len(repoBranch) == 0:
      branchPart = ''
    else:
      branchPart = ' --branch '+repoBranch+' '
    cloneCommand = 'git clone '+branchPart+sourceRepo
    return cloneCommand

  #@public
  def runSetup(self):
    addExtensionCommand = 'az extension add --name azure-devops'
    command_runner.runShellCommandForTests(addExtensionCommand)
    addAccountExtensionCommand = 'az extension add --upgrade -n account'
    command_runner.runShellCommandForTests(addAccountExtensionCommand)
    self.createDirectoryStructure()
    sourceKeys = config_cliprocessor.inputVars.get('sourceKeys') + command_formatter.getSlashForOS() + 'keys.yaml'
    gitPass = self.getGitPassFromSourceKeys(sourceKeys)
    sourceRepo = config_cliprocessor.inputVars.get('sourceRepo')
    sourceRepo = self.assembleSourceRepo(gitPass, sourceRepo)
    cloneCommand = self.assembleCloneCommand(sourceRepo)
    command_runner.runShellCommand(cloneCommand)
    sourceRepoDestinationDir = sourceRepo.split('/')[-1].replace('.git','')
    sourceRepoDestinationDir = config_cliprocessor.inputVars.get('userCallingDir') + sourceRepoDestinationDir
    sourceRepoDestinationDir = command_formatter.formatPathForOS(sourceRepoDestinationDir)
    acmConfigPath = config_cliprocessor.inputVars.get('acmConfigPath')
    acmConfigPath = command_formatter.formatPathForOS(acmConfigPath)
    os.rename(sourceRepoDestinationDir, acmConfigPath)
    keysStarterPath = config_cliprocessor.inputVars.get('dirOfYamlKeys')
    destinationKeys = keysStarterPath +command_formatter.getSlashForOS()+'keys.yaml'
    shutil.copy(sourceKeys, destinationKeys)
    self.runConfigure()

  #@public
  def undoSetup(self):
    self.undoConfigure()

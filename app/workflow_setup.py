## Copyright 2023 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

from command_runner import command_runner 
from command_formatter import command_formatter
from config_fileprocessor import config_fileprocessor 
from log_writer import log_writer

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

  ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

  #@private
  def createDirectoryStructure(self):
    import config_cliprocessor
    crnr = command_runner()
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
        crnr.runShellCommand(binariesCommand)

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
        crnr.runShellCommand(logsCommand)
        print('logsPath is: ', str(logsPath))

    print('Contents of acmAdmin directory are: ')
    for item in os.listdir(adminPath):
      print('... ', item)

    print('Contents of keys directory are: ')
    for item in os.listdir(keysPath):
      print('... ', item)
 
  #@private
  def downloadAndExtractBinary(self, url, dependencies_binaries_path):
    lw = log_writer()
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
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    os.remove(file_name)

  #@private
  def getDependencies(self):
    import config_cliprocessor
    crnr = command_runner()
    cfmtr = command_formatter()
    configPath = config_cliprocessor.inputVars.get('acmConfigPath') 
    yaml_setup_config_file_and_path = configPath + cfmtr.getSlashForOS() + "setupConfig.yaml"
    yaml_setup_config_file_and_path = cfmtr.formatPathForOS(yaml_setup_config_file_and_path)
    dependencies_binaries_path = config_cliprocessor.inputVars.get('dependenciesBinariesPath')
    dependencies_binaries_path = cfmtr.formatPathForOS(dependencies_binaries_path)
    if platform.system() == "Windows":
      propName = "download-link-windows"
    else:
      propName = "download-link-linux"
    dependenciesList = self.getDependenciesList(yaml_setup_config_file_and_path)
    for dependency in dependenciesList:
      if dependency == "azure-cli":
        addExtensionCommand = 'az extension add --name azure-devops'
        crnr.runShellCommandForTests(addExtensionCommand)
        addAccountExtensionCommand = 'az extension add --upgrade -n account'
        crnr.runShellCommandForTests(addAccountExtensionCommand)
      elif dependency == "terraform":
        url_terraform = self.getDependencyProperty(yaml_setup_config_file_and_path, "dependencies", "terraform", propName)
        self.downloadAndExtractBinary(url_terraform, dependencies_binaries_path)
        if platform.system() == 'Linux':
          fullyQualifiedPath = dependencies_binaries_path + 'terraform'
          myCmd = 'chmod +x ' + fullyQualifiedPath
          crnr.runShellCommand(myCmd)
      elif dependency == "packer":
        url_packer = self.getDependencyProperty(yaml_setup_config_file_and_path, "dependencies", "packer", propName)
        self.downloadAndExtractBinary(url_packer, dependencies_binaries_path)
        if platform.system() == 'Linux':
          fullyQualifiedPath = dependencies_binaries_path + 'packer'
          myCmd = 'chmod +x ' + fullyQualifiedPath
          crnr.runShellCommand(myCmd)

  #@private
  def checkDependencies(self):
    failedCheck = False
    import config_cliprocessor
    crnr = command_runner()
    cfmtr = command_formatter()
    lw = log_writer()
    logString = "Checking to see if required dependencies are installed..."
    lw.writeLogVerbose("acm", logString)
    configPath = config_cliprocessor.inputVars.get('acmConfigPath')
    yaml_setup_config_file_and_path = configPath +cfmtr.getSlashForOS() + "setupConfig.yaml"  
    yaml_setup_config_file_and_path = cfmtr.formatPathForOS(yaml_setup_config_file_and_path)
    dependencies_binaries_path = config_cliprocessor.inputVars.get('dependenciesBinariesPath')
    dependencies_binaries_path = cfmtr.formatPathForOS(dependencies_binaries_path)
    dependenciesList = self.getDependenciesList(yaml_setup_config_file_and_path)
    for dependency in dependenciesList:
      if dependency == "terraform":
        #Terraform
        tfVers = self.getDependencyVersion(yaml_setup_config_file_and_path, 'terraform')
        if tfVers.count('.') == 1:
          tfVers = 'v' + tfVers + '.'
        else:
          logString = 'ERROR: The value you entered for terraform version in acm.yaml is not valid.  Only the first two blocks are accepted, as in \"x.y\" '
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
        tfCheck = None
        tfDependencyCheckCommand = dependencies_binaries_path + "terraform --version"
        tfResult = crnr.checkIfInstalled(tfDependencyCheckCommand, tfVers)
        if 'Dependency is installed' in tfResult:
          tfCheck = True
        if 'NOT installed' in tfResult:
          tfCheck = False
          failedCheck = True
        #ADD CHECK FOR SUCCESS TO MAKE TRUE
      elif dependency == "packer":
        #packer
        pkrVers = self.getDependencyVersion(yaml_setup_config_file_and_path, 'packer')
        if pkrVers.count('.') != 1:
          logString = 'ERROR: The value you entered for packer version in acm.yaml is not valid.  Only the first two blocks are accepted, as in \"x.y\" '
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
        if pkrVers.count('.') == 1:
          pkrVers = pkrVers + '.'
        pkrCheck = None
        pkrDependencyCheckCommand = dependencies_binaries_path + "packer --version"
        pkrResult = crnr.checkIfInstalled(pkrDependencyCheckCommand, pkrVers)
        if 'Dependency is installed' in tfResult:
          pkrCheck = True
        if 'NOT installed' in pkrResult:
          pkrCheck = False
          failedCheck = True
        #ADD CHECK FOR SUCCESS TO MAKE TRUE
      elif dependency == "azure-cli":
        #Azure CLI
        azVers = self.getDependencyVersion(yaml_setup_config_file_and_path, 'azure-cli')
        azCheck = None
        azDependencyCheckCmd = "az version"
        azResult = crnr.checkIfAzInstalled(azDependencyCheckCmd, azVers)
        if 'Dependency is installed' in azResult:
          azCheck = True
        if 'NOT installed' in azResult:
          azCheck = False
          failedCheck = True
        #ADD CHECK FOR SUCCESS TO MAKE TRUE
        #Azure-Devops CLI extension
        azdoVers = self.getDependencyVersionSecondLevel(yaml_setup_config_file_and_path, 'dependencies', 'azure-cli', 'modules', 'azure-cli-ext-azure-devops')
        azdoCheck = None
        azDependencyCheckCmd = "az version"
        azdoResult = crnr.checkIfAzdoInstalled(azDependencyCheckCmd, azdoVers)
        if 'Dependency is installed' in azdoResult:
          azdoCheck = True
        if 'NOT installed' in azdoResult:
          azdoCheck = False
          failedCheck = True
        #ADD CHECK FOR SUCCESS TO MAKE TRUE
      elif dependency == "git":
        #git check
        gitVers = self.getDependencyVersion(yaml_setup_config_file_and_path, 'git')
        if gitVers.count('.') != 0:
          logString = 'ERROR: The value you entered for git version in acm.yaml is not valid.  Only the first block is accepted, as in \"x\" '
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
        if gitVers.count('.') == 0:
          gitVers = gitVers + '.'
        gitCheck = None
        gitDependencyCheckCommand = "git --version"
        gitResult = crnr.checkIfInstalled(gitDependencyCheckCommand, gitVers)
        if 'Dependency is installed' in gitResult:
          gitCheck = True
        if 'NOT installed' in gitResult:
          gitCheck = False
          failedCheck = True
        #ADD CHECK FOR SUCCESS TO MAKE TRUE
      elif dependency == "aws-cli":
        awsVers = self.getDependencyVersion(yaml_setup_config_file_and_path, 'aws-cli')
        awsCheck = None
        awsDependencyCheckCmd = "aws --version"
        awsResult = crnr.checkIfAwsInstalled(awsDependencyCheckCmd, awsVers)
        if 'Dependency is installed' in awsResult:
          awsCheck = True
        if 'NOT installed' in awsResult:
          awsCheck = False
          failedCheck = True

    logString = "-------------------------------------------------------------------------"
    lw.writeLogVerbose("acm", logString)
    if self.getIfDependencyIsInList(yaml_setup_config_file_and_path, "azure-cli"):
      if azCheck == True:
        azCheckPassStr = "az cli version " + azVers + ":                              INSTALLED"
        logString = azCheckPassStr
        lw.writeLogVerbose("acm", logString)
      elif (azCheck == False) or (azCheck == None):
        azCheckFailStr = "az cli version " + azVers + ":                              MISSING"
        logString = azCheckFailStr
        lw.writeLogVerbose("acm", logString)
      if azdoCheck == True:
        azdoCheckPassStr = "azure-devops extension version " + azdoVers + " for az cli:   INSTALLED"
        logString = azdoCheckPassStr
        lw.writeLogVerbose("acm", logString)
      elif (azCheck == False) or (azCheck == None):
        azdoCheckFailStr = "azure-devops extension version " + azdoVers + " for az cli:   MISSING"
        logString = azdoCheckFailStr
        lw.writeLogVerbose("acm", logString)
    if self.getIfDependencyIsInList(yaml_setup_config_file_and_path, "git"):
      if gitCheck == True:
        gitCheckPassStr = "git version " + gitVers + ":                                INSTALLED"
        logString = gitCheckPassStr
        lw.writeLogVerbose("acm", logString)
      elif (gitCheck == False) or (gitCheck == None):
        gitCheckFailStr = "git version " + gitVers + ":                                MISSING"
        logString = gitCheckFailStr
        lw.writeLogVerbose("acm", logString)
    if self.getIfDependencyIsInList(yaml_setup_config_file_and_path, "terraform"):
      if tfCheck == True:
        tfCheckPassStr = "terraform version " + tfVers + ":                         INSTALLED"
        logString = tfCheckPassStr
        lw.writeLogVerbose("acm", logString)
      elif (tfCheck == False) or (tfCheck == None):
        tfCheckFailStr = "terraform version " + tfVers + ":                         MISSING"
        logString = tfCheckFailStr
        lw.writeLogVerbose("acm", logString)
    if self.getIfDependencyIsInList(yaml_setup_config_file_and_path, "packer"):
      if pkrCheck == True:
        pkrCheckPassStr = "packer version " + pkrVers + ":                              INSTALLED"
        logString = pkrCheckPassStr
        lw.writeLogVerbose("acm", logString)
      elif (pkrCheck == False) or (pkrCheck == None):
        pkrCheckFailStr = "packer version " + pkrVers + ":                              MISSING"
        logString = pkrCheckFailStr
        lw.writeLogVerbose("acm", logString)

    if self.getIfDependencyIsInList(yaml_setup_config_file_and_path, "aws-cli"):
      if awsCheck == True:
        awsCheckPassStr = "aws cli version " + awsVers + ":                              INSTALLED"
        logString = awsCheckPassStr
        lw.writeLogVerbose("acm", logString)
      elif (awsCheck == False) or (awsCheck == None):
        awsCheckFailStr = "aws cli version " + awsVers + ":                              MISSING"
        logString = awsCheckFailStr
        lw.writeLogVerbose("acm", logString)

    logString = "-------------------------------------------------------------------------"
    lw.writeLogVerbose("acm", logString)
    if failedCheck == True:
      logString = "ERROR:  Your system is missing one or more of the dependencies listed above.  Please make sure that the dependencies are properly installed and then re-run the setup on command. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)

  #@private
  def cloneTheSourceCode(self):
    import config_cliprocessor 
    crnr = command_runner()
    cfmtr = command_formatter()
    configPath = config_cliprocessor.inputVars.get('acmConfigPath') 
    yaml_setup_config_file_and_path = configPath +cfmtr.getSlashForOS() + "setupConfig.yaml"  
    yaml_setup_config_file_and_path = cfmtr.formatPathForOS(yaml_setup_config_file_and_path)
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    sourceRepoInstanceNames = self.getInstanceNames(yaml_setup_config_file_and_path, 'source')
    acmAdmin = userCallingDir + cfmtr.getSlashForOS() + 'acmAdmin'
    acmAdmin = cfmtr.formatPathForOS(acmAdmin)
    for sourceRepoInstance in sourceRepoInstanceNames: 
      repoUrl = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'repo')
      self.validateRepoStrings('repo', repoUrl)
      public = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'public')
      self.validateRepoStrings('public', public)
      repoBranch = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'branch')
      self.validateRepoStrings('branch', repoBranch)


      if (public != "true") and (public != "True"):
        repoUrlCred = self.assembleSourceRepo(repoUrl)
      else:
        repoUrlCred = repoUrl
      gitCloneCommand = "git clone -b " + repoBranch + " " + repoUrlCred  
      crnr.runShellCommandInWorkingDir(gitCloneCommand, userCallingDir)
      #Start the API if repo is an API
      apiBool = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'api')
      print("apiBool is: ", apiBool)
      print("type(apiBool) is: ", type(apiBool))
      if (apiBool != None):
        if (isinstance(apiBool, bool)):
          if apiBool: 
            setupScript = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'setupScript')
            #shutdownScript = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'shutdownScript')
            if setupScript.endswith(".py"):
              repoFolderName = repoUrl.split("/")[-1].replace(".git","")
              repoFolderAndPath = userCallingDir + cfmtr.getSlashForOS() + repoFolderName
              #setupCommand = "python "+setupScript #Commenting this line because linux could not find setupScript even though windows could
              setupCommand = "python "+repoFolderAndPath+cfmtr.getSlashForOS()+setupScript
              #self.runShellCommandInWorkingDir(setupCommand, repoFolderAndPath)
              os.chdir(repoFolderAndPath)
              print("os.getcwd() is: ", str(os.getcwd()))
              print("repoFolderAndPath is: ", str(repoFolderAndPath))
              print("About to list contents of repoFolderAndPath. ")
              from pathlib import Path
              print(*Path(str(repoFolderAndPath)).iterdir(), sep="\n")
              import subprocess
              #stream = subprocess.Popen(setupCommand, stdout=subprocess.DEVNULL) #This line works on windows, but not on linux.
              stream = subprocess.Popen(setupCommand, stdout=subprocess.DEVNULL, cwd=str(repoFolderAndPath))
            else:
              logString = "ERROR: The setup script name does not end in '.py'.  If you require support for scripts in other languages besides python, please either submit a feature request describing your requirements, or a pull request with the solution you suggest.  "
              print(logString)
              exit(1)
        else:
          logString = "ERROR: Value for the 'api' field must be a boolean if the 'api' field is used."
          print(logString)
          exit(1)
#        quit("mnbvcxz BREAKPOINT")

    #RETURN FAILURE QUIT IF ANY DEPENDENCY IS MISSING.  INCLUDE MESSAGE STATING WHICH DEPENDENCY IS MISSING.

  def validateRepoStrings(self, fieldName, obj_to_test):
    if fieldName == "public":
      if isinstance(obj_to_test, bool):
        return
    else:
      if not isinstance(obj_to_test, str):
        print("ERROR: Value for ", fieldName, " is not a string.  ")
        quit()
      if len(obj_to_test)<2:
        print("ERROR: value of ", fieldName, " must be a valid string value at least 2 characters long.")
        quit()

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
    import config_cliprocessor
    print("minSetup is: ", str(config_cliprocessor.inputVars.get('minSetup')))
    if config_cliprocessor.inputVars.get('minSetup') != True:
      self.cloneTheSourceCode()

  #@private
  def undoConfigure(self):
    import config_cliprocessor
    crnr = command_runner()
    cfmtr = command_formatter()
    lw = log_writer()

    #Destroy the acmAdmin directory, and then destroy the binaries location if linux
    admin_path = config_cliprocessor.inputVars.get('acmAdminPath')
    try:
      shutil.rmtree(admin_path, ignore_errors=True)
    except FileNotFoundError:
      logString = "The acmAdmin directory does not exist.  It may have already been deleted."
      lw.writeLogVerbose("acm", logString)
    if platform.system() == 'Linux':
      binaries_path = '/opt/acm/'
      try:
        shutil.rmtree(binaries_path, ignore_errors=True)
      except FileNotFoundError:
        logString = "The /opt/acm/ directory does not exist.  It may have already been deleted."
        lw.writeLogVerbose("acm", logString)
      crnr.runShellCommandInWorkingDir("dir", '/opt')

    #Delete the location where the terraform controller placed the calls to modules.  
    #Note this might be the wrong location because these are probably put in the building blocks folder.  
    # Also note that .gitignore in the actual location in the building blocks folder should keep these out of version control.  
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    callsToModulesDir = userCallingDir + cfmtr.getSlashForOS() + 'calls-to-modules'
    try:
      shutil.rmtree(callsToModulesDir, ignore_errors=True)
    except FileNotFoundError:
      logString = "The calls-to-modules directory does not exist.  It may have already been deleted."
      lw.writeLogVerbose("acm", logString)

    print("minSetup is: ", str(config_cliprocessor.inputVars.get('minSetup')))
    #quit("vbnmnbvcqwertyytrewq")
    if config_cliprocessor.inputVars.get('minSetup') != True:
      #Delete the local copies of the repos you cloned to create this instance
      self.deleteLocalCopiesOfGitRepos()

  #@private
  def deleteLocalCopiesOfGitRepos(self):
    import config_cliprocessor
    crnr = command_runner()
    cfmtr = command_formatter()
    lw = log_writer()
    config_path = config_cliprocessor.inputVars.get('acmConfigPath')
    if platform.system() == 'Linux':
      gitRemoveCmd = 'rm -rf .git'
    if platform.system() == 'Windows':
      gitRemoveCmd = 'rmdir /s /q .git'
    #Now get the names of all the repos that were imported. 
    yaml_setup_config_file_and_path = config_path +cfmtr.getSlashForOS() + "setupConfig.yaml"  
    yaml_setup_config_file_and_path = cfmtr.formatPathForOS(yaml_setup_config_file_and_path)
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    sourceRepoInstanceNames = self.getInstanceNames(yaml_setup_config_file_and_path, 'source')
    #Now delete the local copy of each imported repo.
    for sourceRepoInstance in sourceRepoInstanceNames:
      repoUrl = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'repo')
      repoUrlEnd = repoUrl.split("//")[1]
      repoName = repoUrlEnd.split('/')[-1].replace('.git','')
      repoPath = userCallingDir + cfmtr.getSlashForOS() + repoName
#//start stuff to clean up
      #Start the API if repo is an API
      apiBool = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'api')
      print("apiBool is: ", apiBool)
      print("type(apiBool) is: ", type(apiBool))
      if (apiBool != None):
        if (isinstance(apiBool, bool)):
          if apiBool: 
            #setupScript = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'setupScript')
            shutdownScript = self.getSourceCodeProperty(yaml_setup_config_file_and_path, 'source', sourceRepoInstance, 'shutdownScript')
            if shutdownScript.endswith(".py"):
              repoFolderName = repoUrl.split("/")[-1].replace(".git","")
              repoFolderAndPath = userCallingDir + cfmtr.getSlashForOS() + repoFolderName
              shutdownCommand = "python "+shutdownScript
              self.runShellCommandInWorkingDir(shutdownCommand, repoFolderAndPath)
              #os.chdir(repoFolderAndPath)
              #import subprocess
              #stream = subprocess.Popen(setupCommand, stdout=subprocess.DEVNULL)
            else:
              logString = "ERROR: The shutdown script name does not end in '.py'.  If you require support for scripts in other languages besides python, please either submit a feature request describing your requirements, or a pull request with the solution you suggest.  "
              print(logString)
              exit(1)
        else:
          print("sourceRepoInstance is: ", sourceRepoInstance)
          logString = "ERROR: Value for the 'api' field must be a boolean if the 'api' field is used."
          print(logString)
          exit(1)
#//end stuff to clean up
      #Delete the repo if it exists locally.  This handles case where repo was NOT cloned locally due to incomplete setup. 
      if os.path.exists(repoPath):
        crnr.runShellCommandInWorkingDir(gitRemoveCmd, repoPath)
        try:
          shutil.rmtree(repoPath)
        except FileNotFoundError:
          logString = "The "+repoName+" directory does not exist.  It may have already been deleted."
          lw.writeLogVerbose("acm", logString)
    #No delete the acmConfig directory
    crnr.runShellCommandInWorkingDir(gitRemoveCmd, config_path)
    try:
      shutil.rmtree(config_path)
    except FileNotFoundError:
      logString = "The acmConfig directory does not exist.  It may have already been deleted."
      lw.writeLogVerbose("acm", logString)

  #@private
  def getDependenciesList(self, yamlConfigFileAndPath):
    dependenciesList = []
    with open(yamlConfigFileAndPath) as f:  
      my_dict = yaml.safe_load(f)
      for key, value in my_dict.items():  
        if key == "dependencies":
          childTypes = my_dict.get(key)
          for instanceOfType in childTypes: 
            dependenciesList.append(instanceOfType.get("name"))
    return dependenciesList

  #@private
  def getIfDependencyIsInList(self, yamlConfigFileAndPath, dependencyName):
    isInList = False
    with open(yamlConfigFileAndPath) as f:  
      my_dict = yaml.safe_load(f)
      for key, value in my_dict.items():  
        if key == "dependencies":
          childTypes = my_dict.get(key)
          for instanceOfType in childTypes: 
            if instanceOfType.get('name') == dependencyName:
              isInList = True
    return isInList


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
      print("ERROR: The dependency is not listed in the config file.  Halting program so you can look for the root cause of the problem before proceeding. ")
      sys.exit(1)

  #@private
  def getDependencyVersionSecondLevel(self, yamlConfigFileAndPath, typeParent, instanceName, propertyName, grandChild):
    lw = log_writer()
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
                  print("ERROR: Invalid dependency configuration in acm.yaml.  Halting program so you can diagnose the source of the problem.  ")
                  sys.exit(1)
        else:  
          logString = "The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation."
          lw.writeLogVerbose("acm", logString)
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
    lw = log_writer()
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
          lw.writeLogVerbose("acm", logString)
    return propertyValue

  #@private
  def getGitPassFromSourceKeys(self, sourceKeys):
    lw = log_writer()
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
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    if gitPassCount == 0:
      logString = "ERROR: gitPass variable not found in sourceKeys file. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    elif gitPassCount > 1:
      logString = "ERROR: Multiple values for gitPass were found in sourceKeys file.  Only one record for gitPass is allowed as input."
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    elif gitPassCount == 1:
      pass
    return gitPass

  #@private
  def assembleSourceRepo(self, sourceRepo):
    import config_cliprocessor
    cfmtr = command_formatter()
    cfp = config_fileprocessor()
    keysStarterPath = config_cliprocessor.inputVars.get('dirOfYamlKeys')
    destinationKeys = keysStarterPath +cfmtr.getSlashForOS()+'keys.yaml'
    repoUrlStart = sourceRepo.split("//")[0] + "//"
    repoUrlEnd = "@" + sourceRepo.split("//")[1]
    gitProvider = sourceRepo.split("//")[1].split(".")[0]
    if gitProvider == "github":
      pword = cfp.getFirstLevelValue(destinationKeys, 'gitPass')
      repoUrlCred = repoUrlStart + pword + repoUrlEnd
    elif gitProvider == "gitlab":
      pword = cfp.getFirstLevelValue(destinationKeys, 'gitlabPAT')
      usr = cfp.getFirstLevelValue(destinationKeys, 'gitlabUser')
      repoUrlCred = repoUrlStart + usr + ":" + pword + repoUrlEnd
    elif gitProvider == "dev":
      if sourceRepo.split("//")[1].split(".")[1] == "azure":
        pword = cfp.getFirstLevelValue(destinationKeys, 'azdoPAT')
        repoUrlCred = repoUrlStart + pword + repoUrlEnd
      else:
        secondPart = sourceRepo.split("//")[1].split(".")[1]
        errorMessage = "ERROR: Your git provider "+gitProvider+"."+secondPart+" is not one of the currently supported options: github, gitlab, dev.azure. Place a feature request at the GitHub repo for this project requesting support for your additional git provider and we would be happy to reply.  "
        print(errorMessage)
        quit()
    else:
      errorMessage = "ERROR: Your git provider "+gitProvider+" is not one of the currently supported options: github, gitlab, dev.azure. Please submit a feature request at the GitHub repo for this project requesting support for your additional git provider and we would be happy to reply.  "
      print(errorMessage)
      quit()
    return repoUrlCred


  #@private
  def assembleCloneCommand(self, sourceRepo):
    import config_cliprocessor
    repoBranch = config_cliprocessor.inputVars.get('repoBranch')
    if len(repoBranch) == 0:
      branchPart = ''
    else:
      branchPart = ' --branch '+repoBranch+' '
    cloneCommand = 'git clone '+branchPart+sourceRepo
    return cloneCommand
 
  #@public
  def runSetup(self):
    import config_cliprocessor
    crnr = command_runner()
    cfmtr = command_formatter()
    self.createDirectoryStructure()
    print("minSetup is: ", str(config_cliprocessor.inputVars.get('minSetup')))
    #quit("vbnmnbvcqwertyytrewq")
    if config_cliprocessor.inputVars.get('minSetup') != True:
      sourceRepo = config_cliprocessor.inputVars.get('sourceRepo') 
      public = config_cliprocessor.inputVars.get('repoPublic')
      if (public != "true") and (public != "True"):
        sourceRepo = self.assembleSourceRepo(sourceRepo)
      cloneCommand = self.assembleCloneCommand(sourceRepo)
      crnr.runShellCommand(cloneCommand) 
      sourceRepoDestinationDir = sourceRepo.split('/')[-1].replace('.git','')
      sourceRepoDestinationDir = config_cliprocessor.inputVars.get('userCallingDir') + sourceRepoDestinationDir
      sourceRepoDestinationDir = cfmtr.formatPathForOS(sourceRepoDestinationDir)
      acmConfigPath = config_cliprocessor.inputVars.get('acmConfigPath')
      acmConfigPath = cfmtr.formatPathForOS(acmConfigPath)
      import time
      time.sleep(15)
      os.rename(sourceRepoDestinationDir, acmConfigPath)
    self.runConfigure()

  #@public
  def undoSetup(self):
    self.undoConfigure()
    lw = log_writer()
    logString = "Finished running acm setup off"
    lw.writeLogVerbose("acm", logString)

  #@public
  def runShellCommandInWorkingDir(self, commandToRun, workingDir):
    import subprocess
    lw = log_writer()
    proc = subprocess.Popen( commandToRun,cwd=workingDir, stdout=subprocess.PIPE, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=self.ansi_escape.sub('', thetext)
        logString = decodedline
        lw.writeLogVerbose("shell", logString)
      else:
        break

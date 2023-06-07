## Copyright 2023 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

import fileinput 
import sys
import platform
import os
from pathlib import Path
from distutils.dir_util import copy_tree
import shutil
import subprocess
import re

from log_writer import log_writer
from command_formatter import command_formatter
from controller_azureadmin import controller_azureadmin
from controller_azdoproject import controller_azdoproject

class controller_terraform:

  tfOutputDict = {}
  foundationApply = True
  ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
  terraformResult = ''

  def __init__(self):  
    pass
 
  #@public
  def terraformCrudOperation(self, operation, keyDir, systemConfig, instance, typeParent, typeName, typeGrandChild, typeInstanceName):
    import config_cliprocessor
    myLogWriter = log_writer()
    myCmdFormatter = command_formatter()
    if "foundation" in systemConfig.keys():
      foundationInstanceName = systemConfig.get("foundation").get("instanceName")
    else:
      foundationInstanceName = "nof"
    #1. Set variable values
    if typeName == "networkFoundation":
      templateName = systemConfig.get("foundation").get("templateName")
      instanceName = systemConfig.get("foundation").get("instanceName")
    else:
      for thisInstance in systemConfig.get("serviceTypes").get(typeName).get("instances"):
        if thisInstance.get("instanceName") == typeInstanceName:
          templateName = thisInstance.get("templateName")
          instanceName = thisInstance.get("instanceName")
    dynamicVarsPath = config_cliprocessor.inputVars.get('dynamicVarsPath')
    oldTfStateName = self.getBackedUpStateFileName(dynamicVarsPath, foundationInstanceName, templateName, instanceName)
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    relative_path_to_instances =  config_cliprocessor.inputVars.get('relativePathToInstances')
    path_to_application_root = ''
    repoName = templateName.split('/')[0]
    if templateName.count('/') == 2:
      nameParts = templateName.split("/")
      if (len(nameParts[0]) > 1) and (len(nameParts[1]) >1) and (len(nameParts[2]) > 1):
        relative_path_to_instances = nameParts[0] + '\\' + nameParts[1] + relative_path_to_instances  
        template_Name = nameParts[2]  
        path_to_application_root = userCallingDir + nameParts[0] + "\\" + nameParts[1] + "\\"
      else:
        logString = 'ERROR: templateName is not valid. '
        myLogWriter.writeLogVerbose("acm", logString)
        sys.exit(1)
    else:
      logString = "Template name "+templateName+" is not valid.  Must have only one /.  "
      myLogWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
    relative_path_to_instances = myCmdFormatter.formatPathForOS(relative_path_to_instances)
    path_to_application_root = myCmdFormatter.formatPathForOS(path_to_application_root)
    relativePathToInstance = relative_path_to_instances + template_Name + "\\"
    destinationCallParent = myCmdFormatter.convertPathForOS(userCallingDir, relativePathToInstance)
    #2. Then second instantiate call to module
    destinationCallInstance = self.instantiateCallToModule(systemConfig, keyDir, foundationInstanceName, typeName, repoName, instanceName, template_Name, oldTfStateName)
    if os.path.exists(destinationCallInstance) and os.path.isdir(destinationCallInstance):
      #3. Then third assemble and run command
      self.assembleAndRunCommand(systemConfig, instance, operation, instanceName, destinationCallInstance, typeName)
      logString = "The terraform command was assembled and run.  "
      myLogWriter.writeLogVerbose("acm", logString)
      if self.terraformResult == "Destroyed": 
        logString = "Destroy operation succeeded.  "
        myLogWriter.writeLogVerbose("acm", logString)
      elif self.terraformResult == "Applied": 
        if (typeParent == "systems") and (typeName == "projects") and (typeGrandChild is None) and (operation != "output"):
          myAzdoProjectCtrlr = controller_azdoproject()
          logString = "Terraform operation succeeded for project.  But now about to import code into the repository.  "
          myLogWriter.writeLogVerbose("acm", logString)
          myAzdoProjectCtrlr.importCodeIntoRepo(keyDir, instance, self)
        logString = "Apply operation succeeded.  "
        myLogWriter.writeLogVerbose("acm", logString)
      elif operation == "output":
        logString = "terraform output operation completed.  This code does not currently check for errors, so continuing.  If you find downstream errors, remember to check the terraform output as one possible cause."
        myLogWriter.writeLogVerbose("acm", logString)
      else:
        logString = "Terraform operation failed.  Quitting program here so you can debug the source of the problem.  "
        myLogWriter.writeLogVerbose("acm", logString)
        sys.exit(1)
      #4. Then fourth off each instance of the calls to the modules in local agent file system
      doCleanup = self.setDoCleanUp(operation)
      if(doCleanup):
        logString = "Inside conditional block of things to do if operation completed: ", operation
        myLogWriter.writeLogVerbose("acm", logString)
        key_source = config_cliprocessor.inputVars.get('keySource')
        if (typeName == 'admin'): 
          myAzAdminController = controller_azureadmin()
          myAzAdminController.cleanUp(operation, systemConfig, instance, typeName, instanceName, destinationCallInstance, self)
        self.cleanupAfterOperation(destinationCallInstance, destinationCallParent, foundationInstanceName, templateName, instanceName, key_source)
      else:   
        logString = "-------------------------------------------------------------------------------------------------------------------------------"
        myLogWriter.writeLogVerbose("acm", logString)
        logString = "ERROR: Failed to off this instance named: " + instanceName + ".  Halting program here so you can examine what went wrong and fix the problem before re-running the program. "
        myLogWriter.writeLogVerbose("acm", logString)
        sys.exit(1)
    else:  
      logString = "The instance specified as \"" + instanceName + "\" does not have any corresponding call to a module that might manage it.  Either it does not exist or it is outside the scope of this program.  Specifically, the following directory does not exist: " + destinationAutoScalingSubnetCallInstance + "  Therefore, we are not processing the request to remove the instance named: \"" + instanceName + "\""
      myLogWriter.writeLogVerbose("acm", logString)
      sys.exit(1)

  #@private
  def getBackedUpStateFileName(self, absPath, foundationInstance, templateNm, instanceNm):
    myCmdFormatter = command_formatter()
    template_name = templateNm.replace('/', '__')
    backedUpStateFileName = absPath + '\\terraform_tfstate_' + foundationInstance + '-' + template_name + '-' + instanceNm + '.backup'
    backedUpStateFileName = myCmdFormatter.formatPathForOS(backedUpStateFileName)
    return backedUpStateFileName

  #@private
  def instantiateCallToModule(self, systemConfig, keyDir, foundationInstanceName, typeName, repoName, instanceName, templateName, oldTfStateName):
    import config_cliprocessor
    myLogWriter = log_writer()
    myCmdFormatter = command_formatter()
    if (foundationInstanceName is None) or (len(foundationInstanceName)==0):
      foundationInstanceName = "nof"
    relativePathTemplate = myCmdFormatter.getSlashForOS() + "calls-to-modules" + myCmdFormatter.getSlashForOS() + "templates" + myCmdFormatter.getSlashForOS() + templateName + myCmdFormatter.getSlashForOS()
    if templateName == 'network-foundation':
      relativePathInstance = myCmdFormatter.getSlashForOS() + "calls-to-modules" + myCmdFormatter.getSlashForOS() + "instances" + myCmdFormatter.getSlashForOS() + templateName + myCmdFormatter.getSlashForOS() +foundationInstanceName+"-" + templateName + myCmdFormatter.getSlashForOS()  
      keyFile = foundationInstanceName + "-" + templateName  
    else:
      relativePathInstance = myCmdFormatter.getSlashForOS() + "calls-to-modules" + myCmdFormatter.getSlashForOS() + "instances" + myCmdFormatter.getSlashForOS() + templateName + myCmdFormatter.getSlashForOS() +foundationInstanceName+"-"+instanceName+"-" + templateName + myCmdFormatter.getSlashForOS()
      keyFile = foundationInstanceName + "-" + instanceName + "-" + templateName  
    keyFile = myCmdFormatter.formatPathForOS(keyFile)
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')+myCmdFormatter.getSlashForOS()
    pathToTemplate = userCallingDir+repoName+myCmdFormatter.getSlashForOS()+'terraform'+myCmdFormatter.getSlashForOS()
    sourceOfCallTemplate = myCmdFormatter.convertPathForOS(pathToTemplate, relativePathTemplate)
    destinationCallInstance = myCmdFormatter.convertPathForOS(pathToTemplate, relativePathInstance)
    remoteBackend = False
    templateFileAndPath = sourceOfCallTemplate + "main.tf"
    if os.path.isfile(templateFileAndPath):
      with open(templateFileAndPath) as f:
        for line in f:
          if 'backend \"' in line:
            if line[0] != "#":
              remoteBackend = True
    if remoteBackend == True:  
      oldTfStateName = "remoteBackend"
    if platform.system() == 'Windows':
      if len(destinationCallInstance) >135:
        logString = "destinationCallInstance path is too long at: " + destinationCallInstance
        myLogWriter.writeLogVerbose("acm", logString)
        logString = "ERROR: The path of the directory into which you are placing the call to the terraform module is greater than 135 characters and is thus too long.  Halting program with this meaningful message so that you can avoid receiving an unhelpful message from the program vendor.  Please shorten the length of the path and re-run.  You can either move your app higher up in the directory structure such as C:\\x\\yourApp , or you can change your config by shortening the template names and instance names that are fed into this path definition. "
        myLogWriter.writeLogVerbose("acm", logString)
        sys.exit(1)
    p = Path(destinationCallInstance)
    if p.exists():
      logString = "The instance of the call to module already exists."
      myLogWriter.writeLogVerbose("acm", logString)
    else:
      newPointerLineWindows="  source = \"..\\\..\\\..\\\..\\\modules\\\\" + templateName + "\""
      self.createCallDirectoryAndFile(sourceOfCallTemplate, destinationCallInstance, newPointerLineWindows, oldTfStateName)
    self.initializeTerraformBackend(systemConfig, keyDir, typeName, destinationCallInstance, remoteBackend, instanceName)
    return destinationCallInstance

  #@private
  def createCallDirectoryAndFile(self, sourceOfCallTemplate, destinationCallInstance, newPointerLineWindows, oldTfStateName):
    import config_cliprocessor
    myLogWriter = log_writer()
    keySource = config_cliprocessor.inputVars.get('keySource')
    Path(destinationCallInstance).mkdir(parents=True, exist_ok=True)
    copy_tree(sourceOfCallTemplate, destinationCallInstance)
    fileName = destinationCallInstance + "main.tf"
    if platform.system() == 'Windows':
      #WORK ITEM: change this 4 line windows block to reflect the two line linux version below it.
      searchTerm = "/modules/"
      self.deleteWrongOSPointerLineInCallToModule(fileName, searchTerm)
      searchTerm = "\\modules\\"
      self.changePointerLineInCallToModule(fileName, searchTerm, newPointerLineWindows)
    else: 
      searchTerm = ' source = '
      self.replacePointerLineInCallToModule(fileName, searchTerm)
    if keySource != "keyVault":
      if(self.checkIfFileExists(oldTfStateName)):
        logString = "oldTfStateName file exists. Copying the backup tfstate file into this directory to use again."
        myLogWriter.writeLogVerbose("acm", logString)
        destStateFile = destinationCallInstance + "terraform.tfstate"
        shutil.copyfile(oldTfStateName, destStateFile)
      else:
        logString = "oldTfStateName file does NOT exist. "
        myLogWriter.writeLogVerbose("acm", logString)

  #@private
  def deleteWrongOSPointerLineInCallToModule(self, fileName, searchTerm): 
    with fileinput.FileInput(fileName, inplace = True) as f: 
      for line in f: 
        if searchTerm in line: 
          print('', end ='\n') 
        else: 
          print(line, end ='') 

  #@private
  def changePointerLineInCallToModule(self, fileName, searchTerm, newPointerLine): 
    with fileinput.FileInput(fileName, inplace = True) as f: 
      for line in f: 
        if searchTerm in line: 
          print(newPointerLine, end ='\n') 
        else: 
          print(line, end ='')

  #@private
  def replacePointerLineInCallToModule(self, fileName, searchTerm): 
    with fileinput.FileInput(fileName, inplace = True) as f: 
      for line in f: 
        if searchTerm in line: 
          line = line.replace('\\','/')
          line = line.replace('//','/')
          firstQuoteIndex = line.index('"',0)
          partBeforeQuote = line[0:firstQuoteIndex]
          partAfterQuote = line[firstQuoteIndex:]
          moduleStartIndex = partAfterQuote.index('m',0)
          partStartingWithModule = partAfterQuote[moduleStartIndex:]
          replacementLine = partBeforeQuote+'"../../../../'+partStartingWithModule
          print(replacementLine, end ='\n') 
        else: 
          print(line, end ='') 

  #@private
  def checkIfFileExists(self, oldTfStateName):
    doesExist = False
    try:
      with open(oldTfStateName) as f:
        f.readlines()
        doesExist = True
    except IOError:
      doesExist = False
    return doesExist

  #@private
  def initializeTerraformBackend(self, systemConfig, keyDir, typeName, destinationCallInstance, remoteBackend, instanceName):
    import config_cliprocessor
    myLogWriter = log_writer()
    binariesPath = config_cliprocessor.inputVars.get('dependenciesBinariesPath') 
    if remoteBackend is True: 
      tool = "terraform"
      if typeName == "networkFoundation":
        backendVarCoordinates = systemConfig.get("foundation").get("backendVariables")
      else:
        #USE THE SAME Next 13 LINES TO GET THE mappedVariables EXCEPT CHANGE NAME.
        sharedVarsDict = {}
        instanceVarsDict = {}
        if "sharedVariables" in systemConfig.get("serviceTypes").get(typeName).keys():
          if "backendVariables" in systemConfig.get("serviceTypes").get(typeName).get("sharedVariables"):
            sharedVarsDict = systemConfig.get("serviceTypes").get(typeName).get("sharedVariables").get("backendVariables")
        for fieldOfType in systemConfig.get("serviceTypes").get(typeName):
          if fieldOfType == "instances":
            for thisInstance in systemConfig.get("serviceTypes").get(typeName).get(fieldOfType):
              if thisInstance.get("instanceName") == instanceName:
                instanceVarsDict = thisInstance.get("backendVariables")
        backendVarCoordinates = { **sharedVarsDict, **instanceVarsDict }
      from command_builder import command_builder
      cb = command_builder()
      backendVars = cb.getBackendVarsFragment(backendVarCoordinates, tool, keyDir)
      initCommand= binariesPath + "terraform init -backend=true " + backendVars
    else:
      initCommand = binariesPath + 'terraform init '
    logString = "...................................................................................."
    myLogWriter.writeLogVerbose("acm", logString)
    logString = "initCommand is: " + initCommand
    myLogWriter.writeLogVerbose("acm", logString)
    logString = "...................................................................................."
    myLogWriter.writeLogVerbose("acm", logString)
    self.runTerraformCommand(initCommand, destinationCallInstance)	
    #Add error handling to validate that init command succeeded.

  #@private
  def assembleAndRunCommand(self, systemConfig, instance, operation, instanceName, destinationCallInstance, typeName):
    import config_cliprocessor
    myLogWriter = log_writer()
    if typeName == 'networkFoundation':
      global foundationApply
      foundationApply = True
      mappedVariables = systemConfig.get("foundation").get("mappedVariables")
      serviceType = None
    else:
      serviceType = typeName
      sharedVarsDict = {}
      instanceVarsDict = {}
      if "sharedVariables" in systemConfig.get("serviceTypes").get(typeName).keys():
        if "mappedVariables" in systemConfig.get("serviceTypes").get(typeName).get("sharedVariables"):
          sharedVarsDict = systemConfig.get("serviceTypes").get(typeName).get("sharedVariables").get("mappedVariables")
      for fieldOfType in systemConfig.get("serviceTypes").get(typeName):
        if fieldOfType == "instances":
          for thisInstance in systemConfig.get("serviceTypes").get(typeName).get(fieldOfType):
            if thisInstance.get("instanceName") == instanceName:
              instanceVarsDict = thisInstance.get("mappedVariables")
      mappedVariables = { **sharedVarsDict, **instanceVarsDict }
    commandToRun = 'invalid value must be reset below'
    tool = "terraform"
    binariesPath = config_cliprocessor.inputVars.get('dependenciesBinariesPath') 
    from command_builder import command_builder
    cb = command_builder()
    if operation == 'off':
      #Passing foundationInstanceName into getVarsFragment because we want to use the keys associated with the network foundation when we are attaching anything to the network foundation.
      varsFrag = cb.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, tool, self)
      commandToRun = binariesPath + "terraform destroy -auto-approve" + varsFrag
    elif operation == 'on':
      #Passing foundationInstanceName into getVarsFragment because we want to use the keys associated with the network foundation when we are attaching anything to the network foundation.
      varsFrag = cb.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, tool, self)
      commandToRun = binariesPath + "terraform apply -auto-approve " + varsFrag
    elif operation == 'output':
      commandToRun = binariesPath + 'terraform output'
    else:
      logString = "Error: Invalid value for operation: " + operation
      myLogWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
    logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
    myLogWriter.writeLogVerbose("acm", logString)
    myLogWriter.writeLogVerbose("acm", logString)
    logString = "commandToRun is: " + commandToRun
    myLogWriter.writeLogVerbose("acm", logString)
    logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
    myLogWriter.writeLogVerbose("acm", logString)
    myLogWriter.writeLogVerbose("acm", logString)
    logString = '... destinationCallInstance is: '+ destinationCallInstance
    myLogWriter.writeLogVerbose("acm", logString)
    self.runTerraformCommand(commandToRun, destinationCallInstance)

  #@private
  def setDoCleanUp(self, oper):
    cleanup = False
    if oper == 'on':
      if self.terraformResult == "Applied": 
        cleanup = True
    elif oper == 'off':
      if self.terraformResult == "Destroyed": 
        cleanup = True
    elif oper == 'output':
      #Add some check here to confirm that the output operation succeeded.
      cleanup = True
    return cleanup

  #@private
  def cleanupAfterOperation(self, destinationCallInstance, destinationCallParent, foundationInstanceName, templateName, instanceName, key_source):
    import config_cliprocessor
    myLogWriter = log_writer()
    dynamicVarsPath = config_cliprocessor.inputVars.get('dynamicVarsPath')
    if key_source =="keyFile":
      #Now make a backup copy of the tfstate file.
      tfStateSrc = destinationCallInstance + 'terraform.tfstate'
      tfStateDest = self.getBackedUpStateFileName(dynamicVarsPath, foundationInstanceName, templateName, instanceName)
      if os.path.isfile(tfStateSrc):
        shutil.copy(tfStateSrc, tfStateDest)
    self.offInstanceOfCallToModule(destinationCallInstance, destinationCallParent)
    ###############################################################################
    ### Delete the tfvars file and the instance of the call to module
    ### Note we only want keys to be in external locations such as a vault
    ###############################################################################
    try:
      logString = "About to remove the tfvars file. "
      myLogWriter.writeLogVerbose("acm", logString)
    except OSError:
      pass

  #@private
  def offInstanceOfCallToModule(self, locationOfCallInstance, parentDirOfCallInstance):
    myLogWriter = log_writer()
    logString = "Sleeping 10 seconds to prevent intermittent problem of files not deleting."
    myLogWriter.writeLogVerbose("acm", logString)
    import time
    time.sleep(10)
    if os.path.exists(locationOfCallInstance) and os.path.isdir(locationOfCallInstance):
      path = Path(locationOfCallInstance)
      shutil.rmtree(path)
    else:
      logString = "Given Directory doesn't exist: " + locationOfCallInstance
      myLogWriter.writeLogVerbose("acm", logString)
    if os.path.exists(parentDirOfCallInstance) and os.path.isdir(parentDirOfCallInstance):
      if not os.listdir(parentDirOfCallInstance):
        logString = "Directory is empty"
        myLogWriter.writeLogVerbose("acm", logString)
        path = Path(parentDirOfCallInstance)
        shutil.rmtree(path)
      else:    
        logString = "Parent directory is not empty, so we will keep it for now: " + parentDirOfCallInstance
        myLogWriter.writeLogVerbose("acm", logString)
    else:
      logString = "Given Directory doesn't exist: " + parentDirOfCallInstance
      myLogWriter.writeLogVerbose("acm", logString)
    
  #@private
  def runTerraformCommand(self, commandToRun, workingDir, counter=0):
    try:
      myLogWriter = log_writer()
      reachedOutputs = False
      if " apply" in commandToRun:
        commFragment = "apply"
      elif " destroy" in commandToRun:
        commFragment = "destroy"
      elif " output" in commandToRun:
        commFragment = "output"
      else:
        commFragment = "other"
      lineNum = 0
      errIdx = 0
      isError = "no"
      #Make a work item to re-write this function to throw an error and stop the program whenever an error is encountered.
      proc = subprocess.Popen( commandToRun,cwd=workingDir,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
      while True:
        line = proc.stdout.readline()
        if line:
          lineNum += 1
          thetext=line.decode('utf-8').rstrip('\r|\n')
          decodedline=self.ansi_escape.sub('', thetext)
          myLogWriter.writeLogVerbose("terraform", decodedline)
          if 'Outputs' in decodedline:
            reachedOutputs = True
          if (commFragment == 'output'):
            if (decodedline.count('=') == 1):
              lineParts = decodedline.split('=')
              key = lineParts[0].replace(' ','').replace('"','').replace("'","")
              value = lineParts[1].replace(' ','').replace('"','').replace("'","")
              self.tfOutputDict[key] = value
          if (commFragment != 'output') and (self.foundationApply == True):
            if (decodedline.count('=') == 1) and (reachedOutputs == True):
              lineParts = decodedline.split('=')
              key = lineParts[0].replace(' ','').replace('"','').replace("'","")
              value = lineParts[1].replace(' ','').replace('"','').replace("'","")
              self.tfOutputDict[key] = value
          errIdx = self.processDecodedLine(decodedline, errIdx, commFragment)
        else:
          break
    except:
      counter += 1
      logString = "ERROR: Terraform encountered an error.  We will rerun the terraform command up to 5 times before quitting, in case the problem was caused by latency in the cloud provider. "
      myLogWriter.writeLogVerbose("acm", logString)
      if counter < 6:
        logString = "counter is: "+str(counter)+" .  Going to retry. "
        myLogWriter.writeLogVerbose("acm", logString)
        self.runTerraformCommand(commandToRun, workingDir, counter)
      elif counter >= 6:
        logString = "counter is: "+str(counter)+" .  Going to let the program break so you can examine the root cause of the error. "
        myLogWriter.writeLogVerbose("acm", logString)

  #@private
  def processDecodedLine(self, decodedline, errIdx, commFragment):
    myLogWriter = log_writer()
    if "Too many command line arguments." in decodedline:
      logString = "Error: The variables you passed into the terraform command were corrupted. "
      myLogWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
    if "Failed to instantiate provider" in decodedline:
      logString = "Error: Failed to instantiate provider.  Halting program so you can check your configuration and identify the root of the problem. "
      myLogWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
    if ("giving up after " in decodedline) and (" attempt(s)" in decodedline):
      logString = "Error: Halting program so you can examine upstream logs to discover what the cause is. "
      myLogWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
    if ("Error: No Images were found for Resource Group" in decodedline) and (commFragment == "apply"):
      logString = "Error: No Images were found for Resource Group.  Halting program so you can check your configuration and identify the root of the problem. "
      myLogWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
    if "Error:" in decodedline:
      logString = decodedline+".  Halting program so you can check your configuration and identify the root of the problem. "
      myLogWriter.writeLogVerbose("acm", logString)
      sys.exit(1) 
    if "Destroy complete!" in decodedline:
      logString = "Found Destroy complete!!"
      myLogWriter.writeLogVerbose("acm", logString)
      self.terraformResult="Destroyed"
    if "Apply complete!" in decodedline:
      logString = "Found Apply complete!!"
      myLogWriter.writeLogVerbose("acm", logString)
      self.terraformResult="Applied"
    return errIdx

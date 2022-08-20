## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import os 
import platform

from log_writer import log_writer
from config_fileprocessor import config_fileprocessor
from command_formatter import command_formatter

class config_keysassembler:
  
  def __init__(self):  
    pass

  destinationLinesList = []
  backendVarsList = []
  adminVarsList = []
  sourceLinesList = []

  #@private
  def getBackendVarsList(self, systemConfig, instance, yaml_keys_file_and_path, keyDir):
    cfm = command_formatter()
    instName = instance.get("instanceName")
    yaml_keys_file_and_path = cfm.getKeyFileAndPath(keyDir)
    backendType = instance.get("type")
    self.backendVarsList = []
    if backendType == 'azurerm':  
      #Get the variable values
      resourceGroupName = instance.get("resourceGroupName")
      self.backendVarsList.append({"key":"resourceGroupName", "value":resourceGroupName, "handled":False})
      resourceGroupRegion = instance.get("resourceGroupRegion")
      self.backendVarsList.append({"key":"resourceGroupRegion", "value":resourceGroupRegion, "handled":False})
      cfp = config_fileprocessor()
      subscriptionId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'subscriptionId')
      self.backendVarsList.append({"key":"subscriptionId", "value":subscriptionId, "handled":False})
      clientId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
      self.backendVarsList.append({"key":"clientId", "value":clientId, "handled":False})
      clientSecret = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret')
      if clientSecret[0] == '-':
        clientSecret = '\'' + clientSecret + '\''
      self.backendVarsList.append({"key":"clientSecret", "value":clientSecret, "handled":False})
      tenantId = cfp.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
      self.backendVarsList.append({"key":"tenantId", "value":tenantId, "handled":False})
      orgName = systemConfig.get("organization") 
      self.backendVarsList.append({"key":"orgName", "value":orgName, "handled":False})
      storageAccountName = instName.lower() + orgName.lower()
      self.backendVarsList.append({"key":"storageAccountName", "value":storageAccountName, "handled":False})
      #ADD VALIDATION TO CONFIRM THAT storageAccountName IS NOT LONGER THAN 24 CHARACTERS TO PREVENT DOWNSTREAM ERROR.

  #@private
  def getSourceLines(self, keyDir):
    cfm = command_formatter()
    self.sourceLinesList = []
    keyDir = cfm.formatKeyDir(keyDir)
    sourceKeysFile = keyDir + "keys.yaml"
    #get the source variables into a new array
    if os.path.isfile(sourceKeysFile):
      with open(sourceKeysFile, 'r') as file:
        rawSourceLines = file.readlines()
      #now we have an array of lines. 
      for line in rawSourceLines:
        if (":" in line) and (line.lstrip()[:1] != "#"):
          lineParts = line.split(":")
          if not lineParts[0].isspace():
            if len(lineParts) > 2:
              myValue = ""
              if ("http" in lineParts[1]):
                for part in lineParts[-(len(lineParts)-1):]:
                  part = part.strip()
                  myValue = myValue + ":" + part
                if myValue[0] == ":":
                  myValue = myValue[1:]
              self.sourceLinesList.append({"key":lineParts[0].lstrip(),"value":myValue.strip(),"handled":False})
            else:
              self.sourceLinesList.append({"key":lineParts[0].lstrip(),"value":lineParts[1].strip(),"handled":False})
          else:
            print("WARNING: line contained whitespace to the left of first colon :, so we are skipping it.  If this is in error, please go back and validate your inputs before re-running. ")
    else:
      print("ERROR: sourceKeysFile does NOT exist.")

  #@private
  def checkSourceLinesAgainstAdminVarsRecursively(self):
    for sourceLine in self.sourceLinesList:
      matched = False
      if sourceLine["handled"] == False:
        # Look for a matching key in adminVarsList
        for adminVar in self.adminVarsList:
          if (adminVar["key"] == sourceLine["key"]) and (adminVar["handled"] == False):
            self.destinationLinesList.append(adminVar)
            self.changeSourceLines(sourceLine["key"], True)
            self.changeAdminVars(adminVar["key"], True)
            matched = True
        # Break out of loop if you found a matching key in adminVarsList
        if matched:
          break

  #@private
  def changeAdminVars(self, key, handled):
    for adminVar in self.adminVarsList:
      if adminVar["key"] == key:
        adminVar["handled"] = handled

  #@private
  def changeBackendVars(self, key, handled):
    for backendVar in self.backendVarsList:
      if backendVar["key"] == key:
        backendVar["handled"] = handled

  #@private
  def changeSourceLines(self, key, handled):
    for sourceLine in self.sourceLinesList:
      if sourceLine["key"] == key:
        sourceLine["handled"] = handled

  #@private
  def checkSourceLinesAgainstBackendVarsRecursively(self, typeOfSecret):
    for sourceLine in self.sourceLinesList:
      matched = False
      if sourceLine["handled"] == False:
        # Look for a matching key in backendVarsList
        for backendVar in self.backendVarsList:
          if (backendVar["key"] == sourceLine["key"]) and (backendVar["handled"] == False):
            if typeOfSecret == "child":
              self.destinationLinesList.append(backendVar)
            else:
              self.destinationLinesList.append(sourceLine)
            self.changeSourceLines(sourceLine["key"], True)
            self.changeBackendVars(backendVar["key"], True)
            matched = True
        # Break out of loop if you found a matching key in backendVarsList
        if matched:
          break

  #@public
  def getOutputDir(self, instName):
    import config_cliprocessor
    cfm = command_formatter()
    outputDir = config_cliprocessor.inputVars.get('dirOfOutput')
    outputDir = outputDir + instName
    if not os.path.exists(outputDir):
      os.makedirs(outputDir, exist_ok=True) 
    if platform.system() == "Windows":
      if outputDir[-1] != '\\':
        outputDir = outputDir + '\\'
    elif platform.system() == "Linux":
      if outputDir[-1] != '/':
        outputDir = outputDir + '/'
    cfm.formatPathForOS(outputDir)
    return outputDir

  #@public
  def writeTheVarsFile(self, systemConfig, instance, sourceOfCall, app_id, secKey):
    instName = instance.get("instanceName")
    cfp = config_fileprocessor()
    lw = log_writer()
    cfm = command_formatter()
    keyDir = cfp.getKeyDir(systemConfig)
    outputDir = self.getOutputDir(instName)
    outputKeysFile = outputDir + "keys.yaml"
    if sourceOfCall == "admin":
      #this block ensures that anything already written to the destination file will remain in it, except for explicit changes handled by this function.
      if os.path.isfile(outputKeysFile):
        keyDir = outputDir
    self.getSourceLines(keyDir)
    #get secretsType
    typeOfSecret = "empty"
    for sourceLine in self.sourceLinesList:
      if sourceLine["key"] == "secretsType":
        typeOfSecret = sourceLine["value"]
    if sourceOfCall == "tfBackend":
      #if keys exist in outputDir, then use those.  Otherwise, pull keys in from source.  This should protect against overwriting keys.
      yaml_keys_file_and_path = cfm.getKeyFileAndPath(outputDir)
      if os.path.isfile(yaml_keys_file_and_path):
        #testing the following call with outputDir instead of keyDir
        self.getBackendVarsList(systemConfig, instance, yaml_keys_file_and_path, outputDir)
      else:
        self.getBackendVarsList(systemConfig, instance, yaml_keys_file_and_path, keyDir)
    if sourceOfCall == "admin":
      #Test the vars from azureAdmin
      if app_id.startswith('"') and app_id.endswith('"'):
        app_id = app_id[1:-1]
      if 'empty' in secKey:
        logString = "Error: Failed to load Client Secret.  This might be resolved by re-running the admin module.  Halting program here so you can examine the problem. "
        lw.writeLogVerbose("acm", logString)
        exit(1)
      if 'whatToSearchFor' in app_id: #Change whatToSearchFor to an actual string once the error state is defined.  Just leaving this here now to show where and how to place this check.
        logString = "Error: Failed to load app_id.  This might be resolved by re-running the admin module.  Halting program here so you can examine the problem. "
        lw.writeLogVerbose("acm", logString)
        exit(1)
      itemDict = {"key":"clientId", "value":app_id, "handled":False}
      self.adminVarsList.append(itemDict)
      secKey = secKey.replace('"','')
      secKey = secKey.replace("'","")
      itemDict = {"key":"clientSecret", "value":secKey, "handled":False}
      self.adminVarsList.append(itemDict)
    if sourceOfCall == "tfBackend":
      # Integrate any backendVars that are also in sourceLinesList, while prioritizing the backendVar values
      for sourceLine in self.sourceLinesList:
        self.checkSourceLinesAgainstBackendVarsRecursively(typeOfSecret)
    if sourceOfCall == "admin":
      # Integrate any admin Vars that are also in sourceLinesList, while prioritizing the admin Var values
      for sourceLine in self.sourceLinesList:
        self.checkSourceLinesAgainstAdminVarsRecursively()
    # put into destinationLinesList any items from sourceLinesList that were not also present in backendVarsList
    for sourceLine in self.sourceLinesList:
      if sourceLine["handled"] == False:
        sourceLine["handled"] = True
        self.destinationLinesList.append(sourceLine)
    if sourceOfCall == "tfBackend":
      # put into destinationLinesList any items from backendVarsList that were not also present in sourceLinesList
      for backendVar in self.backendVarsList:
        if backendVar["handled"] == False:
          backendVar["handled"] = True
          self.destinationLinesList.append(backendVar)
    if sourceOfCall == "admin":
      # put into destinationLinesList any items from adminVarsList that were not also present in sourceLinesList
      for adminVar in self.adminVarsList:
        if adminVar["handled"] == False:
          adminVar["handled"] = True
          self.destinationLinesList.append(adminVar)
    if sourceOfCall == "admin":
      for destinationLine in self.destinationLinesList:
        if destinationLine["key"] == "secretsType":
          destinationLine["value"] = "child"
    finalDestinationLinesList = []
    for destinationLine in self.destinationLinesList:
      myVal = destinationLine["value"]
      myVal = myVal.replace('"','')
      myVal = myVal.replace("'","")
      newLine = destinationLine["key"] + ":" + "\"" + myVal + "\"" + "\n"
      newLine = newLine.replace('"','')
      newLine = newLine.replace("'","")
      finalDestinationLinesList.append(newLine)
    with open(outputKeysFile, mode='wt', encoding='utf-8') as myfile:
      for myLine in finalDestinationLinesList:
        myfile.write(myLine)
    self.sourceLinesList.clear()
    self.backendVarsList.clear()
    self.adminVarsList.clear()
    self.destinationLinesList.clear()

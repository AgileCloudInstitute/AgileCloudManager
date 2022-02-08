## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import sys
import platform
import os

import config_cliprocessor
import controller_terraform
import config_fileprocessor
import command_builder
import config_cliprocessor
import controller_tfbackendazrm

destinationLinesList = []
backendVarsList = []
adminVarsList = []
sourceLinesList = []

def getBackendVars(infraConfigFileAndPath, keyDir, instName):
  print("1 debug. ")
  cloud = config_fileprocessor.getCloudName(infraConfigFileAndPath)
  yaml_keys_file_and_path = command_builder.getKeyFileAndPath(keyDir, 'systems', cloud)
  templateName = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, "tfBackend", instName, "templateName")
  backendType = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, "tfBackend", instName, "type")
  global backendVarsList
  backendVarsList = []
  if backendType == 'azurerm':  
    #Get the variable values
    resourceGroupName = controller_tfbackendazrm.getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'resourceGroupName')
    backendVarsList.append({"key":"resourceGroupName", "value":resourceGroupName, "handled":False})
    resourceGroupRegion = controller_tfbackendazrm.getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'resourceGroupRegion')
    backendVarsList.append({"key":"resourceGroupRegion", "value":resourceGroupRegion, "handled":False})
    subscriptionId = controller_tfbackendazrm.getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'subscriptionId')
    backendVarsList.append({"key":"subscriptionId", "value":subscriptionId, "handled":False})
    clientId = controller_tfbackendazrm.getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'clientId')
    backendVarsList.append({"key":"clientId", "value":clientId, "handled":False})
    clientSecret = controller_tfbackendazrm.getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'clientSecret')
    if clientSecret[0] == '-':
      clientSecret = '\'' + clientSecret + '\''
    backendVarsList.append({"key":"clientSecret", "value":clientSecret, "handled":False})
    tenantId = controller_tfbackendazrm.getTfBackendPropVal(yaml_keys_file_and_path, infraConfigFileAndPath, instName, templateName, 'tenantId')
    backendVarsList.append({"key":"tenantId", "value":tenantId, "handled":False})
    orgName = config_fileprocessor.getFirstLevelValue(infraConfigFileAndPath, "organization")
    backendVarsList.append({"key":"orgName", "value":orgName, "handled":False})
    storageAccountName = instName.lower() + orgName.lower()
    backendVarsList.append({"key":"storageAccountName", "value":storageAccountName, "handled":False})

    #ADD VALIDATION TO CONFIRM THAT storageAccountName IS NOT LONGER THAN 24 CHARACTERS TO PREVENT DOWNSTREAM ERROR.

def getSourceLines(keyDir):
  global sourceLinesList
  sourceLinesList = []
  keyDir = formatKeyDir(keyDir)
  sourceKeysFile = keyDir + "adUserKeys.yaml"

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
            sourceLinesList.append({"key":lineParts[0].lstrip(),"value":myValue.strip(),"handled":False})
          else:
            sourceLinesList.append({"key":lineParts[0].lstrip(),"value":lineParts[1].strip(),"handled":False})
        else:
          print("WARNING: line contained whitespace to the left of first colon :, so we are skipping it.  If this is in error, please go back and validate your inputs before re-running. ")
  else:
    print("ERROR: sourceKeysFile does NOT exist.")


def checkSourceLinesAgainstBackendVarsRecursively(typeOfSecret):
  global sourceLinesList
  global backendVarsList
  for sourceLine in sourceLinesList:
    matched = False
    if sourceLine["handled"] == False:
      # Look for a matching key in backendVarsList
      for backendVar in backendVarsList:
        if (backendVar["key"] == sourceLine["key"]) and (backendVar["handled"] == False):
          if typeOfSecret == "child":
            print("+++ ... backendVar is: ", backendVar)
            print("+++ ... sourceLine is: ", sourceLine)
            destinationLinesList.append(backendVar)
          else:
            destinationLinesList.append(sourceLine)
          changeSourceLines(sourceLine["key"], True)
          changeBackendVars(backendVar["key"], True)
          matched = True
      # Break out of loop if you found a matching key in backendVarsList
      if matched:
        break

def checkSourceLinesAgainstAdminVarsRecursively():
  global sourceLinesList
  global adminVarsList
  for sourceLine in sourceLinesList:
    matched = False
    if sourceLine["handled"] == False:
      # Look for a matching key in adminVarsList
      for adminVar in adminVarsList:
        if (adminVar["key"] == sourceLine["key"]) and (adminVar["handled"] == False):
          destinationLinesList.append(adminVar)
          changeSourceLines(sourceLine["key"], True)
          changeAdminVars(adminVar["key"], True)
          matched = True
      # Break out of loop if you found a matching key in adminVarsList
      if matched:
        break


def changeBackendVars(key, handled):
  global backendVarsList
  for backendVar in backendVarsList:
    if backendVar["key"] == key:
      backendVar["handled"] = handled

def changeAdminVars(key, handled):
  global adminVarsList
  for adminVar in adminVarsList:
    if adminVar["key"] == key:
      adminVar["handled"] = handled

def changeDestinationLines(key, handled):
  global destinationLinesList

def changeSourceLines(key, handled):
  global sourceLinesList
  for sourceLine in sourceLinesList:
    if sourceLine["key"] == key:
      sourceLine["handled"] = handled

def getOutputDir(instName):
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
  command_builder.formatPathForOS(outputDir)
  return outputDir

def formatKeyDir(keyDir):
  if platform.system() == "Windows":
    if keyDir[-1] != '\\':
      keyDir = keyDir + '\\'
  elif platform.system() == "Linux":
    if keyDir[-1] != '/':
      keyDir = keyDir + '/'
  keyDir = command_builder.formatPathForOS(keyDir)
  return keyDir
  
def writeTheVarsFile(instName, yaml_infra_config_file_and_path, keyDir, cloud, typeName, sourceOfCall, secKey, app_id):
    global destinationLinesList
    print("instName is: ", instName)
    print("keyDir is: ", keyDir)
    outputDir = getOutputDir(instName)
    outputKeysFile = outputDir + "adUserKeys.yaml"
    if sourceOfCall == "admin":
      #this block ensures that anything already written to the destination file will remain in it, except for explicit changes handled by this function.
      if os.path.isfile(outputKeysFile):
        keyDir = outputDir
    getSourceLines(keyDir)
    global sourceLinesList
    global adminVarsList
    #get secretsType
    typeOfSecret = "empty"
    for sourceLine in sourceLinesList:
      if sourceLine["key"] == "secretsType":
        typeOfSecret = sourceLine["value"]
    if sourceOfCall == "tfBackend":
      #if keys exist in outputDir, then use those.  Otherwise, pull keys in from source.  This should protect against overwriting keys.
      cloud = config_fileprocessor.getCloudName(yaml_infra_config_file_and_path)
      yaml_keys_file_and_path = command_builder.getKeyFileAndPath(outputDir, 'systems', cloud)
      if os.path.isfile(yaml_keys_file_and_path):
        #testing the following call with outputDir instead of keyDir
        getBackendVars(yaml_infra_config_file_and_path, outputDir, instName)
      else:
        getBackendVars(yaml_infra_config_file_and_path, keyDir, instName)
      global backendVarsList
    if sourceOfCall == "admin":
      #Test the vars from azureAdmin
      org = config_fileprocessor.getFirstLevelValue(yaml_infra_config_file_and_path, "organization")
      if app_id.startswith('"') and app_id.endswith('"'):
        app_id = app_id[1:-1]
      if 'empty' in secKey:
        logString = "Error: Failed to load Client Secret.  This might be resolved by re-running the admin module.  Halting program here so you can examine the problem. "
        logWriter.writeLogVerbose("acm", logString)
        exit(1)
      if 'whatToSearchFor' in app_id: #Change whatToSearchFor to an actual string once the error state is defined.  Just leaving this here now to show where and how to place this check.
        logString = "Error: Failed to load app_id.  This might be resolved by re-running the admin module.  Halting program here so you can examine the problem. "
        logWriter.writeLogVerbose("acm", logString)
        exit(1)
      itemDict = {"key":"clientId", "value":app_id, "handled":False}
      adminVarsList.append(itemDict)
      secKey = secKey.replace('"','')
      secKey = secKey.replace("'","")
      itemDict = {"key":"clientSecret", "value":secKey, "handled":False}
      adminVarsList.append(itemDict)
    if sourceOfCall == "tfBackend":
      # Integrate any backendVars that are also in sourceLinesList, while prioritizing the backendVar values
      for sourceLine in sourceLinesList:
        checkSourceLinesAgainstBackendVarsRecursively(typeOfSecret)
    if sourceOfCall == "admin":
      # Integrate any admin Vars that are also in sourceLinesList, while prioritizing the admin Var values
      for sourceLine in sourceLinesList:
        checkSourceLinesAgainstAdminVarsRecursively()
    # put into destinationLinesList any items from sourceLinesList that were not also present in backendVarsList
    for sourceLine in sourceLinesList:
      if sourceLine["handled"] == False:
        sourceLine["handled"] = True
        destinationLinesList.append(sourceLine)

    if sourceOfCall == "tfBackend":
      # put into destinationLinesList any items from backendVarsList that were not also present in sourceLinesList
      for backendVar in backendVarsList:
        if backendVar["handled"] == False:
          backendVar["handled"] = True
          destinationLinesList.append(backendVar)
    if sourceOfCall == "admin":
      # put into destinationLinesList any items from adminVarsList that were not also present in sourceLinesList
      for adminVar in adminVarsList:
        if adminVar["handled"] == False:
          adminVar["handled"] = True
          destinationLinesList.append(admin)

    if sourceOfCall == "admin":
      for destinationLine in destinationLinesList:
        if destinationLine["key"] == "secretsType":
          destinationLine["value"] = "child"
    finalDestinationLinesList = []
    for destinationLine in destinationLinesList:
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
    sourceLinesList.clear()
    backendVarsList.clear()
    adminVarsList.clear()
    destinationLinesList.clear()

## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import yaml
import re
import requests
import sys
import csv
import json
import platform
import os
import command_runner
import logWriter
import config_cliprocessor

def formatPathForOS(input):
  if platform.system() == "Windows":
    input.replace('/','\\')
    input.replace('\\\\','\\')
    input.replace('\\\\\\','\\')
  elif platform.system() == "Linux":
    input.replace('\\','/')
    input.replace('//','/')
    input.replace('///','/')
  if input.endswith('/n'):
    input = input[:-2] + '\n'
  return input

def getVarFromUserConfig(tool, row, yamlInfraFileAndPath, parentInstanceName, callInstanceName, org):
  inputVar = row[0]
  myType = row[2]
  identifier = row[3]
  sourceField = row[4]
  varSnip = "empty"
  with open(yamlInfraFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():
      if myType.count('/') == 1:
        parentPart = myType.split('/')[0]
        childPart = myType.split('/')[1]
        if re.match(parentPart, key):
          parent = my_dict.get(key)
          for child in parent:
            if re.match(childPart, child):
              varSnip = getVarFromType(tool, row, callInstanceName, 2, parent.get(child), org)
              if inputVar == "cloudInit":
                varSnip = varSnip.replace("\\\\", "\\")
      elif myType.count('/') == 2:
        if myType == 'systems/projects/code':
          parentPart = myType.split('/')[0]
          childPart = myType.split('/')[1]
          grandChildPart = myType.split('/')[2]
          if re.match(parentPart, key):
            parent = my_dict.get(key)
            for child in parent:
              if re.match(childPart, child):
                if childPart == 'projects':
                  projectInstances = parent.get(child)
                  for project in projectInstances:
                    if parentInstanceName == project.get('instanceName'):
                      grandChildInstances = project.get(grandChildPart)
                      for grandChild in grandChildInstances:
                        if grandChild.get('instanceName') == callInstanceName:
                          varSnip = getVarFromType(tool, row, callInstanceName, 3, grandChild, org)
        elif myType == 'systems/projects/parent':
          parentPart = myType.split('/')[0]
          childPart = myType.split('/')[1]
          grandChildPart = myType.split('/')[2]
          if re.match(parentPart, key):
            parent = my_dict.get(key)
            for child in parent:
              if re.match(childPart, child):
                if childPart == 'projects':
                  projectInstances = parent.get(child)
                  for project in projectInstances:
                    if parentInstanceName == project.get('instanceName'):
                      varSnip = getVarFromType(tool, row, callInstanceName, 2, project, org)
        else: 
          logString = "Error: Unsupported name for type.  Halting program so you can locate the problem within your configuration."
          logWriter.writeLogVerbose("acm", logString)
          sys.exit(1)
      elif myType.count('/') > 2:
        logString = "More than two occurrences of / are in myType. This is illegal, so we are halting the program to give you a chance to validate your configuration. "
        logWriter.writeLogVerbose("acm", logString)
        sys.exit(1)
      else:
        if re.match(myType, key):
          type = my_dict.get(key)
          varSnip = getVarFromType(tool, row, callInstanceName, 1, type, org)
  varSnip = formatPathForOS(varSnip)
  return varSnip

def getVarFromType(tool, r, callInstanceName, layers, aType, org):
  inputVar = r[0]
  myType = r[2]
  if myType.count('/') == 1:
    myType = myType.split('/')[1]
  identifier = r[3]
  sourceField = r[4]
  varSnip = "empty"
  for props in aType:
    if isinstance(props, str):
      if inputVar == 'cidrBlocks': 
        if props == 'cidrBlocks':
          if aType.get(props) == 'admin':
            cidrBlocks = getAdminCidr()
          elif aType.get(props) == 'public':
            cidrBlocks = '0.0.0.0/0'
          else:
            logString = "cidr block not valid."
            logWriter.writeLogVerbose("acm", logString)
          if tool == 'terraform':
            varSnip = " -var=\"" +inputVar + "="+cidrBlocks +"\""  
          elif tool == 'packer':
            varSnip = " -var \"" +inputVar + "="+cidrBlocks +"\""  
      elif re.match(sourceField, props):
        if tool == 'terraform':
          varSnip = " -var=\"" +inputVar + "="+str(aType.get(props)) +"\""  
        elif tool == 'packer':
          varSnip = " -var \"" +inputVar + "="+str(aType.get(props)) +"\""  
    else:
      for prop in props:
        if props.get("instanceName") == callInstanceName:
          if re.match(sourceField, prop):
            if sourceField == "cidrBlocks":
              if props.get("instanceName") == callInstanceName:
                if props.get(prop) == 'admin':
                  cidrBlocks = getAdminCidr()
                elif props.get(prop) == 'public':
                  cidrBlocks = '0.0.0.0/0'
                else:
                  logString = "cidr block not valid."
                  logWriter.writeLogVerbose("acm", logString)
              if tool == 'terraform':
                varSnip = " -var=\"" +inputVar + "="+cidrBlocks +"\""  
              elif tool == 'packer':
                varSnip = " -var \"" +inputVar + "="+cidrBlocks +"\""  
            elif sourceField == 'pathToScript':
              if props.get(prop) == 'azure':
                configAndSecretsPath = config_cliprocessor.inputVars.get("configAndSecretsPath")
                pathStr = configAndSecretsPath + props.get(prop) + "\startup-script-demo.sh"
                pathStr = formatPathForOS(pathStr)
                if tool == 'terraform':
                  varSnip = " -var=\"" +inputVar + "="+str(pathStr) +"\""  
                elif tool == 'packer':
                  varSnip = " -var \"" +inputVar + "="+str(pathStr) +"\""  
            elif sourceField == 'instanceName':
              if myType == "admin":
                if tool == 'terraform':
                  varSnip = " -var=\"" +inputVar + "="+str(props.get(prop))+"-"+org +"\""  
                elif tool == 'packer':
                  varSnip = " -var \"" +inputVar + "="+str(props.get(prop))+"-"+org +"\""  
              else:
                if tool == 'terraform':
                  varSnip = " -var=\"" +inputVar + "="+str(props.get(prop)) +"\""  
                elif tool == 'packer':
                  varSnip = " -var \"" +inputVar + "="+str(props.get(prop)) +"\""  
            else:  
              if tool == 'terraform':
                if sourceField == 'cloudInit':
                  appParentpath = config_cliprocessor.inputVars.get('app_parent_path')
                  relativePathAndFile = str(props.get(prop))
                  if platform.system() == "Windows":
                    appParentpath = formatPathForOS(appParentpath)
                    relativePathAndFile = formatPathForOS(relativePathAndFile)
                  varSnip = " -var=\"" +inputVar + "="+appParentpath + relativePathAndFile +"\""  
                else:
                  if callInstanceName == "azdoAgents":
                    print("prop is: ", prop)
                  varSnip = " -var=\"" +inputVar + "="+str(props.get(prop)) +"\""  
              elif tool == 'packer':
                if sourceField == 'init_script':
                  appParentpath = config_cliprocessor.inputVars.get('app_parent_path')
                  relativePathAndFile = str(props.get(prop))
                  if platform.system() == "Windows":
                    appParentpath = formatPathForOS(appParentpath)
                    relativePathAndFile = formatPathForOS(relativePathAndFile)
                  varSnip = " -var \"" +inputVar + "="+appParentpath + relativePathAndFile +"\""  
                else:
                  varSnip = " -var \"" +inputVar + "="+str(props.get(prop)) +"\""  
  varSnip = formatPathForOS(varSnip)
  return varSnip

def getSecretVarFromUserConfig(tool, r, yamlInfraFileAndPath, instanceName):
  inputVar = r[0]
  myType = r[2]
  identifier = r[3]
  sourceField = r[4]
  varLine = "empty"
  parent = 'empty'
  child = 'empty'
  if myType.count('/') == 0:
    child = myType
    with open(yamlInfraFileAndPath) as f:  
      my_dict = yaml.safe_load(f)
      for key, value in my_dict.items():  
        if re.match(myType, key):
          type = my_dict.get(key)
          for props in type:
            if isinstance(props, str):
              if re.match(sourceField, props):
                if tool == 'packer':
                  varLine = inputVar + "="+ type.get(props)
                else:
                  varLine = inputVar + "=\""+ type.get(props) +"\"\n"
            else:
              for prop in props:
                if re.match(sourceField, prop):
                  if tool == 'packer':
                    varLine = inputVar + "="+ props.get(prop)
                  else:
                    varLine = inputVar + "=\""+ props.get(prop) +"\"\n"
  elif myType.count('/') == 1:
    parent = myType.split('/', 1)[0]
    child = myType.split('/', 1)[1]
    with open(yamlInfraFileAndPath) as f:  
      my_dict = yaml.safe_load(f)
      for key, value in my_dict.items():  
        if re.match(parent, key):
          types = my_dict.get(key)
          for type in types:
            instances = types.get(type)
            print("---------------------------------------------------------")
            for instance in instances:
              print("instanceName is: ", instanceName)
              print("instance is: ", instance)
              print("r is: ", r)
              if not isinstance(instance, str):
                if instance.get(sourceField) != None:
                  if tool == 'packer':
                    varLine = inputVar + "="+ instance.get(sourceField)
                  else:
                    if instance.get("instanceName") == instanceName:
                      print("sourceField is: ", sourceField)
#                      if instance.get(sourceField) == instanceName
                      varLine = inputVar + "=\""+ instance.get(sourceField) +"\"\n"
                      if sourceField == "tfBackendStateFileName":
                        print("ooo varLine is: ", varLine)
              else:
                if instance == sourceField:
                  if instances.get(sourceField) != None:
                    if tool == 'packer':
                      varLine = inputVar + "="+ instances.get(sourceField)
                    else:
                      if instance.get("instanceName") == instanceName:
                        varLine = inputVar + "=\""+ instances.get(sourceField) +"\"\n"
                        if sourceField == "tfBackendStateFileName":
                          print("xxx varLine is: ", varLine)
  else:  
    logString = "TemplateName is malformed.  Halting program so you can debug.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  if sourceField == "tfBackendStateFileName":
    print("--- varLine is: ", varLine)
#  quit("BREAKPOINT for secret from user config.  ")
  return varLine


def getVarFromOutput(tool, r, callInstanceName):
  inputVar = r[0]
  tfOutputVarName = r[4]
  thismodule = sys.modules[__name__]
  outputVar = getattr(command_runner, tfOutputVarName)
  outputVar = outputVar.replace('"', '')
  outputVar = outputVar.replace(',', '')
  outputVar = outputVar.replace(' ', '')
  if callInstanceName == "azdoAgents":
    print("... outputVar is: ", outputVar)
  #The next 4 lines are a workaround for a bug that had been passing corrupted values for tfOutputVarName from command_runner in the getattr(command_runner, tfOutputVarName) command
  if outputVar.count("=") == 1:
    outputVar = outputVar[outputVar.index("=")+1:]
  if outputVar.count(":") == 1:
    outputVar = outputVar[outputVar.index(":")+1:]
  if tool == 'terraform':
    varSnip = " -var=\"" +inputVar + "="+outputVar+"\""  
  elif tool == 'packer':
    varSnip = " -var \"" +inputVar + "="+outputVar+"\""  
  varSnip = formatPathForOS(varSnip)
  return varSnip

def getSecretVarFromKeys(tool, keyDir, r, instanceName, cloud_vendor):
  if platform.system() == "Windows":
    if keyDir[:-1] != "\\":
      keyDir = keyDir + "\\"
  if platform.system() == "Linux":
    if keyDir[:-1] != "/":
      keyDir = keyDir + "/"
  yamlKeysPath = keyDir.replace("\\\\","\\")
  yamlKeysPath = formatPathForOS(yamlKeysPath)
  if cloud_vendor == "aws":
    yamlKeysFileAndPath = yamlKeysPath + 'iamUserKeys.yaml'
  if cloud_vendor == "azure":
    yamlKeysFileAndPath = yamlKeysPath + 'adUserKeys.yaml'
  else:
    quitStr = "Cloud vendor " + "\"" + cloud_vendor + "\" is not currently supported.  Halting program so you can fix your configuration. "
  pub = config_cliprocessor.inputVars.get("pub")
  sec = config_cliprocessor.inputVars.get("sec")
  tfInputVarName = r[0]
  sourceField = r[4]
  secretLine = 'empty'
  keypairs_dict = {}
  with open(yamlKeysFileAndPath) as f:
    for line in f:
      if ("#" not in line) and (len(line.replace(" ", "")) > 1):
        lineParts = line.split(":",1)
        keypairs_dict[lineParts[0]] = lineParts[1].replace("\n","").strip('\"')
  myItems = keypairs_dict.items()
  for key, value in myItems:  
    if (value[0] == "\"") and (value[-1] == "\""):
      #eliminate any pre-existing double quotes to avoid downstream errors.
      value = value[1:]
      value = value[:-1]
    if key == sourceField:
      if tool == "terraform":
        secretLine = tfInputVarName + "=\""+value+"\"\n"
      elif tool == "packer":
        secretLine = tfInputVarName + "="+value
  if 'empty' in secretLine:
    logString = "Not able to find matching secret value.  Make sure to add better error handling here."
    logWriter.writeLogVerbose("acm", logString)
  return secretLine

def getTypeOfLine(moduleConfigFileAndPath):
  typeOfLine = "NA"
  typeCounter = 0
  c = open(moduleConfigFileAndPath,'r')
  o = csv.reader(c)
  for r in o:
    #Only check the line whose inputVarName is NA
    if r[0] == 'NA':
      typeOfLine = r[2]
      typeCounter += 1
  if typeCounter > 1 or typeCounter == 0:
    logString = "Invalid number of config rows in input file: " +typeCounter+ ".  Add a validation script for the config file."
    logWriter.writeLogVerbose("acm", logString)
  return typeOfLine

def getSecretVars(tool, keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, instanceName):
  secretVarLines = []
  typeOfLine = getTypeOfLine(moduleConfigFileAndPath)
  c = open(moduleConfigFileAndPath,'r')
  o = csv.reader(c)
  keySource = config_cliprocessor.inputVars.get("keySource")
  pub = config_cliprocessor.inputVars.get("pub")
  sec = config_cliprocessor.inputVars.get("sec")
  for r in o:
    inputVarName = r[0]
    if r[5] == 'yes':
      if r[1] == 'infrastructureConfig.yaml':
        typeOfLine = r[2]
        print("instanceName is: ", instanceName)
        print("... about to call getSecretVarFromUserConfig() ")
        secretVarLine = getSecretVarFromUserConfig(tool, r, yamlInfraFileAndPath, instanceName)
        if 'empty' not in secretVarLine:
          secretVarLines.append(secretVarLine.replace(" ", ""))
      elif (r[1] == 'generatedKeys.yaml') or (r[1] == 'generatedAzureKeys.yaml') or (r[1] == 'iamUserKeys.yaml') or (r[1] == 'adUserKeys.yaml'):
        if keySource == "keyFile":
          secretVarLine = getSecretVarFromKeys(tool, keyDir, r, instanceName, cloud_vendor)
          if 'empty' not in secretVarLine:
            secretVarLines.append(secretVarLine.replace(" ", ""))
  if keySource == "keyVault":
    publicKeyLine = "_public_access_key=\""+pub+"\"\n"
    secretVarLines.append(publicKeyLine.replace(" ", ""))
    secretKeyLine = "_secret_access_key=\""+sec+"\"\n"
    secretVarLines.append(secretKeyLine.replace(" ", ""))
#2.2.2022  import controller_terraform
#2.2.2022  if len(controller_terraform.backendFile) > 1:
#2.2.2022    tfBackendFileAndPath = controller_terraform.backendFile
  tfvarsFileAndPath = config_cliprocessor.inputVars.get("tfvarsFileAndPath")
  if len(secretVarLines)>0:
    if tool == 'terraform':
      f = open(tfvarsFileAndPath, "w")
      for line in secretVarLines:
        f.write(line)
      f.close()
      varSnip = " -var-file=\"" + tfvarsFileAndPath +"\""
    elif tool == 'packer':
      packerVarsFileAndPath=tfvarsFileAndPath.replace(".tfvars",".json")
      secretVarDict = dict(s.split('=',1) for s in secretVarLines)
      out_file = open(packerVarsFileAndPath,'w+')
      json.dump(secretVarDict,out_file)
      varSnip = " -var-file=\"" + packerVarsFileAndPath +"\""
  else:
    logString = "ERROR: Required secrets were not found inside: " + str(tfvarsFileAndPath)
    logWriter.writeLogVerbose("acm", logString)
    exit(1)
  c.close()
  varSnip = formatPathForOS(varSnip)
  return varSnip

def getBackendVars(tool, keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, foundationInstanceName, callInstanceName, instanceName):
  secretVarLines = []
  typeOfLine = getTypeOfLine(moduleConfigFileAndPath)
  c = open(moduleConfigFileAndPath,'r')
  o = csv.reader(c)
  keySource = config_cliprocessor.inputVars.get("keySource")
  pub = config_cliprocessor.inputVars.get("pub")
  sec = config_cliprocessor.inputVars.get("sec")
  for r in o:
    inputVarName = r[0]
    if r[5] == 'backend':
      if r[1] == 'infrastructureConfig.yaml':
        typeOfLine = r[2]
        secretVarLine = getSecretVarFromUserConfig(tool, r, yamlInfraFileAndPath, instanceName)
        if 'empty' not in secretVarLine:
          secretVarLines.append(secretVarLine.replace(" ", ""))
      elif (r[1] == 'generatedKeys.yaml') or (r[1] == 'generatedAzureKeys.yaml') or (r[1] == 'iamUserKeys.yaml') or (r[1] == 'adUserKeys.yaml'):
        if keySource == "keyFile":
          secretVarLine = getSecretVarFromKeys(tool, keyDir, r, foundationInstanceName, cloud_vendor)
          if 'empty' not in secretVarLine:
            secretVarLines.append(secretVarLine.replace(" ", ""))
  if keySource == "keyVault":
    publicKeyLine = "_public_access_key=\""+pub+"\"\n"
    secretVarLines.append(publicKeyLine.replace(" ", ""))
    secretKeyLine = "_secret_access_key=\""+sec+"\"\n"
    secretVarLines.append(secretKeyLine.replace(" ", ""))
  if len(secretVarLines)>0:
    tfBackendFileAndPath = config_cliprocessor.inputVars.get("tfBackendFileAndPath")
    if tool == 'terraform':
      f = open(tfBackendFileAndPath, "w")
      for line in secretVarLines:
        f.write(line)
      f.close()
      varSnip = " -backend-config=\"" + tfBackendFileAndPath +"\""
    else:
      logString = "Invalid tool.  There is an error in your configuration which caused the getBackendVars() function to be called for a tool that is not terraform.  "
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
  c.close()
#  quit(keyDir)
#  quit(moduleConfigFileAndPath)
  varSnip = formatPathForOS(varSnip)
  return varSnip

def getBackendVarsFragment(tool, keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, foundationInstanceName, parentInstanceName, callInstanceName, org, instanceName):
  varSnip = "empty"
  varsFragment = ''
  bkndVarSnip = getBackendVars(tool, keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, foundationInstanceName, callInstanceName, instanceName)
  if bkndVarSnip != 'empty':
    if bkndVarSnip is not None:
      varsFragment = varsFragment + bkndVarSnip
  return varsFragment

def getVarsFragment(tool, keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, foundationInstanceName, parentInstanceName, callInstanceName, org):
  varSnip = "empty"
  varsFragment = ''
  varsFragment = readModuleConfigFile(tool, yamlInfraFileAndPath, moduleConfigFileAndPath, parentInstanceName, callInstanceName, org)
  varSnip = getSecretVars(tool, keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, foundationInstanceName)
  if varSnip != 'empty':
    if varSnip is not None:
      varsFragment = varsFragment + varSnip
  return varsFragment

def readModuleConfigFile(tool, yamlInfraFileAndPath, moduleConfigFileAndPath, parentInstanceName, callInstanceName, org):
  varSnip = "empty"
  varsFragment = ''
  c = open(moduleConfigFileAndPath,'r')
  o = csv.reader(c)
  for r in o:
    if r[1] == 'infrastructureConfig.yaml':
      if r[5] == 'no':
        varSnip = getVarFromUserConfig(tool, r, yamlInfraFileAndPath, parentInstanceName, callInstanceName, org)
        if varSnip != 'empty':
          varsFragment = varsFragment + varSnip
    elif r[1] == 'foundationOutput':
      if r[5] == 'no':
        varSnip = getVarFromOutput(tool, r, callInstanceName)
        if varSnip != 'empty':
          varsFragment = varsFragment + varSnip
    elif r[1] == 'customFunction':
      if r[5] == 'no':
        if r[0] == 'adminPublicIP':
          cidrBlock = getAdminCidr()
          if tool == 'terraform':
            varSnip = " -var=\"" +r[0] + "="+cidrBlock +"\""  
          elif tool == 'packer':
            varSnip = " -var \"" +r[0] + "="+cidrBlock +"\""
          varSnip = formatPathForOS(varSnip)
          varsFragment = varsFragment + varSnip
  c.close()
  return varsFragment

def getAdminCidr():
  try: 
    adminCidr1 = (requests.get('https://api.ipify.org').text).rstrip() + "/32"
    adminCidr2 =  (requests.get('http://ipv4.icanhazip.com').text).rstrip() + "/32"
  except requests.exceptions.ConnectionError: 
    sys.exit("One of the external validators of the admin IP address failed to respond to a validation request.  This might be a temporary error and might work if you try again.")
  if adminCidr1 == adminCidr2:  
    cidrBlocks = adminCidr1
    logString = "The external IP of the agent was validated by two independent sources. "
    logWriter.writeLogVerbose("acm", logString)
  else:
    logString = "The external IP of the agent could not be validated by two independent sources.  We therefore cannot complete security configuration.  Check the logs to research what happened. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  return cidrBlocks

def getKeyFileAndPath(keyDir, type_name, cloud_vendor):
  yaml_keys_file_and_path = 'invalid'
  if platform.system() == "Windows":
    if keyDir[:-1] != "\\":
      keyDir = keyDir + "\\"
  if platform.system() == "Linux":
    if keyDir[:-1] != "/":
      keyDir = keyDir + "/"
  keyDir = formatPathForOS(keyDir)
  dirOfSourceKeys = keyDir
  if type_name == 'admin':  
    if cloud_vendor == 'aws':
      yaml_keys_file_and_path = dirOfSourceKeys + config_cliprocessor.inputVars.get('nameOfYamlKeys_IAM_File')
    elif cloud_vendor == 'azure':
      yaml_keys_file_and_path = dirOfSourceKeys + 'adUserKeys' + '.yaml'
  else:  
    if cloud_vendor == 'aws':
      yaml_keys_file_and_path = dirOfSourceKeys + config_cliprocessor.inputVars.get('nameOfYamlKeys_AWS_Network_File')
    elif cloud_vendor == 'azure':
      yaml_keys_file_and_path = dirOfSourceKeys + config_cliprocessor.inputVars.get('nameOfYamlKeys_Azure_Network_File')
  return yaml_keys_file_and_path

#This new function is for getting the specific location for the keys that the admin module creates for each system
def getKeyFileLocation(instance_name, cloud_vendor):
  outputDir = config_cliprocessor.inputVars.get("dirOfOutput") + instance_name + "\\"
  outputDir = formatPathForOS(outputDir)
  if not os.path.exists(outputDir):
    os.makedirs(outputDir)
  keys_file_and_path = 'invalid'
  if cloud_vendor == 'aws':
    keys_file_and_path = outputDir + config_cliprocessor.inputVars.get('nameOfYamlKeys_IAM_File')
  elif cloud_vendor == 'azure':
    keys_file_and_path = outputDir + 'adUserKeys' + '.yaml'
  return keys_file_and_path

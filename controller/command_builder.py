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
import datetime

import command_builder
import command_runner
import logWriter
import config_cliprocessor
import config_fileprocessor
import controller_terraform

def getSlashForOS():
  if platform.system() == 'Windows':
    return '\\'
  else:
    return '/'

def formatPathForOS(input):
  if platform.system() == "Windows":
    input = input.replace('/','\\')
    input = input.replace('\\\\','\\')
    input = input.replace('\\\\\\','\\')
  elif platform.system() == "Linux":
    if '\\' in input:
      print('*** trap 1')
    if '\\\\' in input:
      print('*** trap 2')
    input = input.replace('\\','/')
    input = input.replace('//','/')
    input = input.replace('///','/')
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
              print('mMmMmMmM ... varSnip is: ', varSnip)
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
#  varSnip = formatPathForOS(varSnip)
  print('NnNnNnNnNnNnNnNn .....  varSnip is: ', varSnip)
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
      if inputVar == 'keySourceFile':
        if props == 'keySourceFile':
          if aType.get(props) == '$SOURCEKEYS':
            keySourceFile = config_cliprocessor.inputVars.get('sourceKeys')+command_builder.getSlashForOS()+'keys.yaml'
          else:
            keySourceFile = aType.get(props)
          if tool == 'terraform':
            varSnip = " -var=\"" +inputVar + "="+keySourceFile +"\""  
          elif tool == 'packer':
            varSnip = " -var \"" +inputVar + "="+keySourceFile +"\""  
          print('jjj  varSnip is: ', varSnip)
#          quit('found keySourceFile! ')
      elif inputVar == 'cidrBlocks': 
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
                varSnip = formatPathForOS(varSnip)
#            elif sourceField == 'keySourceFile':
#              print('... mmm r is: ', str(r))
#              print('prop is: ', prop)
#              print('str(props.get(prop)) is: ', str(props.get(prop)))
#              quit()
#              configAndSecretsPath = config_cliprocessor.inputVars.get("configAndSecretsPath")
#              pathStr = configAndSecretsPath + props.get(prop) + "\startup-script-demo.sh"
#              pathStr = formatPathForOS(pathStr)
#              if tool == 'terraform':
#                varSnip = " -var=\"" +inputVar + "="+str(pathStr) +"\""  
#              elif tool == 'packer':
#                varSnip = " -var \"" +inputVar + "="+str(pathStr) +"\""  
#              varSnip = formatPathForOS(varSnip)
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
                  userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
                  relativePathAndFile = str(props.get(prop))
                  if platform.system() == "Windows":
                    userCallingDir = formatPathForOS(userCallingDir)
                    relativePathAndFile = formatPathForOS(relativePathAndFile)
                  varSnip = " -var=\"" +inputVar + "="+userCallingDir + relativePathAndFile +"\""  
                  varSnip = formatPathForOS(varSnip)
                else:
                  if callInstanceName == "azdoAgents":
                    print("prop is: ", prop)
                  varSnip = " -var=\"" +inputVar + "="+str(props.get(prop)) +"\""  
              elif tool == 'packer':
                if sourceField == 'init_script':
                  userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
                  relativePathAndFile = str(props.get(prop))
                  if platform.system() == "Windows":
                    userCallingDir = formatPathForOS(userCallingDir)
                    relativePathAndFile = formatPathForOS(relativePathAndFile)
                  varSnip = " -var \"" +inputVar + "="+userCallingDir + relativePathAndFile +"\""  
                  varSnip = formatPathForOS(varSnip)
                else:
                  varSnip = " -var \"" +inputVar + "="+str(props.get(prop)) +"\""  
#  if 'cidr' not in varSnip: #Consider indenting the next single line.  But for now we are commenting it to see if the new changes above are sufficient.
#  varSnip = formatPathForOS(varSnip)
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
              else:
                if instance == sourceField:
                  if instances.get(sourceField) != None:
                    if tool == 'packer':
                      varLine = inputVar + "="+ instances.get(sourceField)
                    else:
                      if instance.get("instanceName") == instanceName:
                        varLine = inputVar + "=\""+ instances.get(sourceField) +"\"\n"
  else:  
    logString = "TemplateName is malformed.  Halting program so you can debug.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
#  quit("BREAKPOINT for secret from user config.  ")
  return varLine

def getVarFromOutput(tool, r, callInstanceName):
  inputVar = r[0]
  tfOutputVarName = r[4]
#  thismodule = sys.modules[__name__]
  if (tool=='terraform') or (tool=='packer'):
    print('controller_terraform.foundationApply is: ', str(controller_terraform.foundationApply))
    print('controller_terraform.tfOutputDict is: ', str(controller_terraform.tfOutputDict))
    for key in controller_terraform.tfOutputDict:
      print(key, " is: ", controller_terraform.tfOutputDict.get(key))
      if key == inputVar:
        print('1 match.')
      if key == tfOutputVarName:
#        print('2 match.')
        outputVar = controller_terraform.tfOutputDict.get(key)
#      if controller_terraform.tfOutputDict.get(key) == inputVar:
#        print('3 match.')
#      if controller_terraform.tfOutputDict.get(key) == tfOutputVarName:
#        print('4 match.')
#    quit('BREAKPOINT TO DEBUG NEW TERRAFORM OUTPUT.  ')
#  if (tool=='packer'):
#    outputVar = getattr(command_runner, tfOutputVarName)
#    outputVar = outputVar.replace('"', '')
#    outputVar = outputVar.replace(',', '')
#    outputVar = outputVar.replace(' ', '')
#  if callInstanceName == "azdoAgents":
#    print("... outputVar is: ", outputVar)
  #The next 4 lines are a workaround for a bug that had been passing corrupted values for tfOutputVarName from command_runner in the getattr(command_runner, tfOutputVarName) command
  if outputVar.count("=") == 1:
    outputVar = outputVar[outputVar.index("=")+1:]
  if outputVar.count(":") == 1:
    outputVar = outputVar[outputVar.index(":")+1:]
  if tool == 'terraform':
    varSnip = " -var=\"" +inputVar + "="+outputVar+"\""  
  elif tool == 'packer':
    varSnip = " -var \"" +inputVar + "="+outputVar+"\""  
#    print('varSnip is: ', varSnip)
#    print('controller_terraform.foundationApply is: ', controller_terraform.foundationApply)
#    print('controller_terraform.tfOutputDict is: ', str(controller_terraform.tfOutputDict))
#    print('packer trap.')
#    sys.exit(1)
  #varSnip = formatPathForOS(varSnip)
  return varSnip

def getVarFromCloudFormationOutput(r, infraConfigFileAndPath):
  inputVar = r[0]
  outputVarName = r[4]
  print('inputVar is: ', inputVar)
  print('outputVarName is: ', outputVarName)
#  thismodule = sys.modules[__name__]
#  quit('BREAKPOINT INSIDE command_builder.getVarFromCloudFormationOutput(r, infraConfigFileAndPath)')
  stackName = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'stackName')
  getOutputsCommand = 'aws cloudformation describe-stacks --stack-name '+stackName
  jsonStatus = command_runner.getShellJsonResponse(getOutputsCommand)
#  print('outputs response from describe stack command is: ', str(jsonStatus))
  jsonStatus = yaml.safe_load(jsonStatus)
  print('---')
  print('stackName is: ', stackName)
  print('---')
#  print(jsonStatus)
  stacks = jsonStatus['Stacks']
  print('number of stacks returned is: ', len(stacks))
  #print('outputs is: ', str(outputs))
  for stack in stacks:
#    print('This stack is: ', str(stack))
    for output in stack['Outputs']:
      print('output is: ', str(output))
      print('output["OutputKey"] is: ', str(output['OutputKey']))
      if outputVarName == output['OutputKey']:
        return 'ParameterKey='+outputVarName+',ParameterValue='+output['OutputValue'].replace(' ','')+' '
  #varSnip = formatPathForOS(varSnip)
  return 'empty' #varSnip

def getSecretVarFromKeys(tool, keyDir, r, instanceName, cloud_vendor):
  if platform.system() == "Windows":
    if keyDir[:-1] != "\\":
      keyDir = keyDir + "\\"
  if platform.system() == "Linux":
    if keyDir[:-1] != "/":
      keyDir = keyDir + "/"
  yamlKeysPath = keyDir.replace("\\\\","\\")
  yamlKeysPath = formatPathForOS(yamlKeysPath)
  yamlKeysFileAndPath = yamlKeysPath + 'keys.yaml'
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
  print('myItems is: ', str(myItems))
#  if r[0] == 'KeyName':
#    quit('Following KeyName')

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
      elif tool == 'arm':
        valDict = { "value": value  }
        secretLine = '        '+tfInputVarName+': '+str(valDict)
      elif tool == 'cloudformation':
#        valDict = { "value": value  }
        secretLine = tfInputVarName+'='+str(value).replace(' ','')
        secretLine = 'ParameterKey='+tfInputVarName+',ParameterValue='+str(value).replace(' ','')
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
  print('............... bbbbb  tfvarsFileAndPath is: ', tfvarsFileAndPath)
  return varSnip

def getBackendVars(tool, keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, foundationInstanceName, callInstanceName, instanceName):
  secretVarLines = []
#  print('moduleConfigFileAndPath is: ', moduleConfigFileAndPath)
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

def getArmParamsFile(keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, instanceName,outputDict={}):
  tool = 'arm'
  secretVarLines = []
  c = open(moduleConfigFileAndPath,'r')
  o = csv.reader(c)
  keySource = config_cliprocessor.inputVars.get("keySource")
  for r in o:
    inputVarName = r[0]
    print('inputVarName is: ', inputVarName)
    if r[1] == 'infrastructureConfig.yaml':
      if 'image' in moduleConfigFileAndPath:
        print('r is: ', r)
      secretVarLine = getArmParamFileLine(r, yamlInfraFileAndPath, instanceName,outputDict)
      if 'empty' not in secretVarLine:
        secretVarLines.append(secretVarLine.replace(" ", ""))
    elif (r[1] == 'generatedKeys.yaml') or (r[1] == 'generatedAzureKeys.yaml') or (r[1] == 'iamUserKeys.yaml') or (r[1] == 'adUserKeys.yaml'):
      if keySource == "keyFile":
        secretVarLine = getSecretVarFromKeys(tool, keyDir, r, instanceName, cloud_vendor)
        if 'empty' not in secretVarLine:
          secretVarLines.append(secretVarLine.replace(" ", ""))
    elif r[1] == 'customFunction':
      print('-------------- customFunction ---------- ')
      if r[5] == 'no':
        if r[0] == 'adminPublicIP':
          cidrBlock = getAdminCidr()
          valDict = { "value": cidrBlock }
          secretVarLine = '        '+r[0]+':'+str(valDict)
          secretVarLines.append(secretVarLine.replace(" ", ""))
        if r[0] == 'currentDateTimeAlphaNumeric':
          dateTimeCode = str(datetime.datetime.now()).replace(' ','').replace('-','').replace(':','').replace('.','')
          valDict = { "value": dateTimeCode }
          secretVarLine = '        '+r[0]+':'+str(valDict)
          secretVarLines.append(secretVarLine.replace(" ", ""))
        if r[0] == 'imgBuilderId':
          subscriptionId = outputDict['subscriptionId']
          resourceGroupName = outputDict['resourceGroupName']
          identityName = outputDict['identityName']
          imgBuilderId='/subscriptions/'+subscriptionId+'/resourcegroups/'+resourceGroupName+'/providers/Microsoft.ManagedIdentity/userAssignedIdentities/'+identityName
          print('subscriptionId is: ', subscriptionId)
          print('resourceGroupName is: ', resourceGroupName)
          print('identityName is: ', identityName)
          print('imgBuilderId is: ', imgBuilderId)
          valDict = { "value": imgBuilderId }
          secretVarLine = '        '+r[0]+':'+str(valDict)
          secretVarLines.append(secretVarLine.replace(" ", ""))
        if r[0] == 'foundationResourceGroupName':
          getRgNameCmd = 'az deployment group show -g '+outputDict['resourceGroupName']+' -n '+outputDict['deploymentName']+' --query properties.outputs.'+r[0]+'.value'
          print('outputDict is: ', str(outputDict))
          print('getRgNameCmd is: ', getRgNameCmd)
          foundationResourceGroupName = command_runner.getShellJsonResponse(getRgNameCmd)
          valDict = { "value": foundationResourceGroupName }
          secretVarLine = '        '+r[0]+':'+str(valDict)
          secretVarLines.append(secretVarLine.replace(" ", "").replace('"','').replace('\\n',''))
#          print('secretVarLines is: ', str(secretVarLines))
#          quit('neom')

  print('len(secretVarLines) is: ', len(secretVarLines))
  tfvarsFileAndPath = config_cliprocessor.inputVars.get("tfvarsFileAndPath")
  print('tfvarsFileAndPath is: ', tfvarsFileAndPath)
  if len(secretVarLines)>0:
      armVarsFileAndPath=tfvarsFileAndPath.replace(".tfvars",".json")
      print('type(secretVarLines) is: ', type(secretVarLines))
      print('secretVarLines is: ', secretVarLines)
      varsDict = dict()   
      for line in secretVarLines:
        varsDict[line.split(":", 1)[0]] = json.loads(line.split(":", 1)[1].replace('\'','"'))
      paramsDict = {
        "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
        "contentVersion": "1.0.0.0",
        "parameters": varsDict
      }
#      print('paramsDict is: ', str(paramsDict))
#      quit('897!')
      out_file = open(armVarsFileAndPath,'w+')
      json.dump(paramsDict,out_file)
      varSnip = " --parameters " + armVarsFileAndPath 
  else:
    logString = "ERROR: Required secrets were not found inside: " + str(tfvarsFileAndPath)
    logWriter.writeLogVerbose("acm", logString)
    exit(1)
  c.close()
  varSnip = formatPathForOS(varSnip)
#  print('varSnip is: ', varSnip)
#  quit('m--->')
  return varSnip

def getCloudFormationParamsFile(keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, caller, serviceType, instanceName,outputDict={}):
  tool = 'cloudformation'
  numVars = 0
  secretVars = ''
  print('moduleConfigFileAndPath is: ', moduleConfigFileAndPath)
#  quit('xxx!')
  c = open(moduleConfigFileAndPath,'r')
  o = csv.reader(c)
  keySource = config_cliprocessor.inputVars.get("keySource")
  print('.......................................')
  for r in o:
    inputVarName = r[0]
    print('r[0] is: ', r[0])
    print('r[1] is: ', r[1])
#    if (r[1] != 'source') and (r[1] != 'NA') and (r[1] != 'infrastructureConfig.yaml'):
#      quit('ooo!')
    if r[1] == 'infrastructureConfig.yaml':
      secretVarLine = getCloudFormationParamFileLine(r, yamlInfraFileAndPath, instanceName,outputDict)
      if 'empty' not in secretVarLine:
        secretVars = secretVars+' '+secretVarLine
        numVars +=1
    elif r[1] == 'foundationOutput':
      if r[5] == 'no':
        varSnip = getVarFromCloudFormationOutput(r, yamlInfraFileAndPath)
        if varSnip != 'empty':
          secretVars = secretVars + varSnip
#      print('secretVars is: ', secretVars)
#      quit('fff!')
    elif (r[1] == 'generatedKeys.yaml') or (r[1] == 'generatedAzureKeys.yaml') or (r[1] == 'iamUserKeys.yaml') or (r[1] == 'adUserKeys.yaml'):
      if keySource == "keyFile":
        secretVarLine = getSecretVarFromKeys(tool, keyDir, r, instanceName, 'aws')
        if 'empty' not in secretVarLine:
          secretVars = secretVars+' '+secretVarLine
          numVars +=1
#         secretVarLines.append(secretVarLine.replace(" ", ""))
    elif r[1] == 'customFunction':
      if r[5] == 'no':
        if r[0] == 'adminPublicIP':
          cidrBlock = getAdminCidr()
#          valDict = { "value": cidrBlock }
          secretVarLine = r[0]+'='+str(cidrBlock).replace(' ','')
          secretVars = secretVars+' '+secretVarLine
          numVars +=1
        if r[0] == 'currentDateTimeAlphaNumeric':
          dateTimeCode = str(datetime.datetime.now()).replace(' ','').replace('-','').replace(':','').replace('.','')
#          valDict = { "value": dateTimeCode }
          secretVarLine = r[0]+'='+str(dateTimeCode).replace(' ','')
          secretVars = secretVars+' '+secretVarLine
          numVars +=1
        if r[0] == 'ImageId':
#          print('outputDict is: ', outputDict)
#          print('keyDir is: ', keyDir)
          myList = ['ImageOwnerId','ImageOwnerId','ImageOwnerId','ImageOwnerId','ImageOwnerId',]
          imageOwnerIdLine = getSecretVarFromKeys(tool, keyDir, myList, instanceName, 'aws')
          imageOwnerId = imageOwnerIdLine.split('=')[2]
          listImagesCommand = 'aws ec2 describe-images --owners '+imageOwnerId
          logString = 'listImagesCommand is: '+listImagesCommand
          logWriter.writeLogVerbose("acm", logString)
          jsonStatus = command_runner.getShellJsonResponse(listImagesCommand)
          logString = 'Initial response from listImagesCommand is: '+str(jsonStatus)
          logWriter.writeLogVerbose("acm", logString)
          images = yaml.safe_load(jsonStatus)['Images']
          nameRoot = outputDict['ImageNameRoot']
          imageNamesList = []
          datesList = []
          imageNameIdDict = {}
          for image in images:
#            print('image is: ', image)
            if (image['State'] == 'available') and (nameRoot in image['Name']):
#              print(image['ImageId'])
#              print(image['Name'])
              imageNamesList.append(image['Name'])
              imageNameIdDict[image['Name']] = image['ImageId']
          for name in imageNamesList:
            datesList.append(name.split('_')[1])
#          print('imageNamesList is: ', imageNamesList)
#          print('datesList is: ', datesList)
          mostRecentDate = max(datesList)
          mostRecentImageName = nameRoot+'_'+mostRecentDate
          imageId = imageNameIdDict[mostRecentImageName]
#          print('imageId is: ', imageId)
#          print('imageOwnerId is: ', imageOwnerId)
#          secretVarLine = r[0]+'='+imageId
          secretVarLine = 'ParameterKey='+r[0]+',ParameterValue='+imageId 
          secretVars = secretVars+' '+secretVarLine
          numVars +=1
#          print('secretVars is: ', secretVars)
#          quit('get ImageId customFunction')
  tfvarsFileAndPath = config_cliprocessor.inputVars.get("tfvarsFileAndPath")
  if numVars>0:
      #armVarsFileAndPath=tfvarsFileAndPath.replace(".tfvars",".json")
      #varsDict = dict()   
      #for line in secretVarLines:
      #  varsDict[line.split(":", 1)[0]] = json.loads(line.split(":", 1)[1].replace('\'','"'))
      #paramsDict = {
      #  "parameters": varsDict
      #}
      #out_file = open(armVarsFileAndPath,'w+')
      #json.dump(paramsDict,out_file)
      varSnip = " --parameters "+secretVars    #file://" + formatPathForOS(armVarsFileAndPath) 
  else:
    logString = "ERROR: Required secrets were not found inside: " + str(tfvarsFileAndPath)
    logWriter.writeLogVerbose("acm", logString)
    exit(1)
  c.close()
#  quit('BREAKPOINT TO DEBUG pqrs')
  return varSnip

def getArmParamFileLine(r, yamlInfraFileAndPath, instanceName, outputDict):
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
                valDict = { "value": type.get(props)  }
                varLine = '        '+inputVar+':'+str(valDict) 
            else:
              for prop in props:
                if re.match(sourceField, prop):
                  valDict = { "value": props.get(prop)  }
                  varLine = '        '+inputVar+':'+str(valDict)
  elif myType.count('/') == 1:
    parent = myType.split('/', 1)[0]
    child = myType.split('/', 1)[1]
    print('parent and child are: ',parent, ' : ', child)
    with open(yamlInfraFileAndPath) as f:  
      my_dict = yaml.safe_load(f)
      for key, value in my_dict.items():  
        if re.match(parent, key):
          types = my_dict.get(key)
          for type in types:
            instances = types.get(type)
            print("---------------------------------------------------------")
            for instance in instances:
              print("... instanceName is: ", instanceName)
              print("... instance is: ", instance)
              print("r is: ", r)
              if not isinstance(instance, str):
                print('Not a string!')
                print('instance.get(sourceField) is: ', instance.get(sourceField) )
#                quit('-1')
                if instance.get(sourceField) != None:
                  print('instance.get("instanceName") is: ', instance.get("instanceName"))
                  print('instanceName is: ', instanceName)
#                  quit('-3')
                  if instance.get("instanceName") == instanceName:
                    if ('hasImageBuilds' in outputDict.keys()) and ((sourceField == 'imageTemplateName') or (sourceField == 'imageName')):
                      print('hasImageBuilds is in dict.')
                      print('inputVar is: ', inputVar)
                      print('sourceField is: ', sourceField)
                      print('instance.get(sourceField) is : ', instance.get(sourceField))
                      print('outputDict["dateTimeCode"] is: ', outputDict["dateTimeCode"])
#                        sourceField = sourceField+outputDict["dateTimeCode"]
                      valDict = { "value": instance.get(sourceField)+'_'+outputDict["dateTimeCode"]  }
                      varLine = '        '+inputVar+':'+str(valDict) 
#                        quit('hasImageBuilds is True!')
                    else:
                      if inputVar == 'imageName':
                        if 'typeParent' in outputDict.keys():
                          if outputDict['typeParent'] == 'systems':
                            print("outputDict['typeParent'] is: ", outputDict['typeParent'])
                            listImagesCmd = 'az image list --resource-group '+outputDict['resourceGroupName']
                            print('listImagesCmd is: ', listImagesCmd)
                            jsonStatus = command_runner.getShellJsonResponse(listImagesCmd)
                            print('jsonStatus is: ', str(jsonStatus))
                            jsonStatus = json.loads(jsonStatus)
                            datepartsList = []
                            for image in jsonStatus:
                              if instance.get(sourceField) in image['name']:
                                datepart = image['name'].split('_')[1]
                                datepartsList.append(datepart)
#                              print('... image is: ', str(image))
                            print('datepartsList is: ', str(datepartsList))
                            mostRecentDate = max(datepartsList)
                            imgName = instance.get(sourceField)+'_'+str(mostRecentDate)
                            print('imgName is: ', imgName)
                            valDict = { "value": imgName  }
                            varLine = '        '+inputVar+':'+str(valDict) 
#                            quit('234!')
#                        quit('kokopuff')
                        print("sourceField is: ", sourceField)
#                      quit('-2')
                      else: 
                        valDict = { "value": instance.get(sourceField)  }
                        varLine = '        '+inputVar+':'+str(valDict) 
              else:
                print('String!')
                if instance == sourceField:
                  if instances.get(sourceField) != None:
                    if instance.get("instanceName") == instanceName:
                      valDict = { "value": instances.get(sourceField)  }
                      varLine = '        '+inputVar+':'+str(valDict)
              if inputVar == 'imageName':
                print('r is: ', r)
                print('outputDict.keys() is: ', str(outputDict.keys()))
#                quit('b!')
  else:  
    logString = "TemplateName is malformed.  Halting program so you can debug.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
#  quit("BREAKPOINT for secret from user config.  ")
  return varLine

def getCloudFormationParamFileLine(r, yamlInfraFileAndPath, instanceName, outputDict):
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
#        print('key is: ', key)
        if re.match(myType, key):
          print('myType is: ', myType)
          type = my_dict.get(key)
          for props in type:
            if isinstance(props, str):
              if re.match(sourceField, props):
                varLine = 'ParameterKey='+inputVar+',ParameterValue='+type.get(props).replace(' ','')
            else:
              for prop in props:
                if re.match(sourceField, prop):
                  varLine = 'ParameterKey='+inputVar+',ParameterValue='+props.get(prop).replace(' ','')
    if (inputVar == 'SSHLocation') or (inputVar == 'InstanceType'):
      print('myType end is: ', myType)
      print('varLine is: ', varLine)
      quit('3!')
  elif myType.count('/') == 1:
    parent = myType.split('/', 1)[0]
    child = myType.split('/', 1)[1]
    print('parent and child are: ',parent, ' : ', child)
    with open(yamlInfraFileAndPath) as f:  
      my_dict = yaml.safe_load(f)
      for key, value in my_dict.items():  
        if re.match(parent, key):
          types = my_dict.get(key)
          for type in types:
            instances = types.get(type)
            print("---------------------------------------------------------")
            for instance in instances:
              if not isinstance(instance, str):
                if instance.get(sourceField) != None:
                  print('instance.get(sourceField) is: ', instance.get(sourceField))
                  print('x sourceField is: ', sourceField)
                  print('x instance.get("instanceName") is: ', instance.get("instanceName"))
                  print('x instanceName is: ', instanceName)
                  if instance.get("instanceName") == instanceName:
                    if ('hasImageBuilds' in outputDict.keys()) and ((sourceField == 'imageTemplateName') or (sourceField == 'imageName')):
#                      valDict = { "value": instance.get(sourceField)+outputDict["dateTimeCode"]  }
#                      varLine = inputVar+'='+str(instance.get(sourceField)+outputDict["dateTimeCode"]).replace(' ','')
                      varLine = 'ParameterKey='+inputVar+',ParameterValue='+str(instance.get(sourceField)+outputDict["dateTimeCode"]).replace(' ','')
#                        quit('hasImageBuilds is True!')
                    else:
                      print("sourceField is: ", sourceField)
#                      if (sourceField == 'InstanceType') or (sourceField == 'SSHLocation'):
#                        quit('-2')
#                      valDict = { "value": instance.get(sourceField)  }
#                      varLine = inputVar+'='+str(instance.get(sourceField)).replace(' ','')
                      varLine = 'ParameterKey='+inputVar+',ParameterValue='+str(instance.get(sourceField)).replace(' ','')
              else:
                print('String!')
                if instance == sourceField:
                  if instances.get(sourceField) != None:
                    if instance.get("instanceName") == instanceName:
#                      valDict = { "value": instances.get(sourceField)  }
#                      varLine = inputVar+'='+str(instances.get(sourceField)).replace(' ','')
                      varLine = 'ParameterKey='+inputVar+',ParameterValue='+str(instances.get(sourceField)).replace(' ','')
  else:  
    logString = "TemplateName is malformed.  Halting program so you can debug.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
#  quit("BREAKPOINT for secret from user config.  ")
  return varLine


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
  print('iiiii varsFragment is: ', varsFragment)
  varSnip = getSecretVars(tool, keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, foundationInstanceName)
  if varSnip != 'empty':
    if varSnip is not None:
      varsFragment = varsFragment + varSnip
  return varsFragment

def getArmVarsFragment(keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, foundationInstanceName, parentInstanceName, callInstanceName, org, outputDict={}):
  varSnip = "empty"
  varsFragment = ''
#  varsFragment = readModuleConfigFile('arm', yamlInfraFileAndPath, moduleConfigFileAndPath, parentInstanceName, callInstanceName, org)
#  print('varsFragment is: ', varsFragment)
#  quit('--@!')
  varSnip = getArmParamsFile(keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, 'azure', foundationInstanceName,outputDict)
  if varSnip != 'empty':
    if varSnip is not None:
      varsFragment = varsFragment + varSnip
  return varsFragment

def getCloudFormationVarsFragment(keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, foundationInstanceName, parentInstanceName, callInstanceName, org, caller, serviceType, outputDict={}):
  varSnip = "empty"
  varsFragment = ''
#  varSnip = getCloudFormationParamsFile(keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, caller, serviceType, foundationInstanceName,outputDict)
  varSnip = getCloudFormationParamsFile(keyDir, yamlInfraFileAndPath, moduleConfigFileAndPath, caller, serviceType, callInstanceName,outputDict)
  if varSnip != 'empty':
    if varSnip is not None:
      varsFragment = varsFragment + varSnip
  return varsFragment

def readModuleConfigFile(tool, yamlInfraFileAndPath, moduleConfigFileAndPath, parentInstanceName, callInstanceName, org):
  varSnip = "empty"
  varsFragment = ''
  print('moduleConfigFileAndPath is: ', moduleConfigFileAndPath)
#  quit('@!')
  c = open(moduleConfigFileAndPath,'r')
  o = csv.reader(c)
  for r in o:
    print('r[0] is: ', r[0])
    if r[1] == 'infrastructureConfig.yaml':
      if r[5] == 'no':
        varSnip = getVarFromUserConfig(tool, r, yamlInfraFileAndPath, parentInstanceName, callInstanceName, org)
        if varSnip != 'empty':
          varsFragment = varsFragment + varSnip
        print('llllLLL varsFragment is: ', varsFragment) 
    elif r[1] == 'foundationOutput':
      if r[5] == 'no':
        varSnip = getVarFromOutput(tool, r, callInstanceName)
        if varSnip != 'empty':
          varsFragment = varsFragment + varSnip
    elif r[1] == 'customFunction':
      print('-------------- customFunction ---------- ')
      if r[5] == 'no':
        if r[0] == 'adminPublicIP':
          cidrBlock = getAdminCidr()
          if tool == 'terraform':
            varSnip = " -var=\"" +r[0] + "="+cidrBlock +"\""  
          elif tool == 'packer':
            varSnip = " -var \"" +r[0] + "="+cidrBlock +"\""
#          elif tool == 'arm':
#            varSnip = '        "'+r[0]+'": { "value": "' + cidrBlock + '" }\n'
#        if r[0] == 'currentDateTimeAlphaNumeric':
#          dateTimeCode = str(datetime.datetime.now()).replace(' ','').replace('-','').replace(':','').replace('.','')


#          #varSnip = formatPathForOS(varSnip)
#          varsFragment = varsFragment + varSnip
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
  yaml_keys_file_and_path = dirOfSourceKeys + 'keys.yaml'
  return yaml_keys_file_and_path

#This new function is for getting the specific location for the keys that the admin module creates for each system
def getKeyFileLocation(instance_name, cloud_vendor):
  outputDir = config_cliprocessor.inputVars.get("dirOfOutput") + instance_name + "\\"
  outputDir = formatPathForOS(outputDir)
  if not os.path.exists(outputDir):
    os.makedirs(outputDir)
  keys_file_and_path = 'invalid'
  keys_file_and_path = outputDir + 'keys.yaml'
  return keys_file_and_path

def assembleCloneCommand(sourceRepo):
  repoBranch = config_cliprocessor.inputVars.get('repoBranch')
  print('.... repoBranch is: ', repoBranch)
  print('mmm len(repoBranch) is: ', len(repoBranch))
  if len(repoBranch) == 0:
    branchPart = ''
  else:
    branchPart = ' --branch '+repoBranch+' '
  cloneCommand = 'git clone '+branchPart+sourceRepo
  return cloneCommand

def assembleSourceRepo(gitPass, sourceRepo):
  ### Assemble the URL to use to clone the repo that contains the configurtion.  
#  sourceRepo = getCliVariable('sourceRepo')
  if len(sourceRepo) == 0:
    logString = 'ERROR: sourceRepo parameter must be properly included in your command.'
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  if sourceRepo[0:8] != 'https://':
    logString = 'ERROR: the sourceRepo parameter must begin with https://'
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  else:
    print('Match!')
    if gitPass != None:
      sourceRepo = 'https://'+gitPass.strip()+'@'+sourceRepo[8:].strip()
  return sourceRepo

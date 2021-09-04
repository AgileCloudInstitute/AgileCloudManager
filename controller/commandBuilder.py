## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import yaml
import re
import requests
import sys
import csv
import json
import platform
import os
import commandRunner
import configReader

def getVarFromUserConfig(tool, row, yamlInfraFileAndPath, parentInstanceName, callInstanceName, org, **inputVars):
  inputVar = row[0]
  myType = row[2]
  identifier = row[3]
  sourceField = row[4]
  varSnip = "empty"
#  print("org is: ", org)
#  print("....parentInstanceName is: ", parentInstanceName)
#  print("....callInstanceName is: ", callInstanceName)
#  print("myType is: ", myType)
#  print("yamlInfraFileAndPath is: ", yamlInfraFileAndPath)
#  quit("Rest stop. ")
  with open(yamlInfraFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if myType.count('/') == 1:
        parentPart = myType.split('/')[0]
        childPart = myType.split('/')[1]
#        if myType == "systems/admin":

        if re.match(parentPart, key):
          parent = my_dict.get(key)
          for child in parent:
            if re.match(childPart, child):
              varSnip = getVarFromType(tool, row, callInstanceName, 2, parent.get(child), org, **inputVars)
              #if child == 'images':
#              print("...child is: ", child)
#              print("...parent.get(child) is: ", parent.get(child))
#              print("...varSnip is: ", varSnip)
#          quit("breakpoint")
      elif myType.count('/') == 2:
        if myType == 'projectManagement/projects/code':
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
                          varSnip = getVarFromType(tool, row, callInstanceName, 3, grandChild, org, **inputVars)
        elif myType == 'projectManagement/projects/parent':
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
                      varSnip = getVarFromType(tool, row, callInstanceName, 2, project, org, **inputVars)
        else: 
          quit("Error: Unsupported name for type.  Halting program so you can locate the problem within your configuration.")
      elif myType.count('/') > 2:
        quit("More than two occurrences of / are in myType. This is illegal, so we are halting the program to give you a chance to validate your configuration. ")
      else:
        if re.match(myType, key):
          type = my_dict.get(key)
          varSnip = getVarFromType(tool, row, callInstanceName, 1, type, org, **inputVars)
  return varSnip

def getVarFromType(tool, r, callInstanceName, layers, aType, org, **inputVars):
  inputVar = r[0]
  myType = r[2]
  if myType.count('/') == 1:
    myType = myType.split('/')[1]
  identifier = r[3]
  sourceField = r[4]
  varSnip = "empty"
  print("aType is: ", aType)
  print("myType is: ", myType)
#  quit("I am tired.")
  for props in aType:
    if isinstance(props, str):
      if inputVar == 'cidrBlocks': 
        if props == 'cidrBlocks':
          if aType.get(props) == 'admin':
            cidrBlocks = getAdminCidr()
          elif aType.get(props) == 'public':
            cidrBlocks = '0.0.0.0/0'
          else:
            print("cidr block not valid.")
          if tool == 'terraform':
            varSnip = " -var=\"" +inputVar + "="+cidrBlocks +"\""  
          elif tool == 'packer':
            varSnip = " -var \"" +inputVar + "="+cidrBlocks +"\""  
      elif re.match(sourceField, props):
#        quit("hi ho.")
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
                  print("cidr block not valid.")
              if tool == 'terraform':
                varSnip = " -var=\"" +inputVar + "="+cidrBlocks +"\""  
              elif tool == 'packer':
                varSnip = " -var \"" +inputVar + "="+cidrBlocks +"\""  
            elif sourceField == 'pathToScript':
              if props.get(prop) == 'azure':
                configAndSecretsPath = inputVars.get("configAndSecretsPath")
                pathStr = configAndSecretsPath + props.get(prop) + "\startup-script-demo.sh"
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
#              print("varSnip is: ", varSnip)
#              quit("Found instanceName. ")
            else:  
              if tool == 'terraform':
                if sourceField == 'cloudInit':
                  appParentpath = inputVars.get('app_parent_path')
                  relativePathAndFile = str(props.get(prop))
#                  print("platform.system() is: ", platform.system())
                  if platform.system() == "Windows":
                    appParentpath = appParentpath.replace("/", "\\")
                    relativePathAndFile = relativePathAndFile.replace("/", "\\")
#                  print("....appParentpath is: ", appParentpath)
#                  print("....relativePathAndFile is: ", relativePathAndFile)
                  varSnip = " -var=\"" +inputVar + "="+appParentpath + relativePathAndFile +"\""  
#                  print("....tool is terraform")
#                  print("....sourceField is: ", sourceField)
#                  print("....varSnip is:", varSnip)
                else:
                  varSnip = " -var=\"" +inputVar + "="+str(props.get(prop)) +"\""  
              elif tool == 'packer':
                if sourceField == 'init_script':
#                  print("mmmmmmmmmmmmmmmmmmmmm")
#                  print("....sourceField is: ", sourceField)
#                  print("....prop is: ", prop)
                  appParentpath = inputVars.get('app_parent_path')
                  relativePathAndFile = str(props.get(prop))
#                  print("platform.system() is: ", platform.system())
                  if platform.system() == "Windows":
                    appParentpath = appParentpath.replace("/", "\\")
                    relativePathAndFile = relativePathAndFile.replace("/", "\\")
#                  print("....appParentpath is: ", appParentpath)
#                  print("....relativePathAndFile is: ", relativePathAndFile)
                  varSnip = " -var \"" +inputVar + "="+appParentpath + relativePathAndFile +"\""  
#                  print("....varSnip is: ", varSnip)
                else:
                  varSnip = " -var \"" +inputVar + "="+str(props.get(prop)) +"\""  
#  quit("not gonna return.")
  return varSnip


def getSecretVarFromUserConfig(tool, r, yamlInfraFileAndPath):
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
            for instance in instances:
              if not isinstance(instance, str):
                if instance.get(sourceField) != None:
                  if tool == 'packer':
                    varLine = inputVar + "="+ instance.get(sourceField)
                  else:
                    varLine = inputVar + "=\""+ instance.get(sourceField) +"\"\n"
  else:  
    quit("TemplateName is malformed.  Halting program so you can debug.  ")
  return varLine


def getVarFromOutput(tool, r):
  inputVar = r[0]
  tfOutputVarName = r[4]
  thismodule = sys.modules[__name__]
  outputVar = getattr(commandRunner, tfOutputVarName)
  outputVar = outputVar.replace('"', '')
  if tool == 'terraform':
    varSnip = " -var=\"" +inputVar + "="+outputVar+"\""  
  elif tool == 'packer':
    varSnip = " -var \"" +inputVar + "="+outputVar+"\""  
  return varSnip

def getSecretVarFromKeys(tool, r, instanceName, cloud_vendor, **input_vars):
  #yamlKeysPath = getKeyPath(cloud_vendor, **input_vars)
  #print("yamlKeysPath is: ", yamlKeysPath)
  #yamlKeysFileAndPath = yamlKeysPath + r[1]

  yamlKeysPath  = input_vars.get("keysDir").replace("\\\\","\\")
  if cloud_vendor == "aws":
    yamlKeysFileAndPath = yamlKeysPath + 'iamUserKeys.yaml'
  if cloud_vendor == "azure":
    yamlKeysFileAndPath = yamlKeysPath + 'adUserKeys.yaml'
  else:
    quitStr = "Cloud vendor " + "\"" + cloud_vendor + "\" is not currently supported.  Halting program so you can fix your configuration. "

  #if 'iamUserKeys.yaml' in yamlKeysFileAndPath:
  #  keyPairName = 'iamUserKeyPair'
  #elif 'adUserKeys.yaml' in yamlKeysFileAndPath:
  #  keyPairName = 'adUserKeyPair'
  #else:
  #  keyPairName = instanceName + 'KeyPair'

  pub = input_vars.get("pub")
  sec = input_vars.get("sec")
  tfInputVarName = r[0]
  sourceField = r[4]
  secretLine = 'empty'
  print("yamlKeysFileAndPath is: ", yamlKeysFileAndPath)
  if cloud_vendor != "azure":
    quit("Breakpoint getSecretVarFromKeys.")
  with open(yamlKeysFileAndPath) as f:  
    keypairs_dict = yaml.safe_load(f)
    myItems = keypairs_dict.items()
    for key, value in myItems:  
      if (value[0] == "\"") and (value[-1] == "\""):
        #eliminate any pre-existing double quotes to avoid downstream errors.
        #print("value is: ", value , " and value already has quotes")
        value = value[1:]
        value = value[:-1]
        #print("revised value is: ", value)
      if key == sourceField:
        if tool == "terraform":
          secretLine = tfInputVarName + "=\""+value+"\"\n"
        elif tool == "packer":
          secretLine = tfInputVarName + "="+value
  if 'empty' in secretLine:
    print("Not able to find matching secret value.  Make sure to add better error handling here.")
  #print("secretLine is: ", secretLine)
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
    print("Invalid number of config rows in input file: ", +typeCounter+ ".  Add a validation script for the config file.")
  return typeOfLine

def getSecretVars(tool, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, instanceName, **inputVars):
  secretVarLines = []
  typeOfLine = getTypeOfLine(moduleConfigFileAndPath)
  c = open(moduleConfigFileAndPath,'r')
  o = csv.reader(c)
  keySource = inputVars.get("keySource")
  pub = inputVars.get("pub")
  sec = inputVars.get("sec")
  for r in o:
    inputVarName = r[0]
    if r[5] == 'yes':
      if r[1] == 'infrastructureConfig.yaml':
        typeOfLine = r[2]
        secretVarLine = getSecretVarFromUserConfig(tool, r, yamlInfraFileAndPath)
        if 'empty' not in secretVarLine:
          secretVarLines.append(secretVarLine)
      elif (r[1] == 'generatedKeys.yaml') or (r[1] == 'generatedAzureKeys.yaml') or (r[1] == 'iamUserKeys.yaml') or (r[1] == 'adUserKeys.yaml'):
        if keySource == "keyFile":
          secretVarLine = getSecretVarFromKeys(tool, r, instanceName, cloud_vendor, **inputVars)
          if 'empty' not in secretVarLine:
            secretVarLines.append(secretVarLine)
  if keySource == "keyVault":
    publicKeyLine = "_public_access_key=\""+pub+"\"\n"
    secretVarLines.append(publicKeyLine)
    secretKeyLine = "_secret_access_key=\""+sec+"\"\n"
    secretVarLines.append(secretKeyLine)
  if len(secretVarLines)>0:
    tfvarsFileAndPath = inputVars.get("tfvarsFileAndPath")
    if tool == 'terraform':
#      print("secretVarLines is: ", secretVarLines)
#      quit("halt! ")
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
  c.close()
  return varSnip

def getVarsFragment(tool, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, foundationInstanceName, parentInstanceName, callInstanceName, org, **inputVars):
  varSnip = "empty"
  varsFragment = ''
  varsFragment = readModuleConfigFile(tool, yamlInfraFileAndPath, moduleConfigFileAndPath, parentInstanceName, callInstanceName, org, **inputVars)
  varSnip = getSecretVars(tool, yamlInfraFileAndPath, moduleConfigFileAndPath, cloud_vendor, foundationInstanceName, **inputVars)
  if varSnip != 'empty':
    if varSnip is not None:
      varsFragment = varsFragment + varSnip
  return varsFragment


def readModuleConfigFile(tool, yamlInfraFileAndPath, moduleConfigFileAndPath, parentInstanceName, callInstanceName, org, **inputVars):
  varSnip = "empty"
  varsFragment = ''
  c = open(moduleConfigFileAndPath,'r')
  o = csv.reader(c)
  for r in o:
    if r[1] == 'infrastructureConfig.yaml':
      if r[5] == 'no':
        varSnip = getVarFromUserConfig(tool, r, yamlInfraFileAndPath, parentInstanceName, callInstanceName, org, **inputVars)
        if varSnip != 'empty':
          varsFragment = varsFragment + varSnip
    elif r[1] == 'foundationOutput':
      if r[5] == 'no':
        varSnip = getVarFromOutput(tool, r)
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
    print("The external IP of the agent was validated by two independent sources. ")
  else:
    sys.exit("The external IP of the agent could not be validated by two independent sources.  We therefore cannot complete security configuration.  Check the logs to research what happened. ")
  return cidrBlocks

def getKeyFileAndPath(type_name, cloud_vendor, **input_vars):
  yaml_keys_file_and_path = 'invalid'
  if type_name == 'admin':  
    if cloud_vendor == 'aws':
      yaml_keys_file_and_path = input_vars.get('dirOfYamlKeys') + input_vars.get('nameOfYamlKeys_IAM_File')
    elif cloud_vendor == 'azure':
      yaml_keys_file_and_path = input_vars.get('dirOfYamlKeys') + 'adUserKeys' + '.yaml'
      #input_vars.get('nameOfYamlKeys_Azure_AD_File')
  else:  
    if cloud_vendor == 'aws':
      yaml_keys_file_and_path = input_vars.get('dirOfYamlKeys') + input_vars.get('nameOfYamlKeys_AWS_Network_File')
    elif cloud_vendor == 'azure':
      yaml_keys_file_and_path = input_vars.get('dirOfYamlKeys') + input_vars.get('nameOfYamlKeys_Azure_Network_File')

#  print("yaml_keys_file_and_path is: ", yaml_keys_file_and_path)
#  quit("HALT")

  return yaml_keys_file_and_path

#..........................................................................................................
#This new function is for getting the specific location for the keys that the admin module creates for each system
def getKeyFileLocation(instance_name, cloud_vendor, **input_vars):
  outputDir = input_vars.get("dirOfOutput") + instance_name + "\\"
  if not os.path.exists(outputDir):
    os.makedirs(outputDir)
  keys_file_and_path = 'invalid'
  if cloud_vendor == 'aws':
    keys_file_and_path = outputDir + input_vars.get('nameOfYamlKeys_IAM_File')
  elif cloud_vendor == 'azure':
    keys_file_and_path = outputDir + 'adUserKeys' + '.yaml'
#  print("keys_file_and_path is: ", keys_file_and_path)
#  quit("HALT")

  return keys_file_and_path

#..........................................................................................................

def getKeyPath(cloud_vendor, **input_vars):
  print("cloud_vendor is: ", cloud_vendor)
  yaml_keys_path = 'invalid'
  if cloud_vendor == 'aws':
    yaml_keys_path = input_vars.get('dirOfYamlKeys')
  elif cloud_vendor == 'azure':
    yaml_keys_path = input_vars.get('dirOfYamlKeys')

#  print("yaml_keys_file_and_path is: ", yaml_keys_file_and_path)
#  quit("HALT")

  return yaml_keys_path

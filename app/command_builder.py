## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

from config_fileprocessor import config_fileprocessor
from controller_custom import controller_custom
from controller_arm import controller_arm
from command_formatter import command_formatter
from command_runner import command_runner
from log_writer import log_writer

import datetime
import json
import platform
import requests
import sys
import os
import yaml

class command_builder:

  outputVariables = []

  def __init__(self):  
    pass

  #@public
  def getVarsFragment(self, systemConfig, serviceType, instance, mappedVariables, tool, callingClass, outputDict={}):
    copyOfInstance = instance
    if (tool == 'arm') or (tool == 'cloudformation'):
      mappedVariables = copyOfInstance.get("mappedVariables")
    varLines = self.readMappedVariablesFromConfig(systemConfig, serviceType, copyOfInstance, mappedVariables, tool, callingClass, outputDict)
    if tool == 'customController':
      varsFragment = self.getCustomControllerParamsFile(varLines, instance)
    elif tool == 'arm':
      varsFragment = self.getArmParamsFile(varLines)
    elif tool == 'cloudformation':
      varsFragment = self.getCloudFormationParamsFile(varLines)
    elif tool == "terraform":
      varsFragment = self.getTerraformParamsFile(varLines)
    elif tool == "packer":
      varsFragment = self.getPackerParamsFile(varLines)
    print('serviceType is: ', serviceType)
    print('tool is: ', tool)
    print('callingClass is: ', callingClass)

    print('xzs varsFragment is: ', varsFragment)
#    quit('poiuytrewq')
    return varsFragment

  #@public
  def getBackendVarsFragment(self, backendVarCoordinates, tool, keyDir):
    bkndVarSnip = "empty"
    varsFragment = ''
    bkndVarSnip = self.getBackendVars(backendVarCoordinates, tool, keyDir)
    if bkndVarSnip != 'empty':
      if bkndVarSnip is not None:
        varsFragment = varsFragment + bkndVarSnip
    return varsFragment

  #@private
  def getTerraformParamsFile(self, varLines):
    import config_cliprocessor
    cfmtr = command_formatter()
    lw = log_writer()
    tfvarsFileAndPath = config_cliprocessor.inputVars.get("tfvarsFileAndPath")
    if len(varLines)>0:
        f = open(tfvarsFileAndPath, "w")
        for line in varLines:
          f.write(line)
        f.close()
        varSnip = " -var-file=\"" + tfvarsFileAndPath +"\""
    else:
      logString = "ERROR: Required secrets were not found inside: " + str(tfvarsFileAndPath)
      lw.writeLogVerbose("acm", logString)
      exit(1)
    varSnip = cfmtr.formatPathForOS(varSnip)
    return varSnip

  #@private
  def getPackerParamsFile(self, varLines):
    import config_cliprocessor
    cfmtr = command_formatter()
    lw = log_writer()
    tfvarsFileAndPath = config_cliprocessor.inputVars.get("tfvarsFileAndPath")
    if len(varLines)>0:
        packerVarsFileAndPath=tfvarsFileAndPath.replace(".tfvars",".json")
        secretVarDict = dict(s.split('=',1) for s in varLines)
        out_file = open(packerVarsFileAndPath,'w+')
        json.dump(secretVarDict,out_file)
        varSnip = " -var-file=\"" + packerVarsFileAndPath +"\""
    else:
      logString = "ERROR: Required secrets were not found inside: " + str(tfvarsFileAndPath)
      lw.writeLogVerbose("acm", logString)
      exit(1)
    varSnip = cfmtr.formatPathForOS(varSnip)
    return varSnip

  #@private
  def getCustomControllerParamsFile(self, customLineDictsList, instance):
    import config_cliprocessor
    cfmtr = command_formatter()
    lw = log_writer()
    userCallingDir = config_cliprocessor.inputVars.get("userCallingDir")
    templateFileAndPath = userCallingDir+'/'+instance.get('templateName')
    templateFileAndPath = cfmtr.formatPathForOS(templateFileAndPath)
    if not os.path.isfile(templateFileAndPath):
      logString = "ERROR: "+templateFileAndPath+ " is not a valid file location. "
      lw.writeLogVerbose("acm", logString)
      exit(1)
    varsFileAndPath = config_cliprocessor.inputVars.get("tfvarsFileAndPath")
    if len(customLineDictsList)>0:
      customVarsFileAndPath=varsFileAndPath.replace(".tfvars",".json")
      out_file = open(customVarsFileAndPath,'w+')
      json.dump(customLineDictsList,out_file)
      varSnip = " --varsfile://" + customVarsFileAndPath + " --templateFile://"+templateFileAndPath
      out_file.close()
    else:
      logString = "ERROR: Required variables were not passed into: " + str(varsFileAndPath)
      lw.writeLogVerbose("acm", logString)
      exit(1)
    return varSnip

  #@private
  def getArmParamsFile(self, varLines):
    import config_cliprocessor
    cfmtr = command_formatter()
    lw = log_writer()
    varsFileAndPath = config_cliprocessor.inputVars.get("tfvarsFileAndPath")
    revisedVarLines = []
    if len(varLines)>0:
      armVarsFileAndPath=varsFileAndPath.replace(".tfvars",".json")
      for rawLine in varLines:
        cleanLine = rawLine.replace('"','').replace(' ','')
        revisedVarLines.append(cleanLine)
      varsDict = dict()   
      for line in revisedVarLines:
        varsDict[line.split(":", 1)[0]] = json.loads(line.split(":", 1)[1].replace('\'','"'))
      paramsDict = {
        "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
        "contentVersion": "1.0.0.0",
        "parameters": varsDict
      }
      out_file = open(armVarsFileAndPath,'w+')
      json.dump(paramsDict,out_file)
      varSnip = " --parameters " + armVarsFileAndPath 
    else:
      logString = "ERROR: Required secrets were not found inside: " + str(varsFileAndPath)
      lw.writeLogVerbose("acm", logString)
      exit(1)
    varSnip = cfmtr.formatPathForOS(varSnip)
    return varSnip

  #@private
  def getArmVarLine(self, varName, varValue):
    valDict = { "value": varValue  }
    varLine = '        '+varName+':'+str(valDict)
    return varLine

  #The following function needs to be integrated somewhere. IT IS NOT CALLED ANYWHERE.
  #@private
  def getAdminCidr(self):
    lw = log_writer()
    try: 
      adminCidr1 = (requests.get('https://api.ipify.org').text).rstrip() + "/32"
      adminCidr2 =  (requests.get('http://ipv4.icanhazip.com').text).rstrip() + "/32"
    except requests.exceptions.ConnectionError: 
      sys.exit("One of the external validators of the admin IP address failed to respond to a validation request.  This might be a temporary error and might work if you try again.")
    if adminCidr1 == adminCidr2:  
      cidrBlocks = adminCidr1
      logString = "The external IP of the agent was validated by two independent sources. "
      lw.writeLogVerbose("acm", logString)
    else:
      logString = "The external IP of the agent could not be validated by two independent sources.  We therefore cannot complete security configuration.  Check the logs to research what happened. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    return cidrBlocks

  #private
  def getBackendVars(self, backendVarCoordinates, tool, keyDir):
    import config_cliprocessor
    cfmtr = command_formatter()
    lw = log_writer()
    secretVarLines = []
#    print('backendVarCoordinates is: ', backendVarCoordinates)
#    quit('---b!')
    for backendVar in backendVarCoordinates:
#      if backendVar == 'key':
#        print('1 backendVar is: ', backendVar)
      if backendVarCoordinates.get(backendVar).startswith("$keys"):
        secretVarLine = self.getSecretVarFromKeys(tool, keyDir, backendVar, backendVarCoordinates.get(backendVar))
        if 'empty' not in secretVarLine:
          secretVarLines.append(secretVarLine.replace(" ", ""))
      elif backendVarCoordinates.get(backendVar).startswith("$"):
        quit("DEBUG getBackendVars() in command_builder.py")
      else:
          secretVarLine = self.getSecretVarFromUserConfig(tool, backendVar, backendVarCoordinates.get(backendVar))
          if 'empty' not in secretVarLine:
            secretVarLines.append(secretVarLine.replace(" ", ""))
#          if backendVar == 'key':
#            print('2 backendVar is: ', backendVar)
#            print('secretVarLine is: ', secretVarLine)
#    print('a secretVarLines is: ', secretVarLines)
    if len(secretVarLines)>0:
      tfBackendFileAndPath = config_cliprocessor.inputVars.get("tfBackendFileAndPath")
      if tool == 'terraform':
        from pathlib import Path
        p = Path(tfBackendFileAndPath.replace('backend.tfvars',''))
        p.mkdir(parents=True, exist_ok=True)
        f = open(tfBackendFileAndPath, "w")
        for line in secretVarLines:
          f.write(line)
        f.close()
        varSnip = " -backend-config=\"" + tfBackendFileAndPath +"\""
      else:
        logString = "Invalid tool.  There is an error in your configuration which caused the getBackendVars() function to be called for a tool that is not terraform.  "
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    varSnip = cfmtr.formatPathForOS(varSnip)
#    print('varSnip is: ', varSnip)
#    print('b secretVarLines is: ', secretVarLines)
#    quit('a---!')
    return varSnip

  #@private
  def getSecretVarFromKeys(self, tool, keyDir, sourceField, valueCoordinates):
    cfmtr = command_formatter()
    lw = log_writer()
    secretLine = "empty"
    if platform.system() == "Windows":
      if keyDir[:-1] != "\\":
        keyDir = keyDir + "\\"
    if platform.system() == "Linux":
      if keyDir[:-1] != "/":
        keyDir = keyDir + "/"
    yamlKeysPath = keyDir.replace("\\\\","\\")
    yamlKeysPath = cfmtr.formatPathForOS(yamlKeysPath)
    yamlKeysFileAndPath = yamlKeysPath + 'keys.yaml'
    if valueCoordinates == "$keys":
      tfInputVarName = sourceField
    else: 
      if valueCoordinates.count(".") == 1:
        coordParts = valueCoordinates.split(".")
        tfInputVarName = coordParts[1]
      else:
        quit("ERROR: Only one . after $keys is allowed in configuration.  ")
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
      if key == tfInputVarName:
        if tool == "terraform":
          secretLine = sourceField + "=\""+value.replace(" ","")+"\"\n"
        elif tool == "packer":
          secretLine = sourceField + "="+value.replace(" ","")
        elif tool == 'arm':
          valDict = { "value": value.replace(" ","")  }
          secretLine = '        '+tfInputVarName+': '+str(valDict)
        elif tool == 'cloudformation':
          secretLine = {"ParameterKey":tfInputVarName,"ParameterValue":value.replace(" ","")}
        elif tool == 'customController':
          secretLine = {sourceField:value.replace(" ","")}
    if 'empty' in secretLine:
      logString = "Not able to find matching value for "+tfInputVarName+" in "+yamlKeysFileAndPath+" .  Halting program so you can examine the root cause of this problem. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    return secretLine

  #@private
  def getRawSecretFromKeys(self, keyDir, sourceField, valueCoordinates):
    cfmtr = command_formatter()
    lw = log_writer()
    secret = "empty"
    if platform.system() == "Windows":
      if keyDir[:-1] != "\\":
        keyDir = keyDir + "\\"
    if platform.system() == "Linux":
      if keyDir[:-1] != "/":
        keyDir = keyDir + "/"
    yamlKeysPath = keyDir.replace("\\\\","\\")
    yamlKeysPath = cfmtr.formatPathForOS(yamlKeysPath)
    yamlKeysFileAndPath = yamlKeysPath + 'keys.yaml'
    if valueCoordinates == "$keys":
      tfInputVarName = sourceField
    else: 
      if valueCoordinates.count(".") == 1:
        coordParts = valueCoordinates.split(".")
        tfInputVarName = coordParts[1]
      else:
        quit("ERROR: Only one . after $keys is allowed in configuration.  ")
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
      if key == tfInputVarName:
        secret = value.replace(" ","")
    if 'empty' in secret:
      logString = "Not able to find matching value for "+tfInputVarName+" in "+yamlKeysFileAndPath+" .  Halting program so you can examine the root cause of this problem. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    return secret

  #@private
  def getSecretValueFromKeys(self, tool, keyDir, sourceField, valueCoordinates):
    cfmtr = command_formatter()
    lw = log_writer()
    returnValue = "empty"
    if platform.system() == "Windows":
      if keyDir[:-1] != "\\":
        keyDir = keyDir + "\\"
    if platform.system() == "Linux":
      if keyDir[:-1] != "/":
        keyDir = keyDir + "/"
    yamlKeysPath = keyDir.replace("\\\\","\\")
    yamlKeysPath = cfmtr.formatPathForOS(yamlKeysPath)
    yamlKeysFileAndPath = yamlKeysPath + 'keys.yaml'
    if valueCoordinates == "$keys":
      tfInputVarName = sourceField
    else: 
      if valueCoordinates.count(".") == 1:
        coordParts = valueCoordinates.split(".")
        tfInputVarName = coordParts[1]
      else:
        quit("ERROR: Only one . after $keys is allowed in configuration.  ")
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
      if key == tfInputVarName:
        returnValue = value.replace(" ","")
    if 'empty' in returnValue:
      logString = "Not able to find matching value for "+tfInputVarName+" in "+yamlKeysFileAndPath+" .  Halting program so you can examine the root cause of this problem. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    return returnValue

  #@private
  def getSecretVarFromUserConfig(self, tool, fieldName, value):
    varLine = "empty"
    if tool == 'packer':
      varLine = fieldName + "="+ value
    else:
      varLine = fieldName + "=\""+ value +"\"\n"
    return varLine

  #@private
  def integrateSharedVariables(self, systemConfig, serviceType, instance):
    #This section might be redundant to code in controller_terraform.py that integrates sharedVariables
    for blockName in systemConfig:
      if blockName == "serviceTypes":
        for type in systemConfig.get(blockName):
          if serviceType == type:
            if 'sharedVariables' in systemConfig.get(blockName).get(type).keys():
              for sharedBlockName in systemConfig.get(blockName).get(type):
                if sharedBlockName == "sharedVariables":
                  sharedVarsDict = {}
                  instanceVarsDict = {}
                  if "sharedVariables" in systemConfig.get("serviceTypes").get(serviceType).keys():
                    if "mappedVariables" in systemConfig.get("serviceTypes").get(serviceType).get("sharedVariables"):
                      sharedVarsDict = systemConfig.get("serviceTypes").get(serviceType).get("sharedVariables").get("mappedVariables")
                      print("sharedVarsDict is: ", sharedVarsDict)
                  instanceVarsDict = instance.get("mappedVariables")
                  mappedVariables = { **sharedVarsDict, **instanceVarsDict }
            else:
              mappedVariables = instance.get('mappedVariables')
    return mappedVariables

  #@private
  def needsFoundationOutput(self, mappedVariables):
    needsFoundationOutput = False
    for varName in mappedVariables:
      if mappedVariables.get(varName).startswith("$customFunction.foundationOutput"):
        needsFoundationOutput = True
    return needsFoundationOutput

  #@private
  def readMappedVariablesFromConfig(self, systemConfig, serviceType, instance, mappedVariables, tool, callingClass, outputDict={}):
    cfp = config_fileprocessor()
    lw = log_writer()
    keyDir = cfp.getKeyDir(systemConfig)
    varLines = []
    #FIRST: integrate sharedVariables
    if (serviceType != None) and (serviceType != 'networkFoundation') and (serviceType != 'images'):
      mappedVariables = self.integrateSharedVariables(systemConfig, serviceType, instance)
    #SECOND, get foundation output variables if the tool is packer, and if there are any calls to $foundationOutput in mappedVariables
    if self.needsFoundationOutput(mappedVariables):
      if (hasattr(callingClass, 'foundationOutput')) and (len(callingClass.foundationOutput) > 0):
        foundationOutputVariables = callingClass.foundationOutput
      else:
        foundationOutputVariables = self.populateFoundationOutput(tool, systemConfig, keyDir, instance)
      self.outputVariables = foundationOutputVariables
    #iterate through each mapped variable to get the value
    for varName in mappedVariables:
      #THIRD, get the value for each variable
      value = self.getValueForOneMappedVariable(mappedVariables, varName, tool, keyDir, systemConfig, instance, varLines, outputDict)
      print('ddd value is: ', value)
      #FOURTH, Now add the value you just calculated into the result of this function
      if tool == "arm":
        varLine = self.getArmVarLine(varName, value)
        varLines.append(varLine.replace(" ", ""))
      elif tool == "cloudformation":
        lineDict = {"ParameterKey":varName,"ParameterValue":value}
        varLines.append(lineDict)
      elif tool == "customController":
        customLineDict = {varName:value}
        varLines.append(customLineDict)
      elif tool == 'terraform':
        tfVarLine = varName + "=\""+value.replace(" ","")+"\"\n"
        varLines.append(tfVarLine)
      elif tool == 'packer':
        pkVarLine = varName + "="+value.replace(" ","")
        varLines.append(pkVarLine)
      else:
        logString = "ERROR: Invalid controller name: "+tool
        quit(logString)
      print('ddd mappedVariables is: ', str(mappedVariables))
      print('ddd varLines is: ', str(varLines))
    print('end varLines is: ', str(varLines))
    #SIXTH, return the variables
    if (tool == "arm") or (tool == "cloudformation") or (tool == "customController") or (tool == "terraform") or (tool == "packer"):
      return varLines
    else:
      logString = "ERROR: You have entered an invalid tool "+tool+" . "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  def populateFoundationOutput(self, tool, systemConfig, keyDir, instance):
    foundationOutputVariables = {}
    if (tool == "packer") or (tool == "terraform"):
      foundationTool = systemConfig.get("foundation").get("controller")
      if foundationTool == "terraform":
        from controller_terraform import controller_terraform
        ct = controller_terraform()
        ct.terraformCrudOperation('output', keyDir, systemConfig, None, 'none', 'networkFoundation', None, None)
        foundationOutputVariables = ct.tfOutputDict
      else:
        quit("Other output tools handled elsewhere in code, so this should never be triggered.")
    elif tool == 'customController':
      cc = controller_custom()
      controllerPathFoundation = instance.get('controller').replace('$customController.','')
      controllerCommandFoundation = instance.get('controllerCommand')
      foundationMappedVariables = systemConfig.get('foundation').get('mappedVariables')
      foundationInstance = systemConfig.get('foundation')
      cc.runCustomController('output', systemConfig, controllerPathFoundation, controllerCommandFoundation, foundationMappedVariables, None, foundationInstance)
      foundationOutputVariables = cc.outputVariables
    elif tool == 'arm':
      ca = controller_arm()
      ca.createDeployment(systemConfig, systemConfig.get("foundation"), 'networkFoundation', 'networkFoundation', True)
      foundationOutputVariables = ca.foundationOutput
    return foundationOutputVariables

  #@private
  def addPathFunction(self,funcCoordParts):
    import config_cliprocessor
    cfmtr = command_formatter()
    if len(funcCoordParts) == 3:
      valRoot = funcCoordParts[2]
    elif len(funcCoordParts) == 4:
      valRoot = funcCoordParts[2] + '.' + funcCoordParts[3]
    else:
      logString = "ERROR: Only 2 or 3 dots . may be included in a call to the addPath function.  If a third dot is present, it must be to attack a file type as in someScript.py "
      quit(logString)
    filename = config_cliprocessor.inputVars.get('userCallingDir')+cfmtr.getSlashForOS()+valRoot
    filename = cfmtr.formatPathForOS(filename)
    if os.path.exists(filename):
      return filename
    else:
      logString = "ERROR: Invalid filename passed into addPath function. "+str(filename)
      quit(logString)

  #@private
  def getVarFromOutput(self, tool, tfOutputVarName):
    print('nn tfOutputVarName is: ', tfOutputVarName)
    if len(tfOutputVarName) == 0:
      logString = "ERROR: There were no foundation output variables.  Has your foundation already been deleted?  Or is your foundation configuration failing to produce output variables?"
      quit(logString)
    if (tool=='terraform') or (tool=='packer'):
      for key in self.outputVariables:
        if key == tfOutputVarName:
          outputVar = self.outputVariables[tfOutputVarName]
    return outputVar

  #@private
  def getSecretMappedVariables(self, mappedVariables, tool, keyDir):
    import config_cliprocessor
    cfmtr = command_formatter()
    lw = log_writer()
    secretVarLines = []
    for varName in mappedVariables:
      if mappedVariables.get(varName).startswith("$keys"):
        if mappedVariables.get(varName).count(".") == 0:
          secretVarLine = self.getSecretVarFromKeys(tool, keyDir, varName, "$keys")
          if 'empty' not in secretVarLine:
            secretVarLines.append(secretVarLine.replace(" ", ""))
        elif mappedVariables.get(varName).count(".") == 1:
          secretVarLine = self.getSecretVarFromKeys(tool, keyDir, varName, mappedVariables.get(varName))
          if 'empty' not in secretVarLine:
            if isinstance(secretVarLine, str):
              secretVarLine = secretVarLine.replace(" ", "")
            secretVarLines.append(secretVarLine)
        else:
          quit("ERROR: Invalid number of . in mappedVariable")
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
      lw.writeLogVerbose("acm", logString)
      exit(1)
    varSnip = cfmtr.formatPathForOS(varSnip)
    return varSnip

  #@private
  def getCloudFormationParamsFile(self, varLines):
    import config_cliprocessor
    lw = log_writer()
    varsFileAndPath = config_cliprocessor.inputVars.get("tfvarsFileAndPath")
    if len(varLines)>0:
      cfVarsFileAndPath=varsFileAndPath.replace(".tfvars",".json")
      out_file = open(cfVarsFileAndPath,'w+')
      json.dump(varLines,out_file)
      varSnip = " --parameters file://" + cfVarsFileAndPath 
    else:
      logString = "ERROR: Required variables were not passed into: " + str(varsFileAndPath)
      lw.writeLogVerbose("acm", logString)
      exit(1)
    return varSnip

  #@private
  def getValueForOneMappedVariable(self, mappedVariables, varName, tool, keyDir, systemConfig, instance, varLines, outputDict):
    cr = command_runner()
    if mappedVariables.get(varName).startswith('$env.'):
      envVarName = mappedVariables.get(varName).replace('$env.', '')
      print('varName is: ', varName)
      print('envVarName is: ', envVarName)
      print('os.environ is: ', str(os.environ))
      print("ACM_VAR_ONE:", os.environ.get('ACM_VAR_ONE', '<unset>'))
      print("ACM_VAR_TWO:", os.environ.get('ACM_VAR_TWO', '<unset>'))
      if envVarName in os.environ:
        value = os.environ.get(envVarName)
      else:
        logString = 'ERROR: '+envVarName+' is not among your environment variables. '
        quit(logString)
    elif mappedVariables.get(varName).startswith("$keys"):
      print('zzz tool is: ', tool)
      print('zzz varName is: ', varName)
      print('zzz keyDir is: ', keyDir)
      print('zzz mappedVariables.get(varName) is: ', mappedVariables.get(varName))
      #This is handled in a separate block below in this function
      if tool == "arm":
        #For ARM templates, vars get placed in a params file to obscure them from logs.  
        #Later, below, add handling to take variables sourced from keys and put them into ARM templates
        #For now, the $keys for ARM templates are handled by the custom controller which makes cli calls to the Azure API
        if (mappedVariables.get(varName).count('.') == 0) or (mappedVariables.get(varName).count('.') == 1):
          value = self.getRawSecretFromKeys(keyDir, varName, mappedVariables.get(varName))
        else:
          logString = "ERROR: For ARM templates, exactly either zero or one dot is allowed in $keys coordinates, as in $keys.varName "
          quit(logString)
      elif tool == "cloudformation":
        value = self.getRawSecretFromKeys(keyDir, varName, mappedVariables.get(varName))
      elif tool == "customController":
        value = self.getSecretValueFromKeys(tool, keyDir, varName, mappedVariables.get(varName))
      elif tool == "terraform":
        if (mappedVariables.get(varName).count('.') == 0) or (mappedVariables.get(varName).count('.') == 1):
          value = self.getRawSecretFromKeys(keyDir, varName, mappedVariables.get(varName))
        else:
          logString = "ERROR: Exactly either zero or one dot is allowed in $keys coordinates, as in $keys.varName "
          quit(logString)
      elif tool == "packer":
        if (mappedVariables.get(varName).count('.') == 0) or (mappedVariables.get(varName).count('.') == 1):
          value = self.getRawSecretFromKeys(keyDir, varName, mappedVariables.get(varName))
        else:
          logString = "ERROR: Exactly either zero or one dot is allowed in $keys coordinates, as in $keys.varName "
          quit(logString)
    elif mappedVariables.get(varName).startswith("$this"):
#      print('mappedVariables is: ', mappedVariables)
      print('mappedVariables.get(varName) is: ', mappedVariables.get(varName))
      print('varName is: ', varName)
      if (not mappedVariables.get(varName).startswith('$this.instance')) and (not mappedVariables.get(varName).startswith('$this.tags')) and (not mappedVariables.get(varName).startswith('$this.foundation')):
        logString = "ERROR: Illegal syntax for "+varName+":  "+mappedVariables.get(varName)
        quit(logString)
      if mappedVariables.get(varName).count(".") == 1:
        varToCheck = varName
      elif mappedVariables.get(varName).count(".") == 2:
        thisParts = mappedVariables.get(varName).split(".")
        varToCheck = thisParts[2]
      else:
        logString = 'ERROR: $this statement had an illegal number of dots ( . ).  Only either one or 2 dots are allowed in each $this statement.  '
        quit(logString)
      print('varToCheck is: ', varToCheck)
      if mappedVariables.get(varName).startswith("$this.foundationMapped"):
        value = systemConfig.get('foundation').get('mappedVariables').get(varToCheck)
      if (str(mappedVariables.get(varName)).startswith('$this.foundation')) and (not mappedVariables.get(varName).startswith("$this.foundationMapped")):
        value = systemConfig.get('foundation').get(varToCheck)
        print('... uuu value is: ', value)
      elif mappedVariables.get(varName).startswith("$this.instance"):
        value = instance.get(varToCheck)
      elif mappedVariables.get(varName).startswith("$this.tags"):
        value = systemConfig.get('tags').get(varToCheck)
    elif mappedVariables.get(varName).startswith("$customFunction"):
      funcCoordParts = mappedVariables.get(varName).split(".")
      funcName = funcCoordParts[1]
      if funcName == 'foundationOutput':
        if tool == "arm":
          if len(funcCoordParts) == 2:
            varToCheck = varName
          elif len(funcCoordParts) == 3:
            varToCheck = funcCoordParts[2]
          else:
            logString = "ERROR: $customFunction.foundationOutput is only allowed to have either one or two dots . in the command.  "
            quit(logString)
          if varToCheck in self.outputVariables.keys():
            for thisOutput in self.outputVariables:
              if varToCheck == thisOutput:
                value = str(self.outputVariables[thisOutput]['value'])
          else:
            logString = "ERROR: "+varToCheck+" was not in your foundation output: "+str(self.outputVariables.keys())
            quit(logString)
        elif tool == "cloudformation":
          if len(funcCoordParts) == 2:
            varToCheck = varName
          elif len(funcCoordParts) == 3:
            varToCheck = funcCoordParts[2]
          else:
            logString = "ERROR: $customFunction.foundationOutput is only allowed to have either one or two dots . in the command.  "
            quit(logString)
          from controller_cf import controller_cf
          ccf4output = controller_cf()
          from config_fileprocessor import config_fileprocessor
          cfp = config_fileprocessor()
          outputKeyDir = cfp.getKeyDir(systemConfig)
          value = ccf4output.getVarFromCloudFormationOutput(outputKeyDir, varToCheck, systemConfig.get("foundation").get('stackName'), systemConfig.get("foundation").get('region'))
        elif tool == "customController":
          if len(funcCoordParts) == 2:
            nameToCheck = varName
          elif len(funcCoordParts) == 3:
            nameToCheck = funcCoordParts[2]
          for thisOutput in self.outputVariables:
            if thisOutput['varName'] == nameToCheck:
              value = thisOutput['varValue']
        else:
          if mappedVariables.get(varName).count(".") == 1:
            tfOutputVarName = varName
          elif mappedVariables.get(varName).count(".") == 2:
            tfOutputVarName = mappedVariables.get(varName).split(".")[2]
          else:
            logString = "ERROR: Incorrect number of dots in $customFunction.foundationOutput coordinates.  When using $customFunction.foundationOutput as a source for variable values, your config must use either one dot or two dots.  The line with problems is: "+mappedVariables.get(varName)
            quit(logString)
          value = self.getVarFromOutput(tool, tfOutputVarName)
      elif funcName == "addPath":
        value = self.addPathFunction(funcCoordParts)
      elif funcName == 'imageBuilderId':
        subscriptionId = outputDict['subscriptionId']
        resourceGroupName = outputDict['resourceGroupName']
        identityName = outputDict['identityName']
        value='/subscriptions/'+subscriptionId+'/resourcegroups/'+resourceGroupName+'/providers/Microsoft.ManagedIdentity/userAssignedIdentities/'+identityName
      elif funcName == "currentDateTime":
        if "dateTimeCode" in outputDict.keys():
          value = outputDict.get('dateTimeCode')
        else:
          value = str(datetime.datetime.now()).replace(' ','').replace('-','').replace(':','').replace('.','')
      elif funcName == "addDateTime":
        if len(funcCoordParts) == 3:
          if "dateTimeCode" in outputDict.keys():
            dt = outputDict.get('dateTimeCode')
          else:
            dt = str(datetime.datetime.now()).replace(' ','').replace('-','').replace(':','').replace('.','')
          rootString = funcCoordParts[2]
          value = (rootString+dt).replace(' ','').lower()
        else:
          logString = "ERROR: addDateTime function call must have exactly two dots in format: $customFunction.addDateTime.rootstring"
          quit(logString)
      elif funcName == "imageTemplateName":
        if len(funcCoordParts) == 2:
          if "dateTimeCode" in outputDict.keys():
            dt = outputDict.get('dateTimeCode')
          else:
            dt = str(datetime.datetime.now()).replace(' ','').replace('-','').replace(':','').replace('.','')
          rootString = instance.get('instanceName')
          value = (rootString+dt).replace(' ','').lower()
#          print('eee value is: ', value)
#          quit('---...---987')
        else:
          logString = "ERROR: imageTemplateName function call must have exactly one dot in format: $customFunction.imageTemplateName"
          quit(logString)
      elif funcName == "mostRecentImage":
        if tool == "arm":
          imageNameRoot = funcCoordParts[2]
          resourceGroupName = systemConfig.get('foundation').get("resourceGroupName")
#25Aug          getImagesCmd = 'az resource list --resource-group '+resourceGroupName+' --resource-type Microsoft.Compute/images '
          getImagesCmd = "az graph query -q \"Resources | where type =~ 'Microsoft.Compute/images' and resourceGroup =~ '"+resourceGroupName+"' | project name, resourceGroup | sort by name asc\""
          imgsJSON = cr.getShellJsonResponse(getImagesCmd) 
#          print("imgsJSON", str(imgsJSON))
          imageNamesList = []
          imgsJSON = yaml.safe_load(imgsJSON)  
          for image in imgsJSON['data']:
            if imageNameRoot in image['name']:
              imageNamesList.append(image.get("name"))
          sortedImageList = list(sorted(imageNamesList))
          if len(sortedImageList) >0:
            value = sortedImageList[-1]
          else:
            logString = "ERROR: No images with names containing "+imageNameRoot+" exist in the resource group named "+resourceGroupName 
            quit(logString)
#          print("value is: ", value)
#          quit("25Aug cb")
        elif tool == "cloudformation":
          from controller_cf import controller_cf
          iccf = controller_cf()
          imageNameRoot = funcCoordParts[2]
          outputDict['ImageNameRoot'] = imageNameRoot
          value = iccf.getMostRecentImage(systemConfig, keyDir, outputDict)
        elif tool == 'terraform':
          quit("WARNING: Please use terraform's internal syntax for filtering most recent images.  Program is halting here to allow you to change your terraform code and re-run so that this error can be avoided. ")
        else:
          logString = "The $customFunction.mostRecentImage is currently supported for the terraform, arm and cloudformation controllers. "
          quit(logString)
      elif funcName == "addOrganization":
        valRoot = funcCoordParts[2]
        value = (valRoot+systemConfig.get("organization")).lower()
    else: 
      #Handle plaintext variables that do not require coordinate searching
      value = mappedVariables.get(varName)
    print('end value is: ', value)
    return value

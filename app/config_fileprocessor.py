## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

from command_formatter import command_formatter
import config_cliprocessor

import yaml
import re
import sys

class config_fileprocessor:

  def __init__(self):  
    pass

  #@public
  def getApplianceConfig(self, yamlFileAndPath):
    with open(yamlFileAndPath) as f:  
      topLevel_dict = yaml.safe_load(f)
    return topLevel_dict
 
  #@public
  def getSystemConfig(self, applianceConfig, systemName):
    cfmtr = command_formatter()
    print('x applianceConfig is: ', applianceConfig)
    for item in applianceConfig:
      print("x item is: ", item)
      print("x systemName is: ", systemName)
      if str(item).replace(" ","") == str(systemName).replace(" ","") :
        print("applianceConfig.get(item) is: ", str(applianceConfig.get(item)))

        print("type(applianceConfig.get(item)) is: ", str(type(applianceConfig.get(item))))
        #if type(applianceConfig.get(item)) == dict:
        #  print("x About to return applianceConfig.get(item) ", applianceConfig.get(item))
        #  return applianceConfig.get(item)
        if type(applianceConfig.get(item)) == str:
          if (applianceConfig.get(item).split(".")[1] == "yaml") or (applianceConfig.get(item).split(".")[1] == "yml"):
            systemConfigFile = config_cliprocessor.inputVars.get('userCallingDir')+cfmtr.getSlashForOS()+str(applianceConfig.get(item))
            #systemConfigFile = config_cliprocessor.inputVars.get('acmConfigPath')+cfmtr.getSlashForOS()+"systems"+cfmtr.getSlashForOS()+applianceConfig.get(item)
            systemConfigFile = cfmtr.formatPathForOS(systemConfigFile)
            print("systemConfigFile is: ", systemConfigFile) 
            with open(systemConfigFile) as f:  
              topLevel_dict = yaml.safe_load(f)
            print("topLevel_dict is: ", str(topLevel_dict))
            print("...")
            return topLevel_dict.get(systemName)

  #@public
  def getSystemNames(self, applianceConfig):
    instanceNames = []
    for item in applianceConfig:
      if (type(applianceConfig.get(item)) == dict) or (type(applianceConfig.get(item)) == str):
        if type(item) == str:
          instanceNames.append(item)
    return instanceNames

  #@public
  def systemHasFoundation(self, systemInstanceConfig):
    if "foundation" in systemInstanceConfig.keys():
      return True
    else:
      return False
 
  #@public
  def getKeyDir(self, systemConfig):
    import config_cliprocessor
    propVal = systemConfig.get("keysDir")
    if propVal == '$Default':
      propVal = config_cliprocessor.inputVars.get('dirOfYamlKeys')
    elif '$Output' in propVal:
      propParts = propVal.split('\\')
      if len(propParts) == 2:
        if propParts[0] == '$Output':
          outputDir = config_cliprocessor.inputVars.get('dirOfOutput')
          propVal = outputDir +'/'+ propParts[1] 
        else:
          print('The invalid input for keysDir is: ', propVal)
          print('ERROR: Invalid input for keysDir.')
          sys.exit(1)
      else:
        print('The invalid input for keysDir is: ', propVal)
        print('ERROR: Invalid input for keysDir.')
        sys.exit(1)
    cmdfrmtr = command_formatter()
    propVal = cmdfrmtr.formatPathForOS(propVal)
    return propVal

  #@public
  def getFirstLevelValue(self, yamlFileAndPath, keyName):
    #Only scan lines that have one or two colons.  
    # First colon separates key and value.  Second colon might be in a URL.
    returnVal = ""  
#    print("k keyName is: ", keyName)
    with open(yamlFileAndPath) as file:
      for line in file:
        if line.count(':') == 1:
          lineParts = line.split(":")
          key = lineParts[0].strip()
          value = lineParts[1].strip()
          if keyName == key:
#          if re.match(keyName, key):
            returnVal = value
        elif line.count(':') == 2:
          lineParts = line.split(":")
          key = lineParts[0].strip()
          value = lineParts[1].strip() + ":" + lineParts[2].strip()
          if keyName == key:
#          if re.match(keyName, key):
            returnVal = value
    return returnVal

  def getValueFromConfig(self, keyDir, configVar, varNameString):
    cf = command_formatter()
    #cfp = config_fileprocessor() 
    from log_writer import log_writer
    lw = log_writer()
    yaml_global_config_file_and_path = cf.getConfigFileAndPath(keyDir)
    if configVar.startswith("$config."):
#      print('configVar.split(".") is: ', configVar.split("."))
#      print('configVar.split(".")[1] is: ', configVar.split(".")[1])
      configVar = self.getFirstLevelValue(yaml_global_config_file_and_path, configVar.split(".")[1])
      return configVar
    elif (configVar.startswith("$config")) and ("." not in configVar):
#      import traceback
#      traceback.print_stack()
#      print("varNameString is: ", varNameString)
      configVar = self.getFirstLevelValue(yaml_global_config_file_and_path, varNameString)
#      print("configVar is: ", configVar)
      return configVar
    else:
      logString = "ERROR: could not find value for "+varNameString+" in "+configVar
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)

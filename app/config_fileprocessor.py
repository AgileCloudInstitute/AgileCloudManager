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
  def getPlatformConfig(self, yamlFileAndPath):
    with open(yamlFileAndPath) as f:  
      topLevel_dict = yaml.safe_load(f)
    return topLevel_dict

  #@public
  def getSystemConfig(self, platformConfig, systemName):
    cfmtr = command_formatter()
    print('x platformConfig is: ', platformConfig)
    for item in platformConfig:
      print("x item is: ", item)
      print("x systemName is: ", systemName)
      if str(item).replace(" ","") == str(systemName).replace(" ","") :
        print("platformConfig.get(item) is: ", str(platformConfig.get(item)))
        print("type(platformConfig.get(item)) is: ", str(type(platformConfig.get(item))))
        if type(platformConfig.get(item)) == dict:
          print("x About to return platformConfig.get(item) ", platformConfig.get(item))
          return platformConfig.get(item)
        elif type(platformConfig.get(item)) == str:
          if (platformConfig.get(item).split(".")[1] == "yaml") or (platformConfig.get(item).split(".")[1] == "yml"):
            systemConfigFile = config_cliprocessor.inputVars.get('acmConfigPath')+cfmtr.getSlashForOS()+"systems"+cfmtr.getSlashForOS()+platformConfig.get(item)
            print("systemConfigFile is: ", systemConfigFile) 
            with open(systemConfigFile) as f:  
              topLevel_dict = yaml.safe_load(f)
            print("topLevel_dict is: ", str(topLevel_dict))
            print("...")
            return topLevel_dict.get(systemName)

  #@public
  def getSystemNames(self, platformConfig):
    instanceNames = []
    for item in platformConfig:
      if (type(platformConfig.get(item)) == dict) or (type(platformConfig.get(item)) == str):
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
    with open(yamlFileAndPath) as file:
      for line in file:
        if line.count(':') == 1:
          lineParts = line.split(":")
          key = lineParts[0].strip()
          value = lineParts[1].strip()
          if re.match(keyName, key):
            returnVal = value
        elif line.count(':') == 2:
          lineParts = line.split(":")
          key = lineParts[0].strip()
          value = lineParts[1].strip() + ":" + lineParts[2].strip()
          if re.match(keyName, key):
            returnVal = value
    return returnVal

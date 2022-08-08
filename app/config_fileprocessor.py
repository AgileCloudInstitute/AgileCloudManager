## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import config_cliprocessor
from command_formatter import command_formatter

import yaml
import re

class config_fileprocessor:

#  tfOutputDict = {}
#  foundationApply = True
#  ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
#  terraformResult = ''

  def __init__(self):  
    pass

  #@public
  def getPlatformConfig(self, yamlFileAndPath):
    with open(yamlFileAndPath) as f:  
      topLevel_dict = yaml.safe_load(f)
    return topLevel_dict

  #@public
  def getSystemNames(self, platformConfig):
    instanceNames = []
    for item in platformConfig:
      if type(platformConfig.get(item)) == dict:
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
          quit('ERROR: Invalid input for keysDir.')
      else:
        print('The invalid input for keysDir is: ', propVal)
        quit('ERROR: Invalid input for keysDir.')
    cmdfrmtr = command_formatter()
    propVal = cmdfrmtr.formatPathForOS(propVal)
#    print("bbb propVal is: ", propVal)
#    print("qqwweerrttyy config_cliprocessor.inputVars.get('dirOfOutput') is: ", config_cliprocessor.inputVars.get('dirOfOutput'))
#    quit('jjkkll')
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

## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import platform
import os 

class command_formatter:
  
  def __init__(self):  
    pass
 
  #@public
  def formatPathForOS(self, input):
    if platform.system() == "Windows":
      #First, strip down to a single \ in each location.  
      input = input.replace('\\/','\\')
      input = input.replace('/','\\')
      input = input.replace('\\\\','\\')
      input = input.replace('\\\\\\','\\')
      input = input.replace('\\\\\\\\', '\\\\')
      #Now replace singles with doubles for terraform so you get C:\\path\\to\\a\\file with proper escape sequence.
      input = input.replace('\\','\\\\')
 
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

  #@public
  def getSlashForOS(self):
    if platform.system() == 'Windows':
      return '\\'
    else:
      return '/'

  #@public
  def countSingleSlashesInString(self, inputString):
    singles = 0
    idx = 0
    for c in inputString:
      if (idx > 0) and (idx < (len(inputString)-1)):
        charBefore = inputString[idx-1]
        charAfter = inputString[idx+1]
        if c == "\\":
          if (charBefore != "\\") and (charAfter != "\\"):
            singles = singles + 1
      idx = idx+1
    return singles

  #@public
  def addSlashToString(self, inputString):
    idx = 0
    charBefore = ''
    charAfter = ''
    for c in inputString:
      if (idx > 0) and (idx < (len(inputString)-1)):
        charBefore = inputString[idx-1]
        charAfter = inputString[idx+1]
        if c == "\\":
          if (charBefore != "\\") and (charAfter != "\\"):
            fragmentBefore = inputString[0:idx]
            fragmentAfter = inputString[idx:len(inputString)]
            inputString = fragmentBefore + "\\" + fragmentAfter
      idx = idx+1
    last2 = inputString[-2:]
    if last2 != "\\\\":
      inputString = inputString + "\\\\"
    return inputString

  #This function is for getting the specific location for the keys that the admin module creates for each system
  #@public
  def getKeyFileLocation(self, instance_name):
    import config_cliprocessor
    outputDir = config_cliprocessor.inputVars.get("dirOfOutput") + instance_name + "\\"
    outputDir = self.formatPathForOS(outputDir)
    if not os.path.exists(outputDir):
      os.makedirs(outputDir)
    keys_file_and_path = 'invalid'
    keys_file_and_path = outputDir + 'keys.yaml'
    return keys_file_and_path

  #@public
  def getKeyFileAndPath(self, keyDir):
    yaml_keys_file_and_path = 'invalid'
    if platform.system() == "Windows":
      if keyDir[:-1] != "\\":
        keyDir = keyDir + "\\"
    if platform.system() == "Linux":
      if keyDir[:-1] != "/":
        keyDir = keyDir + "/"
    keyDir = self.formatPathForOS(keyDir)
    dirOfSourceKeys = keyDir
    yaml_keys_file_and_path = dirOfSourceKeys + 'keys.yaml'
    return yaml_keys_file_and_path

  #@public
  def formatKeyDir(self, keyDir):
    if platform.system() == "Windows":
      if keyDir[-1] != '\\':
        keyDir = keyDir + '\\'
    elif platform.system() == "Linux":
      if keyDir[-1] != '/':
        keyDir = keyDir + '/'
    keyDir = self.formatPathForOS(keyDir)
    return keyDir

  #@public
  def convertPathForOS(self, pathToApplicationRoot, relativePath):
    if platform.system() == 'Windows':
      if '/' in relativePath:
        relativePath = relativePath.replace("/", "\\\\")
      destinationCallParent = pathToApplicationRoot + relativePath
    else:
      if '\\' in relativePath:
        relativePath = relativePath.replace('\\', '/')
      destinationCallParent = pathToApplicationRoot + relativePath
    return destinationCallParent

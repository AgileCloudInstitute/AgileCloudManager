## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import yaml
import re
import sys
import csv
import platform

import logWriter
import config_cliprocessor
import command_builder

def getFoundationInstanceName(yamlFileAndPath):
  instanceName = ""  
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("networkFoundation", item):
        foundationItems = topLevel_dict.get(item)
        for foundationItem in foundationItems: 
          if re.match("instanceName", foundationItem):
            instanceName = foundationItems.get(foundationItem)
  return instanceName

def getPreProcessor(yamlFileAndPath, type, typeName, instName):
  preprocessor = {}  
  if type == 'networkFoundation':
    with open(yamlFileAndPath) as f:  
      topLevel_dict = yaml.safe_load(f)
      for item in topLevel_dict:
        if re.match("networkFoundation", item):
          foundationItems = topLevel_dict.get(item)
          for foundationItem in foundationItems: 
            if re.match("preprocessor", foundationItem):
              preprocessor = foundationItems.get(foundationItem)
  elif type == 'serviceInstance':
    with open(yamlFileAndPath) as f:  
      topLevel_dict = yaml.safe_load(f)
      for item in topLevel_dict:
        if re.match('systems', item):
          systemsTypes = topLevel_dict.get(item)
          for systemsType in systemsTypes:
            if re.match(typeName, systemsType):
              items = systemsTypes.get(systemsType)
              for instance in items: 
                instanceName = instance.get("instanceName")
                if len(instanceName) > 0:
                  if instName == instanceName:
                    for instanceItem in instance:
                      if re.match("preprocessor", instanceItem):
                        preprocessor = instance.get(instanceItem)
  return preprocessor

def getPostProcessor(yamlFileAndPath, type, typeName, instName):  
  postprocessor = {}  
  if type == 'networkFoundation':
    with open(yamlFileAndPath) as f:  
      topLevel_dict = yaml.safe_load(f)
      for item in topLevel_dict:
        if re.match("networkFoundation", item):
          foundationItems = topLevel_dict.get(item)
          for foundationItem in foundationItems: 
            if re.match("postprocessor", foundationItem):
              postprocessor = foundationItems.get(foundationItem)
  elif type == 'serviceInstance':
    with open(yamlFileAndPath) as f:  
      topLevel_dict = yaml.safe_load(f)
      for item in topLevel_dict:
        if re.match('systems', item):
          systemsTypes = topLevel_dict.get(item)
          for systemsType in systemsTypes:
            if re.match(typeName, systemsType):
              items = systemsTypes.get(systemsType)
              for instance in items: 
                instanceName = instance.get("instanceName")
                if len(instanceName) > 0:
                  if instName == instanceName:
                    for instanceItem in instance:
                      if re.match("postprocessor", instanceItem):
                        postprocessor = instance.get(instanceItem)
  return postprocessor

def getTopLevelProperty(yamlFileAndPath, typeName, propertyName):
  propVal = ""  
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match(typeName, item):
        typeItems = topLevel_dict.get(item)
        for typeItem in typeItems: 
          if re.match(propertyName, typeItem):
            propVal = typeItems.get(typeItem)
  return propVal

def checkTopLevelType(yamlFileAndPath, typeName):
  returnVal = False
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match(typeName, item):
        returnVal = True
  return returnVal



##############################################################################
##############################################################################

def getDependencyProperty(yamlConfigFileAndPath, typeParent, instanceName, propertyName):
  propertyValue = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if (typeParent == 'dependencies'):
        if key == typeParent:
          childTypes = my_dict.get(key)
          for instanceOfType in childTypes: 
            if instanceOfType.get("name") == instanceName:
              propertyValue = instanceOfType.get(propertyName)
      else:  
        logString = "The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation."
        logWriter.writeLogVerbose("acm", logString)
  return propertyValue

def getDependencyVersionSecondLevel(yamlConfigFileAndPath, typeParent, instanceName, propertyName, grandChild):
  propertyValue = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if (typeParent == 'dependencies'):
        if key == typeParent:
          childTypes = my_dict.get(key)
          for instanceOfType in childTypes: 
            if instanceOfType.get("name") == instanceName:
              propertyValue = instanceOfType.get(propertyName)
              if type(propertyValue) is list:
                for myListItem in propertyValue:
                  if myListItem.get('name') == grandChild:
                    propertyValue = myListItem.get('version')
              else:
                quit("ERROR: Invalid dependency configuration in infrastructureConfig.yaml.  Halting program so you can diagnose the source of the problem.  ")
      else:  
        logString = "The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation."
        logWriter.writeLogVerbose("acm", logString)
  return propertyValue

def getDependencyVersion(yamlFileAndPath, dependency):
  version = ""  
  match = False  
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)  
    for item in topLevel_dict:  
      if re.match("dependencies", item):    
        deps = topLevel_dict.get(item)  
        for dep in deps: 
          if dependency == dep.get("name"):
            version = dep.get("version")  
            match = True  
  if match == True:
    return version
  else: 
    quit("ERROR: The dependency is not listed in the config file.  Halting program so you can look for the root cause of the problem before proceeding. ")

##############################################################################
##############################################################################

def getSourceCodeProperty(yamlConfigFileAndPath, typeParent, instanceName, propertyName):
  propertyValue = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if (typeParent == 'source'):
        if key == typeParent:
          childTypes = my_dict.get(key)
          for instanceOfType in childTypes: 
            if instanceOfType.get("instanceName") == instanceName:
              propertyValue = instanceOfType.get(propertyName)
      else:  
        logString = "The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation."
        logWriter.writeLogVerbose("acm", logString)
  return propertyValue

def getImageInstanceNames(yamlFileAndPath, typeName):
  instanceNames = []
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match('imageBuilds', item):
        imageBuildsTypes = topLevel_dict.get(item)
        for imageBuildsType in imageBuildsTypes:
          if re.match(typeName, imageBuildsType):
            items = imageBuildsTypes.get(imageBuildsType)
            for instance in items: 
              if isinstance(instance, str):
                if instance == "instanceName":  
                  instanceName = items.get(instance)
                  if len(instanceName) > 0:
                    instanceNames.append(instanceName)
              else:  
                instanceName = instance.get("instanceName")
                if len(instanceName) > 0:
                  instanceNames.append(instanceName)
  return instanceNames

def getSystemInstanceNames(yamlFileAndPath, typeName):
  instanceNames = []
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match('systems', item):
        systemsTypes = topLevel_dict.get(item)
        for systemsType in systemsTypes:
          if re.match(typeName, systemsType):
            items = systemsTypes.get(systemsType)
            for instance in items: 
              instanceName = instance.get("instanceName")
              if len(instanceName) > 0:
                instanceNames.append(instanceName)
  return instanceNames

def getSystemPropertyValue(yamlFileAndPath, typeName, instName, propName):
  propVal = "empty"
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match('systems', item):
        systemsTypes = topLevel_dict.get(item)
        for systemsType in systemsTypes:
          if re.match(typeName, systemsType):
            items = systemsTypes.get(systemsType)
            if typeName == "tfBackend":
              print("... items is: ", items)
            for instance in items: 
              instanceName = instance.get("instanceName")
              if len(instanceName) > 0:
                if instName == instanceName:
                  propVal = instance.get(propName)
  return propVal

def getPropertyCoordinatesFromCSV(infraConfigFileAndPath, templateName, propName):
  cloud = getCloudName(infraConfigFileAndPath)
  if len(cloud) < 2:
    quit("ERROR: cloud name not valid.  Add better validation checking to the code. ")
  userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
  path_to_application_root = ''
  module_config_file_and_path = ''
  if templateName.count('/') == 2:
    nameParts = templateName.split("/")
    if (len(nameParts[0]) > 1) and (len(nameParts[1]) >1) and (len(nameParts[2]) > 1): 
      template_Name = nameParts[2]  
      path_to_application_root = userCallingDir + nameParts[0] + "\\" + nameParts[1] + "\\"
      module_config_file_and_path = userCallingDir + nameParts[0] + '\\variableMaps\\' + template_Name + '.csv'
    else:
      quit('ERROR: templateName is not valid. ')
  else:  
    quit("Template name is not valid.  Must have only one /.  ")
  varSnip = "empty"
  varsFragment = ''
  coordinates = ''
  path_to_application_root = command_builder.formatPathForOS(path_to_application_root)
  module_config_file_and_path = command_builder.formatPathForOS(module_config_file_and_path)

  print("path_to_application_root is: ", path_to_application_root)
  print("module_config_file_and_path is: ", module_config_file_and_path)
  print("propName is: ", propName)

  c = open(module_config_file_and_path,'r')
  o = csv.reader(c)
  for r in o:
    if r[0] == propName:
      coordinates = r[1] + '/' + r[2]
  print("coordinates is: ", coordinates)
#  quit("y@!")
  return coordinates

def getCodeInstanceNames(yamlFileAndPath, projInst):
  instanceNames = []
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match('systems', item):
        pmTypes = topLevel_dict.get(item)
        for pmType in pmTypes:
          if re.match('projects', pmType):
            items = pmTypes.get(pmType)
            for instance in items: 
              instanceName = instance.get("instanceName")
              if len(instanceName) > 0:
                if projInst == instanceName:
                  codeInstances = instance.get('code')
                  if codeInstances is not None:
                    for codeInst in codeInstances:
                      codeInstName = codeInst.get('instanceName')
                      instanceNames.append(codeInstName)
  return instanceNames

def getInstanceNames(yamlFileAndPath, typeName):
  instanceNames = []
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match(typeName, item):
        items = topLevel_dict.get(item)
        for instance in items: 
          if type(instance) == str:
            if instance == 'instanceName':
              instanceName = items.get(instance)
              if len(instanceName) > 0:
                instanceNames.append(instanceName)
          elif type(instance) == dict:
            instanceName = instance.get("instanceName")
            if len(instanceName) > 0:
              instanceNames.append(instanceName)
  return instanceNames

def getPropertyFromFirstLevelList(yamlFileAndPath, typeName, instanceName, propertyName):
  propVal = 'empty'
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match(typeName, item):
        items = topLevel_dict.get(item)
        for instance in items: 
          if instance.get('instanceName') == instanceName:
            for prop in instance:
              if prop == propertyName:  
                propVal = instance.get(prop)
  return propVal

def getKeyDir(yamlFileAndPath, typeName, instanceName):
  propertyName = 'keysDir'
  propVal = getPropertyFromFirstLevelList(yamlFileAndPath, typeName, instanceName, propertyName)
  if propVal == '$Default':
    propVal = config_cliprocessor.inputVars.get('dirOfYamlKeys')
  elif '$Output' in propVal:
    propParts = propVal.split('\\')
    if len(propParts) == 2:
      if propParts[0] == '$Output':
        outputDir = config_cliprocessor.inputVars.get('dirOfOutput')
        propVal = outputDir + propParts[1] 
      else:
        print('The invalid input for keysDir is: ', propVal)
        quit('ERROR: Invalid input for keysDir.')
    else:
      print('The invalid input for keysDir is: ', propVal)
      quit('ERROR: Invalid input for keysDir.')
  propVal = command_builder.formatPathForOS(propVal)
  return propVal

#..
def getForce(yamlFileAndPath, typeName, instanceName):
  propertyName = 'forceDelete'
  propVal = getPropertyFromFirstLevelList(yamlFileAndPath, typeName, instanceName, propertyName)
  print('propVal is: ', propVal)
#  quit('^^')
  if (propVal == 'True') or (propVal == True):
    return True
  else:
    return False
#..

def listTypesInImageBuilds(yamlInfraFileAndPath):
  typesList = []
  with open(yamlInfraFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if (re.match('imageBuilds', key)):
        imageBuilderTypes = my_dict.get(key)
        for imageBuilderType in imageBuilderTypes:
          typesList.append(imageBuilderType)
  return typesList

def listTypesInSystem(yamlInfraFileAndPath):
  typesList = []
  with open(yamlInfraFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if (re.match('systems', key)):
        systemTypes = my_dict.get(key)
        for systemType in systemTypes:
          typesList.append(systemType)
  return typesList

def getImageSpecs(yamlInfraFileAndPath):
  typesList = []
  with open(yamlInfraFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if (re.match('imageBuilds', key)):
        imageBuilderTypes = my_dict.get(key)
        for imageBuilderType in imageBuilderTypes:
          if re.match("images", imageBuilderType):
            typesList.append(imageBuilderType)
  return typesList

def getImageTemplateName(yamlConfigFileAndPath, typeName, instanceName):
  #Work item: replace this with getImagePropertyValue() for simplicity
  templateName = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if re.match('imageBuilds', key):
        imageBuildsTypes = my_dict.get(key)
        for imageBuildsType in imageBuildsTypes:
          if re.match(typeName, imageBuildsType):
            imageBuilds = imageBuildsTypes.get(imageBuildsType)
            for imageBuild in imageBuilds:
              if imageBuild.get("instanceName") == instanceName:
                #Note: The following assumes that imageBuild is a string containing only one / with the repo in front and the template name after.  You must add better validation to avoid difficult to diagnose runtime errors.  
                templateName = imageBuild.get("templateName")
                #Note: returning here in early version to clip off a match.  Make sure to add better checking in future to make sure there is only one match.  Here, we are assuming there is only one match without checking.  The config file must include only one match to be valid.  
                print('....xyz templateName: ', templateName)
#                quit('hohoho')
                return templateName
  return templateName

def getImagePropertyValue(yamlConfigFileAndPath, typeName, instanceName, propertyName):
  propVal = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if re.match('imageBuilds', key):
        imageBuildsTypes = my_dict.get(key)
        for imageBuildsType in imageBuildsTypes:
          if re.match(typeName, imageBuildsType):
            imageBuilds = imageBuildsTypes.get(imageBuildsType)
            for imageBuild in imageBuilds:
              if imageBuild.get("instanceName") == instanceName:
                #Note: The following assumes that imageBuild is a string containing only one / with the repo in front and the template name after.  You must add better validation to avoid difficult to diagnose runtime errors.  
                propVal = imageBuild.get(propertyName)
                #Note: returning here in early version to clip off a match.  Make sure to add better checking in future to make sure there is only one match.  Here, we are assuming there is only one match without checking.  The config file must include only one match to be valid.  
                print('....xyz propVal: ', propVal)
#                quit('hohoho')
                return propVal
  return propVal

def getTemplateName(yamlConfigFileAndPath, typeParent, typeName, typeGrandChild, instanceName, grandChildName):
  templateName = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if (typeParent == 'systems') or (typeParent == 'imageBuilds'):
        if key == typeParent:
          systemTypes = my_dict.get(key)
          if type(systemTypes) is dict:
            for instancesOfType in systemTypes: 
              if instancesOfType == typeName:  
                for instance in systemTypes.get(instancesOfType):
                  if typeGrandChild != None:
                    if instanceName == instance.get('instanceName'):
                      if typeGrandChild == 'code':
                        codeInstances = instance.get('code')
                        for codeInst in codeInstances:
                          if grandChildName == codeInst.get('instanceName'):
                            templateName = codeInst.get('templateName')
                  else:
                    if isinstance(instance, str):
                      if instance == 'templateName':
                        templateName = systemTypes.get(instancesOfType).get(instance)
                    else: 
                      if instance.get('instanceName') == instanceName:
                        templateName = instance.get('templateName')
      else:  
        print('typeName is: ', typeName)
        print('key is: ', key)
        if re.match(typeName, key):
          resourceTypes = my_dict.get(key)
          if typeName == 'networkFoundation':
            print('resourceTypes is: ', str(resourceTypes))
          if type(resourceTypes) is dict:
            if typeName == 'networkFoundation':
              print('list(resourceTypes.values())[0] is: ', list(resourceTypes.values())[0])
            valueToCheck = list(resourceTypes.values())[0]
            if isinstance(valueToCheck, str):
              print('... instanceName is: ', instanceName)
              if resourceTypes.get("instanceName") == instanceName:
                templateName = resourceTypes.get("templateName")
                if typeName == 'networkFoundation':
                  print('... templateName is: ', templateName)
          elif type(resourceTypes) is list:
            for instancesOfTypes in resourceTypes:
              if instancesOfTypes.get("instanceName") == instanceName:
                templateName = instancesOfTypes.get("templateName")
  print('------------------------------------------------')
  print('yamlConfigFileAndPath is: ', yamlConfigFileAndPath)
  print('typeParent is: ', typeParent)
  print('typeName is: ', typeName)
  print('typeGrandChild is: ', typeGrandChild)
  print('instanceName is: ', instanceName)
  print('grandChildName is: ', grandChildName)
  print('------------------------------------------------')
  if instanceName == 'AZURE_BuildingBlocks':
    import traceback
    traceback.print_stack()
#    sys.exit(1)
  return templateName


def getFirstLevelValue(yamlFileAndPath, keyName):
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


def getSecondLevelProperty(yamlConfigFileAndPath, typeParent, typeName, instanceName, propertyName):
  propertyValue = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if (typeParent == 'systems') or (typeParent == 'imageBuilds') or (typeParent == 'releaseDefinition'):
        if key == typeParent:
          childTypes = my_dict.get(key)
          if type(childTypes) is dict:
            for instancesOfType in childTypes: 
              if instancesOfType == typeName:  
                for instance in childTypes.get(instancesOfType):
                  print('instance is: ', str(instance))
                  if isinstance(instance, str):
                    logString = "instance is a string. "
                    logWriter.writeLogVerbose("acm", logString)
                  else: 
                    if instance.get('instanceName') == instanceName:
                      propertyValue = instance.get(propertyName)
      else:  
        logString = "The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation."
        logWriter.writeLogVerbose("acm", logString)
  if instanceName == 'AWS_BuildingBlocks':
    print('instanceName is: ', instanceName)
    print('propertyValue is: ', propertyValue)
#    quit('$1!')
  return propertyValue

def getThirdLevelProperty(yamlConfigFileAndPath, typeParent, typeChild, childName, grandChildType, grandChildName, propertyName):
  propertyValue = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if typeParent == 'systems':
        if key == typeParent:
          childTypes = my_dict.get(key)
          if type(childTypes) is dict:
            for instancesOfType in childTypes: 
              if instancesOfType == typeChild:  
                for child in childTypes.get(instancesOfType):
                  if not isinstance(child, str):
                    grandChildren = child.get(grandChildType)
                    for grandKid in grandChildren:
                      if grandKid.get('instanceName') == grandChildName:
                        propertyValue = grandKid.get(propertyName)
      else:  
        logString = "The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation."
        logWriter.writeLogVerbose("acm", logString)
  return propertyValue

def getCloudName(yamlConfigFileAndPath):
  cloud = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if re.match('cloud', key):
        if isinstance(value, str):
          cloud = value
        else:  
          quit("Value for cloud is not a string.  Halting program so that you can validate your configuration.  ")
  if len(cloud) < 2:
    quit("ERROR: cloud name not valid.  Add better validation checking to the code. ")
  return cloud

def getImageRepoDir(yamlConfigFileAndPath, instanceName):
  #Note:  Here we are assuming a properly formatted input string with the repo name at the left of a single /.  Make sure to add proper validation later to ensure that any data passing through here is valid.  
  templateRepo = instanceName.split('/')[0] + '\\' + instanceName.split('/')[1]
  userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
  templateRepoDir = userCallingDir + templateRepo
  templateRepoDir = command_builder.formatPathForOS(templateRepoDir)
  return templateRepoDir

def getYamlKeysFileAndPath(keyDir):
  if platform.system() == "Windows":
    if keyDir[:-1] != "\\":
      keyDir = keyDir + "\\"
  if platform.system() == "Linux":
    if keyDir[:-1] != "/":
      keyDir = keyDir + "/"
  yamlKeysPath = keyDir.replace("\\\\","\\")
  yamlKeysPath = command_builder.formatPathForOS(yamlKeysPath)
  yamlKeysFileAndPath = yamlKeysPath + 'keys.yaml'
  return yamlKeysFileAndPath
 
def getGitPassFromSourceKeys(sourceKeys):
  ### Get gitPass variable from the file indicated by the sourceKeys variable.  
  gitPassCount = 0
  gitPass = None
  if sourceKeys != None:
    with open(sourceKeys) as file:
      for item in file:
        itemParts = item.split(':')
        if itemParts[0].replace(' ','') == 'gitPass':
          gitPass = itemParts[1].replace(' ','')
          gitPassCount += 1
  else:
    logString = "ERROR: ACM_SOURCE_KEYS environment variable was not found."
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  if gitPassCount == 0:
    logString = "ERROR: gitPass variable not found in sourceKeys file. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  elif gitPassCount > 1:
    logString = "ERROR: Multiple values for gitPass were found in sourceKeys file.  Only one record for gitPass is allowed as input."
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  elif gitPassCount == 1:
    pass
  return gitPass

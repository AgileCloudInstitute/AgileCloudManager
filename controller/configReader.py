## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import yaml
import re
import os

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

def getAdminInstanceName(yamlFileAndPath):
  instanceName = ""  
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match("admin", item):
        foundationItems = topLevel_dict.get(item)
        for foundationItem in foundationItems: 
          if re.match("instanceName", foundationItem):
            instanceName = foundationItems.get(foundationItem)
  return instanceName

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

def getProjectManagementInstanceNames(yamlFileAndPath, typeName, grandChild):
  instanceNames = []
  if typeName.count('/') == 1:
    if grandChild != None:
      grandChild = typeName.split('/')[1]
      typeName = typeName.split('/')[0]
  elif typeName.count('/') > 1:
    quit("ERROR: too many / inside typeName. ")
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match('projectManagement', item):
        pmTypes = topLevel_dict.get(item)
        for pmType in pmTypes:
          if re.match(typeName, pmType):
            items = pmTypes.get(pmType)
            for instance in items: 
              if grandChild != None:
                for grandKid in instance:
                  if grandKid == grandChild:
                    grandChildren = instance.get(grandKid)
                    for grandChildInstance in grandChildren:  
                      instanceName = grandChildInstance.get('instanceName')
                      if len(instanceName) > 0:
                        instanceNames.append(instanceName)
              else:
                instanceName = instance.get("instanceName")
                if len(instanceName) > 0:
                  instanceNames.append(instanceName)
  return instanceNames

def getCodeInstanceNames(yamlFileAndPath, projInst):
  instanceNames = []
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match('projectManagement', item):
        pmTypes = topLevel_dict.get(item)
        for pmType in pmTypes:
          if re.match('projects', pmType):
            items = pmTypes.get(pmType)
            for instance in items: 
              instanceName = instance.get("instanceName")
              if len(instanceName) > 0:
                if projInst == instanceName:
                  codeInstances = instance.get('code')
                  for codeInst in codeInstances:
                    codeInstName = codeInst.get('instanceName')
                    instanceNames.append(codeInstName)
  return instanceNames


def getReleaseDefinitionInstanceNames(yamlFileAndPath, typeName):
  instanceNames = []
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match('releaseDefinition', item):
        pmTypes = topLevel_dict.get(item)
        for pmType in pmTypes:
          if re.match(typeName, pmType):
            items = pmTypes.get(pmType)
            for instance in items: 
              instanceName = instance.get("instanceName")
              if len(instanceName) > 0:
                instanceNames.append(instanceName)
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

def getRegion(yamlFileAndPath) :  
  region = "Error: No valid region was supplied. "  
  with open(yamlFileAndPath) as f:  
    my_dict = yaml.safe_load(f)  
    for key, value in my_dict.items():  
      if re.match("networkFoundation", key):
        netFoundationItems = my_dict.get(key)
        for networkItem in netFoundationItems:
          if re.match("region", networkItem):
            region = netFoundationItems.get(networkItem) 
  return region

def listTheTypes(yamlInfraFileAndPath):
  typesList = []
  with open(yamlInfraFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      #Put the following 3 blocked types into a dict later to separate config from code.  We are keeping them here now because we do NOT want to allow users to modify this in the current vesion of this software.
      if (re.match('networkFoundation', key)) or (re.match('admin', key)) or (re.match('tags', key)):
        print("Not importing networkFoundation, admin, or tags here because they are secondary to the present operation.  ")
      else:
        typesList.append(key)
  return typesList

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
                return templateName
  return templateName

def getTemplateName(yamlConfigFileAndPath, typeParent, typeName, typeGrandChild, instanceName, grandChildName):
  templateName = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if (typeParent == 'systems') or (typeParent == 'imageBuilds') or (typeParent == 'projectManagement'):
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
        if re.match(typeName, key):
          resourceTypes = my_dict.get(key)
          if type(resourceTypes) is dict:
            valueToCheck = list(resourceTypes.values())[0]
            if isinstance(valueToCheck, str):
              if resourceTypes.get("instanceName") == instanceName:
                templateName = resourceTypes.get("templateName")
          elif type(resourceTypes) is list:
            for instancesOfTypes in resourceTypes:
              if instancesOfTypes.get("instanceName") == instanceName:
                templateName = instancesOfTypes.get("templateName")
  return templateName


def getFirstLevelValue(yamlFileAndPath, keyName):
  returnVal = ""  
  with open(yamlFileAndPath) as f:  
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      if re.match(keyName, item):
        returnVal = topLevel_dict.get(item)
  return returnVal


def getSecondLevelProperty(yamlConfigFileAndPath, typeParent, typeName, instanceName, propertyName):
  propertyValue = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if (typeParent == 'systems') or (typeParent == 'imageBuilds') or (typeParent == 'projectManagement') or (typeParent == 'releaseDefinition'):
        if key == typeParent:
          childTypes = my_dict.get(key)
          if type(childTypes) is dict:
            for instancesOfType in childTypes: 
              if instancesOfType == typeName:  
                for instance in childTypes.get(instancesOfType):
                  if isinstance(instance, str):
                    print("instance is a string. ")
                  else: 
                    propertyValue = instance.get(propertyName)
      else:  
        print("The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation.")
  return propertyValue

def getThirdLevelProperty(yamlConfigFileAndPath, typeParent, typeChild, childName, grandChildType, grandChildName, propertyName):
  propertyValue = ''
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if typeParent == 'projectManagement':
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
        print("The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation.")
  return propertyValue


def getThirdLevelList(yamlConfigFileAndPath, typeParent, typeName, instanceName, subTypeName, propertyName):
  propertyValuesList = []
  with open(yamlConfigFileAndPath) as f:  
    my_dict = yaml.safe_load(f)
    for key, value in my_dict.items():  
      if (typeParent == 'systems') or (typeParent == 'imageBuilds') or (typeParent == 'projectManagement') or (typeParent == 'releaseDefinition'):
        if key == typeParent:
          childTypes = my_dict.get(key)
          if type(childTypes) is dict:
            for instancesOfType in childTypes: 
              if instancesOfType == typeName:  
                for instance in childTypes.get(instancesOfType):
                  if isinstance(instance, dict):
                    thisDict = instance.get(subTypeName)
                    for thisInstance in thisDict:
                      thisPropertyValue = thisInstance.get(propertyName)
                      propertyValuesList.append(thisPropertyValue)
                  else: 
                    propertyValue = instance.get(propertyName)
                    propertyValuesList.append(propertyValue)
      else:  
        print("The value given for for typeParent is NOT supported.  Please check your configuration file and the documentation.")
  return propertyValuesList


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
  return cloud

def getImageRepoDir(yamlConfigFileAndPath, instanceName):
  #Note:  Here we are assuming a properly formatted input string with the repo name at the left of a single /.  Make sure to add proper validation later to ensure that any data passing through here is valid.  
  templateRepo = instanceName.split('/')[0] + '\\' + instanceName.split('/')[1]
  app_parent_path = os.path.dirname(os.path.realpath("..\\")) + '\\'
  templateRepoDir = app_parent_path + templateRepo
  return templateRepoDir

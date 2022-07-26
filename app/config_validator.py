## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import yaml

import config_cliprocessor

class config_validator:
  
  def __init__(self):  
    pass
 
  #@public
  def processAcmConfig(self):
    infraConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    #First, validate that every system has a unique name in acm.yaml
    typesList = []
    with open(infraConfigFileAndPath, 'r') as f:
      for row in enumerate(f):
        if (not row[1].startswith(" ")) and(not row[1].startswith("#")) and (len(row[1].replace(" ","").replace("\n","")) > 0):
          typeName = row[1].replace(" ","").replace("\n","")
          typesList.append(typeName)
    if len(typesList) != len(set(typesList)):
      logString = "ERROR: Your configuration uses the same name to define multiple systems.  You must give each of your system instances a unique name within each platform configuration.  Halting program so you can fix your configuration. "
      quit(logString)
    #Second, load acm.yaml into a dict and iterate the systems:
    with open(infraConfigFileAndPath, 'r') as f:
      acmConfig = yaml.safe_load(f)
    #Third, validate each system
    for system in acmConfig:
      #System config must be a dictionary
      if (isinstance(acmConfig.get(system), dict)) and (isinstance(system, str)):
        self.validateSystem(acmConfig.get(system))
      else:
        logString = "ERROR: Invalid format for system named "+ str(system)+". The contents of a system must be valid yaml and not just a string. "
        quit(logString)

  #@private
  def validateSystem(self, system):
    validSystemKeysList = ['keysDir', 'forceDelete', 'cloud', 'organization', 'tags', 'foundation', 'serviceTypes']
    #Confirm that each top level key within system is unique
    if len(system) != len(set(system)):
      logString = "ERROR: Each top level key name within each system must be unique and must be one of the following names: "+str(validSystemKeysList)
      quit(logString)
    #Confirm that each system configuration contains at least the following fields: 'keysDir', 'cloud', 'organization', 'serviceTypes'
    if 'keysDir' not in system:
      logString = 'ERROR: system must contain exactly one keysDir.'
      quit(logString)
    if 'cloud' not in system:
      logString = 'ERROR: system must contain exactly one cloud.'
      quit(logString)
    if 'organization' not in system:
      logString = 'ERROR: system must contain exactly one organization.'
      quit(logString)
    if 'serviceTypes' not in system:
      logString = 'ERROR: system must contain exactly one serviceTypes.'
      quit(logString)
    #Validate the top level items within the sytem dict.
    for systemItem in system:
      #Top level keys within system must be string keys and NOT lists.
      if isinstance(systemItem, str):
        #Each top level key string must be one of the key names in validSystemKeysList
        if systemItem not in validSystemKeysList:
          logString = 'ERROR: Illegal top-level field name in system: '+systemItem
          quit(logString)
        else: 
          if systemItem == 'keysDir':
            #Must be string
            if not isinstance(system.get(systemItem), str):
              quit("ERROR: The value of keysDir did not evaluate to a string. ")
          if systemItem == 'forceDelete':
            #Must be True or False if present
            if not isinstance(system.get(systemItem), bool):
              quit("ERROR: The value of forceDelete did not evaluate to either True or False. ")
          if systemItem == 'cloud':
            #Must be string
            if not isinstance(system.get(systemItem), str):
              quit("ERROR: The value of cloud did not evaluate to a string. ")
          if systemItem == 'organization':
            #must be string
            if not isinstance(system.get(systemItem), str):
              quit("ERROR: The value of organization did not evaluate to a string. ")
          if systemItem == 'tags':
            #Must be a dict of key/value pairs with string values for each key if present
            if isinstance(system.get(systemItem), dict):
              for tagKey in system.get(systemItem):
                #Each tag must evaluate to a string
                if not isinstance(system.get(systemItem).get(tagKey), str):
                  quit("ERROR: The value of every tag must evaluate to a string. ")
            else:
              quit("ERROR: The value of the tags block did not evaluate to a dictionary. ")
          if systemItem == 'foundation':
            self.validateFoundation(system.get(systemItem))
          if systemItem == 'serviceTypes':
            #serviceTypes block must be a dictionary
            if isinstance(system.get(systemItem), dict):
              for typeOfService in system.get(systemItem):
                self.validateTypeOfService(system.get(systemItem).get(typeOfService))
            else:
              quit("ERROR: The value of the serviceTypes block did not evaluate to a dictionary. ")
      else:
        logString = "ERROR: Illegal object in top level of system. The items within each system must have one of the following unique names: "+str(validSystemKeysList)
        quit(logString)

  #@private
  def validateFoundation(self, foundationDict):
    #Must be a dict of key/value pairs.  The following keys in dict:
    # instanceName must be string and must be present
    # templateName must be string and must be present
    # controller must be string, must be present, and must have one of a specific set of specific values
    # mappedVariables optional, but must be dict of key/value pairs with string values for each key if present.
    # images optional, but must have specific complex structure if present.
    if isinstance(foundationDict, dict):
      if 'instanceName' not in foundationDict.keys():
        quit("ERROR: foundation must have an instanceName. ")
      if 'templateName' not in foundationDict.keys():
        quit("ERROR: foundation must have a templateName. ")
      if 'controller' not in foundationDict.keys():
        quit("ERROR: foundation must have a controller. ")
      for foundationKey in foundationDict:
        #instanceName, templateName, controller must contain strings
        if (foundationKey == 'instanceName') or (foundationKey == 'templateName') or (foundationKey == 'controller'):
          if not isinstance(foundationDict.get(foundationKey), str):
            logString = "ERROR: Value of "+foundationKey+" must evaluate to a string. "
            quit(logString)
        if (foundationKey == 'mappedVariables') or (foundationKey == 'backendVariables'):
          #mappedVariables and backendVariables must be a dictionary
          self.validateMappedVariables(foundationDict.get(foundationKey))
        if foundationKey == 'images':
          if isinstance(foundationDict.get(foundationKey), list):
            for image in foundationDict.get(foundationKey):
              self.validateImageDefinition(image)
          else:
            quit("ERROR: The images block inside the foundation must be a list of dictionary definitions of one or more individual images. ")
    else:
      quit("ERROR: The value of foundation block did not evaluate to a dictionary. ")

  #@private
  def validateImageDefinition(self, image):
    #image must be a dictionary
    if isinstance(image, dict):
      #Each image must contain these four variables: instanceName, templateName, controller, mappedVariables
      if 'instanceName' not in image.keys():
        quit("ERROR: Each image definition must contain an instanceName. ")
      if 'templateName' not in image.keys():
        quit("ERROR: Each image definition must contain a templateName. ")
      if 'controller' not in image.keys():
        quit("ERROR: Each image definition must contain a controller. ")
      if 'mappedVariables' not in image.keys():
        quit("ERROR: Each image definition must contain a mappedVariables section. ")
      for imageKey in image:
        if isinstance(image.get(imageKey), dict):
          #The only dictionary key allowed in an image definition is a mappedVariables block
          if imageKey == "mappedVariables":
            #mappedVariables must be a dictionary
            self.validateMappedVariables(image.get(imageKey))
          else:
            quit("ERROR: Each key in an image definition must either have a string value, or must be a mappedVariables block. ")
        #All other variables in an image definition must evaluate to strings. 
        elif not isinstance(image.get(imageKey), str):
          quit("ERROR: Each key in an image definition must either have a string value, or must be a mappedVariables block. ")
    else:
      quit("ERROR: Each image definition must be a dictionary of key/value pairs.  ")

  #@private
  def validateTypeOfService(self, serviceType):
    #Each type of service must be a dictionary
    if isinstance(serviceType, dict):
      #An instances block must be present within each type of service
      if 'instances' not in serviceType.keys():
        quit("ERROR: Each type of service must have a block defining instances. ")
      for keyInTypeOfService in serviceType:
        if keyInTypeOfService == "sharedVariables":
          #sharedVariables must be a dict
          if isinstance(serviceType.get(keyInTypeOfService), dict):
            for varGroupName in serviceType.get(keyInTypeOfService):
              if varGroupName == "mappedVariables":
                self.validateMappedVariables(serviceType.get(keyInTypeOfService).get(varGroupName))
              #mappedVariables is the only field name allowed within a sharedVariables block.
              else:
                quit("ERROR: Your configuration has a field named anything other than mappedVariables within a sharedVariables block. ")
          else:
            quit("ERROR: Each sharedVariables block must evaluate to a dictionary that contains one key named mappedVariables. ")
        if keyInTypeOfService == "instances":
          #instances block must be a list
          if isinstance(serviceType.get(keyInTypeOfService), list):
            for instance in serviceType.get(keyInTypeOfService):
              self.validateInstanceOfService(instance)
          else:
            quit("ERROR: The contents of an instances block within a type of service must evaluate to a yaml list. ")
    else:
      quit("ERROR: The block that defines each type of service must evaluate to a dictionary. ")

  #@private
  def validateInstanceOfService(self, instance):
    #Each instance of each type of service must evaluate to a dictionary.
    if isinstance(instance, dict):
      #Every instance must contain the following 3 fields: instanceName, templateName, controller
      if 'instanceName' not in instance.keys():
        quit("ERROR: Each instance of each type of service must have an instanceName field.  ")
      if 'templateName' not in instance.keys():
        quit("ERROR: Each instance of each type of service must have a templateName field.  ")
      if 'controller' not in instance.keys():
        quit("ERROR: Each instance of each type of service must have a controller field.  ")
      for instanceKey in instance:
        if (instanceKey == "mappedVariables") or (instanceKey == "backendVariables")  or (instanceKey == "preprocessor")  or (instanceKey == "postprocessor") :
          #mappedVariables section and backendVariables section must be a dictionary of key/value pairs
          self.validateMappedVariables(instance.get(instanceKey))
        else:
          #All other keys in an instance of a service must have associated values that are strings
          if not isinstance(instance.get(instanceKey), str):
            print(str(instance.get(instanceKey)))
            quit("ERROR: All fields within each instance of each type of service must have string values, with the exception of mappedVariables, backendVariables, preprocessor, and postprocessor sections, which themselves must each be a dictionary of key/value pairs.  ")
    else:
      quit("ERROR: Each instance of each instance of a serviceType must be a dictionary. ")

  #@private
  def validateMappedVariables(self, mappedVarsBlock):
    #mappedVariables section must be a dictionary of key/value pairs
    if isinstance(mappedVarsBlock, dict):
      for mappedVar in mappedVarsBlock:
        #Each variable defined in the mappedVariables block must be a string
        if not isinstance(mappedVarsBlock.get(mappedVar), str):
          logString = "ERROR: Value of each of the variables within each mappedVariables block must be a string.  You are seeing this because at least one of the variables defined within a mappedVariables block is not a string. "
          quit(logString)
    else:
      quit("ERROR: The contents of each mappedVariables block must evaluate to a dictionary.")

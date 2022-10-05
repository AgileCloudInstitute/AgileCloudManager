## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import sys
import io

from config_fileprocessor import config_fileprocessor
from command_formatter import command_formatter
from log_writer import log_writer


class changes_taxonomy:
  
  def __init__(self):  
    self.changeTaxonomy = {}
    self.changeReports = []
    self.changeCounter = 0
 
  changeTaxonomy = {}
  changeReports = []
  changeCounter = 0

  #@public
  def assembleChangeTaxonomy(self, level, command):
    cfp = config_fileprocessor()
    lw = log_writer()
    import config_cliprocessor
    yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    platformConfig = cfp.getPlatformConfig(yamlPlatformConfigFileAndPath)
    if level == 'platform':
      self.createTopLevelOfChangeTaxonomy(command, platformConfig)
      for systemInstance in platformConfig:
        sysCfg = cfp.getSystemConfig(platformConfig, systemInstance)
        serviceTypes = sysCfg.get("serviceTypes")
        systemDict = { }
        systemDict["name"] = systemInstance
        systemDict["status"] = "NOT Started"
        systemDict["currentStep"] = 0
        if cfp.systemHasFoundation(sysCfg):
          foundationInstanceName = sysCfg.get("foundation").get("instanceName")
          systemDict["steps"] = len(serviceTypes)+1 #numStepsEntireSystem ADDS foundation
          systemDict["foundation"] = self.createFoundationDict(foundationInstanceName)
          if "images" in sysCfg.get("foundation").keys():
            images = sysCfg.get("foundation").get("images")
            if len(images) > 0:
              systemDict["images"] = self.createImagesSummary(len(images))
              for image in images:
                systemDict["images"]["instances"][image.get("instanceName")] = self.createImageInstanceDict()
        else:
          systemDict["steps"] = len(serviceTypes) #numStepsEntireSystem does NOT add foundation
          logString = "WARNING: There is NOT any networkFoundation block"
          lw.writeLogVerbose("acm", logString)
        systemDict["services"] = self.createServicesSummaryDict(len(serviceTypes))
        for serviceType in serviceTypes:
          numServiceInstances = len(serviceTypes.get(serviceType))
          serviceDict = self.createServiceTypeSummaryDict(numServiceInstances, serviceType)
          serviceInstances = {}
          for serviceInstanceName in serviceTypes.get(serviceType).get("instances"):
            instanceDict = {"status":"NOT Started", "steps":1, "currentStep":0}
            serviceInstances[serviceInstanceName.get("instanceName")] = instanceDict
          serviceDict["instances"] = serviceInstances
          systemDict["services"]["serviceTypes"].append(serviceDict)
        self.changeTaxonomy["systemsToChange"].append(systemDict)
    elif level == 'foundation':
      self.createTopLevelOfChangeTaxonomy_FoundationOnly(command)
      systemInstanceName = config_cliprocessor.inputVars.get('systemName')
      systemDict = { }
      systemDict["name"] = systemInstanceName
      systemDict["status"] = "NOT Started"
      systemDict["currentStep"] = 0
      systemConfig = cfp.getSystemConfig(platformConfig, systemInstanceName)
      if 'foundation' in systemConfig.keys():
        systemDict["steps"] = 1 #foundation is only one step
        systemDict["foundation"] = self.createFoundationDict(systemConfig.get('foundation').get('instanceName'))
        if 'images' in systemConfig.get('foundation').keys():
          images = systemConfig.get("foundation").get("images")
          if len(images) > 0:
            systemDict["images"] = self.createImagesSummary(len(images))
            for image in images:
              imageInstanceName = image.get("instanceName")
              systemDict["images"]["instances"][imageInstanceName] = self.createImageInstanceDict()
        self.changeTaxonomy["systemsToChange"].append(systemDict)
      else:
        logString = 'ERROR: There is no foundation specified in your yaml config file, but you are running a foundation cli command.'
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    elif level == 'services':
      self.createTopLevelOfChangeTaxonomy_ServicesOnly(command)
      systemInstanceName = config_cliprocessor.inputVars.get('systemName')
      systemConfig = cfp.getSystemConfig(platformConfig, systemInstanceName)
      serviceTypes = []
      for sType in systemConfig.get('serviceTypes'):
        serviceTypes.append(sType)
      systemDict = { }
      systemDict["name"] = systemInstanceName
      systemDict["status"] = "NOT Started"
      systemDict["currentStep"] = 0
      if "foundation" in systemConfig.keys():
        logString = "WARNING: The current code assumes that you have already created a networkFoundation.  Make sure that you already have created the networkFoundation in your workflow.  If you have not already created a networkFoundation, then your services operation will fail.  "
        lw.writeLogVerbose("acm", logString)
        systemDict["steps"] = len(serviceTypes) #numStepsEntireSystem does NOT add foundation step here because this operation is only on the services.
      else:
        systemDict["steps"] = len(serviceTypes) #numStepsEntireSystem does NOT add foundation
        logString = "WARNING: There is NOT any networkFoundation block"
        lw.writeLogVerbose("acm", logString)
      systemDict["services"] = self.createServicesSummaryDict(len(serviceTypes))
      for serviceType in serviceTypes:
        serviceInstanceNames = []
        for sTypeInstance in systemConfig.get('serviceTypes').get(serviceType).get('instances'):
          serviceInstanceNames.append(sTypeInstance.get('instanceName'))
        serviceDict = self.createServiceTypeSummaryDict(len(serviceInstanceNames), serviceType)
        serviceInstances = {}
        for serviceInstanceName in serviceInstanceNames:
          instanceDict = {"status":"NOT Started", "steps":1, "currentStep":0}
          serviceInstances[serviceInstanceName] = instanceDict
        serviceDict["instances"] = serviceInstances
        systemDict["services"]["serviceTypes"].append(serviceDict)
      self.changeTaxonomy["systemsToChange"].append(systemDict)
    elif level == 'servicetype':
      self.createTopLevelOfChangeTaxonomy_ServicesOnly(command)
      systemInstanceName = config_cliprocessor.inputVars.get('systemName')
      systemConfig = cfp.getSystemConfig(platformConfig, systemInstanceName)
      svcType = config_cliprocessor.inputVars.get('serviceType')
      serviceTypes = []
      for sType in systemConfig.get('serviceTypes'):
        if sType == svcType:
          serviceTypes.append(sType)
      systemDict = { }
      systemDict["name"] = systemInstanceName
      systemDict["status"] = "NOT Started"
      systemDict["currentStep"] = 0
      if "foundation" in systemConfig.keys():
        logString = "WARNING: The current code assumes that you have already created a networkFoundation.  Make sure that you already have created the networkFoundation in your workflow.  If you have not already created a networkFoundation, then your services operation will fail.  "
        lw.writeLogVerbose("acm", logString)
        systemDict["steps"] = len(serviceTypes) #numStepsEntireSystem does NOT add foundation step here because this operation is only on the services.
      else:
        systemDict["steps"] = len(serviceTypes) #numStepsEntireSystem does NOT add foundation
        logString = "WARNING: There is NOT any networkFoundation block"
        lw.writeLogVerbose("acm", logString)
      systemDict["services"] = self.createServicesSummaryDict(len(serviceTypes))
      for serviceType in serviceTypes:
        serviceInstanceNames = []
        for sTypeInstance in systemConfig.get('serviceTypes').get(serviceType).get('instances'):
          serviceInstanceNames.append(sTypeInstance.get('instanceName'))
        serviceDict = self.createServiceTypeSummaryDict(len(serviceInstanceNames), serviceType)
        serviceInstances = {}
        for serviceInstanceName in serviceInstanceNames:
          instanceDict = {"status":"NOT Started", "steps":1, "currentStep":0}
          serviceInstances[serviceInstanceName] = instanceDict
        serviceDict["instances"] = serviceInstances
        systemDict["services"]["serviceTypes"].append(serviceDict)
      self.changeTaxonomy["systemsToChange"].append(systemDict)
    elif level == 'serviceinstance':
      self.createTopLevelOfChangeTaxonomy_ServicesOnly(command)
      systemInstanceName = config_cliprocessor.inputVars.get('systemName')
      systemConfig = cfp.getSystemConfig(platformConfig, systemInstanceName)
      svcType = config_cliprocessor.inputVars.get('serviceType')
      svcInstance = config_cliprocessor.inputVars.get('serviceInstance')
      serviceTypes = []
      for sType in systemConfig.get('serviceTypes'):
        if sType == svcType:
          serviceTypes.append(sType)
      systemDict = { }
      systemDict["name"] = systemInstanceName
      systemDict["status"] = "NOT Started"
      systemDict["currentStep"] = 0
      if "foundation" in systemConfig.keys():
        logString = "WARNING: The current code assumes that you have already created a networkFoundation.  Make sure that you already have created the networkFoundation in your workflow.  If you have not already created a networkFoundation, then your services operation will fail.  "
        lw.writeLogVerbose("acm", logString)
        systemDict["steps"] = len(serviceTypes) #numStepsEntireSystem does NOT add foundation step here because this operation is only on the services.
      else:
        systemDict["steps"] = len(serviceTypes) #numStepsEntireSystem does NOT add foundation
        logString = "WARNING: There is NOT any networkFoundation block"
        lw.writeLogVerbose("acm", logString)
      systemDict["services"] = self.createServicesSummaryDict(len(serviceTypes))
      for serviceType in serviceTypes:
        serviceInstanceNames = []
        for sTypeInstance in systemConfig.get('serviceTypes').get(serviceType).get('instances'):
          if sTypeInstance.get('instanceName') == svcInstance:
            serviceInstanceNames.append(sTypeInstance.get('instanceName'))
        serviceDict = self.createServiceTypeSummaryDict(len(serviceInstanceNames), serviceType)
        serviceInstances = {}
        for serviceInstanceName in serviceInstanceNames:
          instanceDict = {"status":"NOT Started", "steps":1, "currentStep":0}
          serviceInstances[serviceInstanceName] = instanceDict
        serviceDict["instances"] = serviceInstances
        systemDict["services"]["serviceTypes"].append(serviceDict)
      self.changeTaxonomy["systemsToChange"].append(systemDict)

  #@public
  def storeChangeTaxonomy(self, cc, level, outputLine):
    import config_cliprocessor
    lw = log_writer()
    cf = command_formatter()
    self.changeCounter += 1
    changeDict = {"changeCounter": self.changeCounter , "line": outputLine}
    self.changeReports.append(changeDict)
    counterOutputLineMeta = "changeCounter is: " + str(self.changeCounter-1)
    outputLineMeta = outputLine.replace("[ acm ] ", "")
    lw.writeMetaLog("acm", counterOutputLineMeta)
    lw.writeMetaLog("acm", outputLineMeta)
    counterOutputLine = "[ acm ] changeCounter is: " + str(self.changeCounter-1)
    if self.changeCounter == 1:
      try:
        print(counterOutputLine)  
      except UnicodeEncodeError as e:
        print(counterOutputLine.encode('utf-8'))
        print("The preceding line is returned here as a byte array because it threw a UnicodeEncodeError which was handled by encoding its as utf-8, which returns a byte array.  ")
    elif self.changeCounter > 1:
      verboseLogFilePath = config_cliprocessor.inputVars.get('verboseLogFilePath')
      verboseLogFileAndPath = verboseLogFilePath + '/log-verbose.log'
      verboseLogFileAndPath = cf.formatPathForOS(verboseLogFileAndPath)
      with io.open(verboseLogFileAndPath, "a", encoding="utf-8") as f:  
        f.write(counterOutputLine + '\n')  
      try:
        print(counterOutputLine)  
      except UnicodeEncodeError as e:
        print(counterOutputLine.encode('utf-8'))
        print("The preceding line is returned here as a byte array because it threw a UnicodeEncodeError which was handled by encoding its as utf-8, which returns a byte array.  ")
      redundant = cc.runComparer(level, self.changeReports, False) 
      if not redundant:
        redundant = cc.runComparer(level, self.changeReports, True)  

  #@private
  def createServiceTypeSummaryDict(self, numServiceInstanceNames, systemType):
    serviceDict = {}
    serviceDict["status"] = "NOT Started"
    serviceDict["steps"] = numServiceInstanceNames
    serviceDict["currentStep"] = 0
    serviceDict["type"] = systemType
    return serviceDict

  #@private
  def createServicesSummaryDict(self, numServiceTypes):
    servicesSummaryDict = {}
    servicesSummaryDict["status"] = "NOT Started"
    servicesSummaryDict["steps"] = numServiceTypes
    servicesSummaryDict["currentStep"] = 0
    servicesSummaryDict["serviceTypes"] = []
    return servicesSummaryDict

  #@private
  def createTopLevelOfChangeTaxonomy(self, command, platformConfig):
    cfp = config_fileprocessor()
    self.changeTaxonomy["command"] = command
    self.changeTaxonomy["overallStatus"] = "NOT Started"
    #Calculate the number of steps for the entire platform, across all systems
    numStepsAllSystems = len(cfp.getSystemNames(platformConfig))
    self.changeTaxonomy["steps"] = numStepsAllSystems
    self.changeTaxonomy["currentStep"] = 0
    self.changeTaxonomy["systemsToChange"] = []

  #@private
  def createTopLevelOfChangeTaxonomy_FoundationOnly(self, command):
    self.changeTaxonomy["command"] = command
    self.changeTaxonomy["overallStatus"] = "NOT Started"
    #Calculate the number of steps for the entire platform, across all systems
    numStepsAllSystems = 1 #Because there is only one system being changed
    self.changeTaxonomy["steps"] = numStepsAllSystems
    self.changeTaxonomy["currentStep"] = 0
    self.changeTaxonomy["systemsToChange"] = []

  #@private
  def createTopLevelOfChangeTaxonomy_ServicesOnly(self, command):
    self.changeTaxonomy["command"] = command
    self.changeTaxonomy["overallStatus"] = "NOT Started"
    #Calculate the number of steps for the entire platform, across all systems
    numStepsAllSystems = 1 #Because there is only one system being changed
    self.changeTaxonomy["steps"] = numStepsAllSystems
    self.changeTaxonomy["currentStep"] = 0
    self.changeTaxonomy["systemsToChange"] = []

  #@private
  def createFoundationDict(self, foundationInstanceName):
    foundationDict = {}
    foundationDict["name"] = foundationInstanceName
    foundationDict["status"] = "NOT Started"
    foundationDict["steps"] = 1
    foundationDict["currentStep"] = 0
    return foundationDict

  #@private
  def createImagesSummary(self, numImageInstances):
    imagesDict = {}
    imagesDict["status"] = "NOT Started" 
    imagesDict["steps"] = numImageInstances
    imagesDict["currentStep"] = 0
    imagesDict["instances"] = {}
    return imagesDict

  #@private
  def createImageInstanceDict(self):
    imageInstanceDict = {}
    imageInstanceDict["status"] = "NOT Started"
    imageInstanceDict["steps"] = 1
    imageInstanceDict["currentStep"] = 0
    return imageInstanceDict

  #@public
  def updateStartOfPlatformRun(self, newStatus):
    ## Highest-level deployment summary.  Corresponds with acm.yaml
    self.changeTaxonomy["overallStatus"] = newStatus

  #@public
  def updateStartOfASystem(self, level, systemInstanceName, newStatus):
    for systemBeingChanged in self.changeTaxonomy["systemsToChange"]:
      if systemBeingChanged["name"] == systemInstanceName:
        systemBeingChanged["status"] = newStatus
        ## Highest-level deployment summary.  Corresponds with platformConfig.yaml
        overallCurrentStep = self.changeTaxonomy["currentStep"]
        if self.changeTaxonomy["overallStatus"] == "In Process":
          overallCurrentStep += 1
        self.changeTaxonomy["currentStep"] = overallCurrentStep

  #@public
  def updateStartOfAFoundation(self, systemInstanceName, newStatus):
    for systemBeingChanged in self.changeTaxonomy["systemsToChange"]:
      if systemBeingChanged["name"] == systemInstanceName:
        if newStatus == "In Process":
          currStepOverall = systemBeingChanged["currentStep"]
          currStepOverall += 1
          systemBeingChanged["currentStep"] = currStepOverall
        ## Foundation of one system summary.  Corresponds with the one foundation within a given systemConfig.yaml file
        currStepFoundation = systemBeingChanged["foundation"]["currentStep"]
        systemBeingChanged["foundation"]["status"] = newStatus
        if (systemBeingChanged["foundation"]["status"] == "In Process"):
          currStepFoundation += 1
        systemBeingChanged["foundation"]["currentStep"] = currStepFoundation

  #@public
  def updateEndOfAFoundation(self, systemInstanceName):
    for systemBeingChanged in self.changeTaxonomy["systemsToChange"]:
      if systemBeingChanged["name"] == systemInstanceName:
        ## Foundation of one system summary.  Corresponds with the one foundation within a given systemConfig.yaml file
        systemBeingChanged["foundation"]["status"] = "Completed"

  #@public
  def updateStartOfAServicesSection(self, systemInstanceName):
    print('self.changeTaxonomy["systemsToChange"] is: ', self.changeTaxonomy["systemsToChange"])
    for systemBeingChanged in self.changeTaxonomy["systemsToChange"]:
      if systemBeingChanged["name"] == systemInstanceName:
        systemBeingChanged["services"]["status"] = "In Process"
        currStepOverall = systemBeingChanged["currentStep"]
        currStepOverall += 1
        systemBeingChanged["currentStep"] = currStepOverall
        if len(systemBeingChanged["services"]["serviceTypes"]) == 0:
          systemBeingChanged["services"]["status"] = "Completed"

  #@public
  def updateStartOfAServiceType(self, systemInstanceName, typeName):
    for systemBeingChanged in self.changeTaxonomy["systemsToChange"]:
      if systemBeingChanged["name"] == systemInstanceName:
        if len(systemBeingChanged["services"]["serviceTypes"]) == 0:
          systemBeingChanged["services"]["status"] = "Completed"
        else: 
          for serviceType in systemBeingChanged["services"]["serviceTypes"]:
            if serviceType["type"] == typeName:
              serviceType["status"] = "In Process"
              #1 serviceTypes (all types) step +1
              currStepAllServices = systemBeingChanged["services"]["currentStep"]
              if (systemBeingChanged["services"]["status"] == "In Process") and (systemBeingChanged["services"]["currentStep"] < systemBeingChanged["services"]["steps"]):  
                currStepAllServices += 1
              systemBeingChanged["services"]["currentStep"] = currStepAllServices
              #2 serviceTypes/typeName status To In Process 
              for serviceType in systemBeingChanged["services"]["serviceTypes"]:
                if serviceType["type"] == typeName:
                  serviceType["status"] = "In Process"

  #@public
  def updateStartOfAnInstanceOfAServiceType(self, systemInstanceName, typeName, instanceName):
    for systemBeingChanged in self.changeTaxonomy["systemsToChange"]:
      if systemBeingChanged["name"] == systemInstanceName:
          for serviceType in systemBeingChanged["services"]["serviceTypes"]:
            if serviceType["type"] == typeName:
                #1 serviceType (singular type) Step +1
                #2 instance of serviceType status change AND step +1
                currStepServiceType = serviceType["currentStep"]
                currStepServiceType += 1
                serviceType["currentStep"] = currStepServiceType
                currStepSvc = serviceType["instances"][instanceName]["currentStep"]
                serviceType["instances"][instanceName]["status"] = "In Process"
                currStepSvc += 1
                serviceType["instances"][instanceName]["currentStep"] = currStepSvc

  #@public
  def updateEndOfAnInstanceOfAServiceType(self, systemInstanceName, typeName, instanceName):
    for systemBeingChanged in self.changeTaxonomy["systemsToChange"]:
      if systemBeingChanged["name"] == systemInstanceName:
        for serviceType in systemBeingChanged["services"]["serviceTypes"]:
          if serviceType["type"] == typeName:
                #1 instance of serviceType status change AND step +1
                serviceType["instances"][instanceName]["status"] = "Completed"

  #@public
  def updateEndOfAServiceType(self, systemInstanceName, typeName):
    for systemBeingChanged in self.changeTaxonomy["systemsToChange"]:
      if systemBeingChanged["name"] == systemInstanceName:
        for serviceType in systemBeingChanged["services"]["serviceTypes"]:
          if serviceType["type"] == typeName:
            serviceType["status"] = "Completed"

  #@public
  def updateEndOfAServicesSection(self, systemInstanceName):
    for systemBeingChanged in self.changeTaxonomy["systemsToChange"]:
      if systemBeingChanged["name"] == systemInstanceName:
        systemBeingChanged["services"]["status"] = "Completed"

  #@public
  def updateEndOfASystem(self, systemInstanceName):
    for systemBeingChanged in self.changeTaxonomy["systemsToChange"]:
      if systemBeingChanged["name"] == systemInstanceName:
        systemBeingChanged["status"] = "Completed"

  #@public
  def updateEndOfPlatformRun(self):
    self.changeTaxonomy["overallStatus"] = "Completed"

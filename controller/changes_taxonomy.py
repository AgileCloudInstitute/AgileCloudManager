## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import sys
import io
from pathlib import Path

import config_fileprocessor
import changes_comparer
import changes_manifest
import config_cliprocessor
import command_builder
import logWriter

changeTaxonomy = {}
changeReports = []
changeCounter = 0
   
def assembleChangeTaxonomy(level, command):
  global changeTaxonomy
  if level == 'platform':
    yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlPlatformConfigFileAndPath')
    systemInstanceNames = config_fileprocessor.getInstanceNames(yamlPlatformConfigFileAndPath, 'systems')
    createTopLevelOfChangeTaxonomy(command, yamlPlatformConfigFileAndPath)
    for instanceName in systemInstanceNames:
      yaml_infra_config_file_and_path = getInfraConfigFileAndPath(instanceName)
      serviceTypes = config_fileprocessor.listTypesInSystem(yaml_infra_config_file_and_path)
      systemDict = { }
      systemDict["name"] = instanceName
      systemDict["status"] = "NOT Started"
      systemDict["currentStep"] = 0
      if config_fileprocessor.checkTopLevelType(yaml_infra_config_file_and_path, "networkFoundation"):
        systemDict["steps"] = len(serviceTypes)+1 #numStepsEntireSystem ADDS foundation
        systemDict["foundation"] = createFoundationDict(yaml_infra_config_file_and_path)
        imageInstanceNames = config_fileprocessor.getImageInstanceNames(yaml_infra_config_file_and_path, "images")
        if len(imageInstanceNames) > 0:
          systemDict["images"] = createImagesSummary(len(imageInstanceNames))
          for imageInstanceName in imageInstanceNames:
            systemDict["images"]["instances"][imageInstanceName] = createImageInstanceDict()
      else:
        systemDict["steps"] = len(serviceTypes) #numStepsEntireSystem does NOT add foundation
        logString = "WARNING: There is NOT any networkFoundation block"
        logWriter.writeLogVerbose("acm", logString)
      systemDict["services"] = createServicesSummaryDict(len(serviceTypes))
      for serviceType in serviceTypes:
        serviceInstanceNames = config_fileprocessor.getSystemInstanceNames(yaml_infra_config_file_and_path, serviceType)
        serviceDict = createServiceTypeSummaryDict(len(serviceInstanceNames), serviceType)
        serviceInstances = {}
        for serviceInstanceName in serviceInstanceNames:
          instanceDict = {"status":"NOT Started", "steps":1, "currentStep":0}
          serviceInstances[serviceInstanceName] = instanceDict
        serviceDict["instances"] = serviceInstances
        systemDict["services"]["serviceTypes"].append(serviceDict)
      changeTaxonomy["systemsToChange"].append(systemDict)
  elif level == 'foundation':
    createTopLevelOfChangeTaxonomy_FoundationOnly(command)
    yaml_infra_config_file_and_path = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    systemInstanceName = config_fileprocessor.getFirstLevelValue(yaml_infra_config_file_and_path, "name")
    systemDict = { }
    systemDict["name"] = systemInstanceName
    systemDict["status"] = "NOT Started"
    systemDict["currentStep"] = 0
    if config_fileprocessor.checkTopLevelType(yaml_infra_config_file_and_path, "networkFoundation"):
      systemDict["steps"] = 1 #foundation is only one step
      systemDict["foundation"] = createFoundationDict(yaml_infra_config_file_and_path)
      imageInstanceNames = config_fileprocessor.getImageInstanceNames(yaml_infra_config_file_and_path, "images")
      if len(imageInstanceNames) > 0:
        systemDict["images"] = createImagesSummary(len(imageInstanceNames))
        for imageInstanceName in imageInstanceNames:
          systemDict["images"]["instances"][imageInstanceName] = createImageInstanceDict()
      changeTaxonomy["systemsToChange"].append(systemDict)
    else:
      logString = 'ERROR: There is no foundation specified in your systemConfig.yaml file, but you are running a foundation cli command.'
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
  elif level == 'services':
    yaml_infra_config_file_and_path = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    createTopLevelOfChangeTaxonomy_ServicesOnly(command, yaml_infra_config_file_and_path)
    systemInstanceName = config_fileprocessor.getFirstLevelValue(yaml_infra_config_file_and_path, "name")
    yaml_infra_config_file_and_path = getInfraConfigFileAndPath(systemInstanceName)
    file_path = Path('yaml_infra_config_file_and_path ')
    if not file_path.is_dir():
      yaml_infra_config_file_and_path = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    print('yaml_infra_config_file_and_path is: ', yaml_infra_config_file_and_path)
    serviceTypes = config_fileprocessor.listTypesInSystem(yaml_infra_config_file_and_path)
    systemDict = { }
    systemDict["name"] = systemInstanceName
    systemDict["status"] = "NOT Started"
    systemDict["currentStep"] = 0
    if config_fileprocessor.checkTopLevelType(yaml_infra_config_file_and_path, "networkFoundation"):
      logString = "WARNING: The current code assumes that you have already created a networkFoundation.  Make sure that you already have created the networkFoundation in your workflow.  If you have not already created a networkFoundation, then your services operation will fail.  "
      logWriter.writeLogVerbose("acm", logString)
      systemDict["steps"] = len(serviceTypes) #numStepsEntireSystem does NOT add foundation step here because this operation is only on the services.
    else:
      systemDict["steps"] = len(serviceTypes) #numStepsEntireSystem does NOT add foundation
      logString = "WARNING: There is NOT any networkFoundation block"
      logWriter.writeLogVerbose("acm", logString)
    systemDict["services"] = createServicesSummaryDict(len(serviceTypes))
    for serviceType in serviceTypes:
      serviceInstanceNames = config_fileprocessor.getSystemInstanceNames(yaml_infra_config_file_and_path, serviceType)
      serviceDict = createServiceTypeSummaryDict(len(serviceInstanceNames), serviceType)
      serviceInstances = {}
      for serviceInstanceName in serviceInstanceNames:
        instanceDict = {"status":"NOT Started", "steps":1, "currentStep":0}
        serviceInstances[serviceInstanceName] = instanceDict
      serviceDict["instances"] = serviceInstances
      systemDict["services"]["serviceTypes"].append(serviceDict)
    changeTaxonomy["systemsToChange"].append(systemDict)

def storeChangeTaxonomy(level, outputLine):
  global changeCounter
  global changeReports
  changeCounter += 1
  changeDict = {"changeCounter": changeCounter , "line": outputLine}
  changeReports.append(changeDict)
  counterOutputLineMeta = "changeCounter is: " + str(changeCounter-1)
  outputLineMeta = outputLine.replace("[ acm ] ", "")
  logWriter.writeMetaLog("acm", counterOutputLineMeta)
  logWriter.writeMetaLog("acm", outputLineMeta)
  counterOutputLine = "[ acm ] changeCounter is: " + str(changeCounter-1)
#  print("changesList is: ", changesList)
  print("len(changeReports)", len(changeReports))
  if changeCounter == 1:
    try:
      print(counterOutputLine)  
    except UnicodeEncodeError as e:
      print(counterOutputLine.encode('utf-8'))
      print("The preceding line is returned here as a byte array because it threw a UnicodeEncodeError which was handled by encoding its as utf-8, which returns a byte array.  ")
  elif changeCounter > 1:
    verboseLogFilePath = config_cliprocessor.inputVars.get('verboseLogFilePath')
    verboseLogFileAndPath = verboseLogFilePath + '/log-verbose.log'
    verboseLogFileAndPath = command_builder.formatPathForOS(verboseLogFileAndPath)
    with io.open(verboseLogFileAndPath, "a", encoding="utf-8") as f:  
      f.write(counterOutputLine + '\n')  
    try:
      print(counterOutputLine)  
    except UnicodeEncodeError as e:
      print(counterOutputLine.encode('utf-8'))
      print("The preceding line is returned here as a byte array because it threw a UnicodeEncodeError which was handled by encoding its as utf-8, which returns a byte array.  ")
    redundant = changes_comparer.runComparer(level, changeReports, False) 
    print("redundant before logging is: ", redundant)
    if not redundant:
      redundant = changes_comparer.runComparer(level, changeReports, True)  
    print("redundant after logging is: ", redundant)

##Start of create components of changeTaxonomy
def getInfraConfigFileAndPath(instanceName):
  yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlPlatformConfigFileAndPath')
  infraConfigFile = config_fileprocessor.getPropertyFromFirstLevelList(yamlPlatformConfigFileAndPath, 'systems', instanceName, 'infraConfigFile')
  if infraConfigFile == "default":
    yaml_infra_config_file_and_path = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
  else:
    yaml_infra_config_file_and_path = config_cliprocessor.inputVars.get('userCallingDir') + infraConfigFile
  return yaml_infra_config_file_and_path

def createServiceTypeSummaryDict(numServiceInstanceNames, systemType):
  serviceDict = {}
  serviceDict["status"] = "NOT Started"
  serviceDict["steps"] = numServiceInstanceNames
  serviceDict["currentStep"] = 0
  serviceDict["type"] = systemType
  return serviceDict

def createServicesSummaryDict(numServiceTypes):
  servicesSummaryDict = {}
  servicesSummaryDict["status"] = "NOT Started"
  servicesSummaryDict["steps"] = numServiceTypes
  servicesSummaryDict["currentStep"] = 0
  servicesSummaryDict["serviceTypes"] = []
  return servicesSummaryDict

def createTopLevelOfChangeTaxonomy(command, yamlPlatformConfigFileAndPath):
  global changeTaxonomy
  changeTaxonomy["command"] = command
  changeTaxonomy["overallStatus"] = "NOT Started"
  #Calculate the number of steps for the entire platform, across all systems
  numStepsAllSystems = len(config_fileprocessor.getInstanceNames(yamlPlatformConfigFileAndPath, 'systems'))
  changeTaxonomy["steps"] = numStepsAllSystems
  changeTaxonomy["currentStep"] = 0
  changeTaxonomy["systemsToChange"] = []

def createTopLevelOfChangeTaxonomy_FoundationOnly(command):
  global changeTaxonomy
  changeTaxonomy["command"] = command
  changeTaxonomy["overallStatus"] = "NOT Started"
  #Calculate the number of steps for the entire platform, across all systems
  numStepsAllSystems = 1 #Because there is only one system being changed
  changeTaxonomy["steps"] = numStepsAllSystems
  changeTaxonomy["currentStep"] = 0
  changeTaxonomy["systemsToChange"] = []

def createTopLevelOfChangeTaxonomy_ServicesOnly(command, yamlPlatformConfigFileAndPath):
  global changeTaxonomy
  changeTaxonomy["command"] = command
  changeTaxonomy["overallStatus"] = "NOT Started"
  #Calculate the number of steps for the entire platform, across all systems
  numStepsAllSystems = 1 #Because there is only one system being changed
  changeTaxonomy["steps"] = numStepsAllSystems
  changeTaxonomy["currentStep"] = 0
  changeTaxonomy["systemsToChange"] = []

def createFoundationDict(yaml_infra_config_file_and_path):
  foundationInstanceName = config_fileprocessor.getFoundationInstanceName(yaml_infra_config_file_and_path)
  foundationDict = {}
  foundationDict["name"] = foundationInstanceName
  foundationDict["status"] = "NOT Started"
  foundationDict["steps"] = 1
  foundationDict["currentStep"] = 0
  return foundationDict

def createImagesSummary(numImageInstances):
  imagesDict = {}
  imagesDict["status"] = "NOT Started" 
  imagesDict["steps"] = numImageInstances
  imagesDict["currentStep"] = 0
  imagesDict["instances"] = {}
  return imagesDict

def createImageInstanceDict():
  imageInstanceDict = {}
  imageInstanceDict["status"] = "NOT Started"
  imageInstanceDict["steps"] = 1
  imageInstanceDict["currentStep"] = 0
  return imageInstanceDict
##End of create components of changeTaxonomy

def printTheTaxonomy():
  #print out the current state of the taxonomy, including each step's status.
  #Call this just at the start of a run, then again at the end of a run, and also at any point where the run is broken and the program stops.
  return changeTaxonomy

#def updateTheTaxonomy(systemInstanceName, typeParent, typeName, instanceName, newStatus):
#  global changeTaxonomy
#  checkStatusValidity(newStatus)
#  if systemInstanceName == "all":
#    changeTaxonomy = overall_UpdateStatus_All(changeTaxonomy, newStatus)
#  for systemBeingChanged in changeTaxonomy["systemsToChange"]:
#    if systemBeingChanged["name"] == systemInstanceName:
#      if (typeParent == None) or (typeParent == "none"):
#        if typeName == "networkFoundation":
#          if newStatus == "In Process":
#            systemBeingChanged = systemBeingChanged_UpdateStep(systemBeingChanged, "foundation")
#          systemBeingChanged = systemBeingChanged_UpdateFoundationStatusAndSteps(systemBeingChanged, newStatus)
#        if typeName == "imageBuilds":
#          systemBeingChanged["images"] = images_UpdateStepAndStatus(systemBeingChanged["images"], instanceName, newStatus)
#        if typeName == None:
#          systemBeingChanged = systemBeingChanged_UpdateStatus(systemBeingChanged, newStatus)
#          changeTaxonomy = overall_UpdateStep_All(changeTaxonomy)
#      if typeParent == "systems":
#        if (typeName == "services") and (instanceName == None):
#          systemBeingChanged = systemBeingChanged_AllServices_UpdateStatus(systemBeingChanged, newStatus)
#          systemBeingChanged = systemBeingChanged_UpdateStep(systemBeingChanged, "services")
#        if len(systemBeingChanged["services"]["serviceTypes"]) == 0:
#          systemBeingChanged["services"]["status"] = "Completed"
#        else: 
#          for serviceType in systemBeingChanged["services"]["serviceTypes"]:
#            if serviceType["type"] == typeName:
#              if instanceName == None:
#                serviceType["status"] = newStatus
#                #1 serviceTypes (all types) step +1
#                systemBeingChanged = systemBeingChanged_AllServices_UpdateStep(systemBeingChanged)
#                #2 serviceTypes/typeName status To In Process 
#                serviceType = serviceType_UpdateStatus(systemBeingChanged, typeName, newStatus)
#              else:
#                if newStatus == "In Process":
#                  #1 serviceType (singular type) Step +1
#                  #2 instance of serviceType status change AND step +1
#                  systemBeingChanged = serviceType_UpdateStep(systemBeingChanged, typeName, instanceName, newStatus) #NOTE This changes the serviceType and not the instances.  But we are using instanceName used as a filter to ensure this only runs the appropriate number of times.
#                  serviceType["instances"][instanceName] = serviceInstanceUpdate(serviceType["instances"][instanceName], systemInstanceName, typeName, instanceName, newStatus, "stepAndStatus", "Start of an instance of a serviceType")
#                if newStatus == "Completed":
#                  #1 instance of serviceType status change AND step +1
#                  serviceType["instances"][instanceName] = serviceInstanceUpdate(serviceType["instances"][instanceName], systemInstanceName, typeName, instanceName, newStatus, "justStatus", "End of an instance of a serviceType")
#  logString = " After update, changeTaxonomy is: " + str(changeTaxonomy)
#  logWriter.writeLogVerbose("acm", logString)

##1.7 Start of new functions to replace updateTheTaxonomy()
def updateStartOfPlatformRun(newStatus):
  global changeTaxonomy
  ## Highest-level deployment summary.  Corresponds with platformConfig.yaml
  changeTaxonomy["overallStatus"] = newStatus

def updateStartOfASystem(level, systemInstanceName, newStatus):
  global changeTaxonomy
  for systemBeingChanged in changeTaxonomy["systemsToChange"]:
    if systemBeingChanged["name"] == systemInstanceName:
      systemBeingChanged["status"] = newStatus
      ## Highest-level deployment summary.  Corresponds with platformConfig.yaml
      overallCurrentStep = changeTaxonomy["currentStep"]
      if changeTaxonomy["overallStatus"] == "In Process":
        overallCurrentStep += 1
      changeTaxonomy["currentStep"] = overallCurrentStep

def updateStartOfAFoundation(systemInstanceName, newStatus):
  global changeTaxonomy
  for systemBeingChanged in changeTaxonomy["systemsToChange"]:
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

def updateEndOfAFoundation(systemInstanceName):
  global changeTaxonomy
  for systemBeingChanged in changeTaxonomy["systemsToChange"]:
    if systemBeingChanged["name"] == systemInstanceName:
      ## Foundation of one system summary.  Corresponds with the one foundation within a given systemConfig.yaml file
      systemBeingChanged["foundation"]["status"] = "Completed"

def updateStartOfAServicesSection(level, systemInstanceName):
  global changeTaxonomy
  for systemBeingChanged in changeTaxonomy["systemsToChange"]:
    if systemBeingChanged["name"] == systemInstanceName:
      systemBeingChanged["services"]["status"] = "In Process"
      currStepOverall = systemBeingChanged["currentStep"]
      currStepOverall += 1
      systemBeingChanged["currentStep"] = currStepOverall
      if len(systemBeingChanged["services"]["serviceTypes"]) == 0:
        systemBeingChanged["services"]["status"] = "Completed"

def updateStartOfAServiceType(systemInstanceName, typeName):
  global changeTaxonomy
  for systemBeingChanged in changeTaxonomy["systemsToChange"]:
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

def updateStartOfAnInstanceOfAServiceType(systemInstanceName, typeName, instanceName):
  global changeTaxonomy
  for systemBeingChanged in changeTaxonomy["systemsToChange"]:
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

def updateEndOfAnInstanceOfAServiceType(systemInstanceName, typeName, instanceName):
  global changeTaxonomy
  for systemBeingChanged in changeTaxonomy["systemsToChange"]:
    if systemBeingChanged["name"] == systemInstanceName:
      for serviceType in systemBeingChanged["services"]["serviceTypes"]:
        if serviceType["type"] == typeName:
              #1 instance of serviceType status change AND step +1
              serviceType["instances"][instanceName]["status"] = "Completed"

def updateEndOfAServiceType(systemInstanceName, typeName):
  global changeTaxonomy
  for systemBeingChanged in changeTaxonomy["systemsToChange"]:
    if systemBeingChanged["name"] == systemInstanceName:
      for serviceType in systemBeingChanged["services"]["serviceTypes"]:
        if serviceType["type"] == typeName:
          serviceType["status"] = "Completed"

def updateEndOfAServicesSection(systemInstanceName):
  global changeTaxonomy
  for systemBeingChanged in changeTaxonomy["systemsToChange"]:
    if systemBeingChanged["name"] == systemInstanceName:
      systemBeingChanged["services"]["status"] = "Completed"

def updateEndOfASystem(systemInstanceName):
  global changeTaxonomy
  for systemBeingChanged in changeTaxonomy["systemsToChange"]:
    if systemBeingChanged["name"] == systemInstanceName:
      systemBeingChanged["status"] = "Completed"

def updateEndOfPlatformRun():
  global changeTaxonomy
  changeTaxonomy["overallStatus"] = "Completed"


##1.7 End of new functions to replace updateTheTaxonomy()

#############################################

def checkStatusValidity(newStatus):  
  if (newStatus != "Not Started") and (newStatus != "In Process") and (newStatus != "Completed"):
    logString = "ERROR: value for newStatus is NOT valid: " + newStatus
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)


# Type methods
#
def serviceInstanceUpdate(serviceInstance, systemInstanceName, typeName, instanceName, newStatus, whatChange, callSource):
  currStepSvc = serviceInstance["currentStep"]
  serviceInstance["status"] = newStatus
  if serviceInstance["status"] == "In Process":
    currStepSvc += 1
  serviceInstance["currentStep"] = currStepSvc
  for changesBlock in changes_manifest.changesManifest:
    if callSource in changesBlock["changeType"]:
      for changeKey in changesBlock:
        if changeKey == "changes":
          for change in changesBlock[changeKey]:
            affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes/" + typeName + "/" + instanceName
            if whatChange == "stepAndStatus":
              if (change["affectedUnit"] == affUnitName) and (change["Step"] == "+1") and (change["Status"].replace('To ','') == newStatus):
                change["changeCompleted"] = True
            elif whatChange == "justStatus":
              if (change["affectedUnit"] == affUnitName) and (change["Step"] == "same") and (change["Status"].replace('To ','') == newStatus):
                change["changeCompleted"] = True
            elif whatChange == "justStep":
              if (change["affectedUnit"] == affUnitName) and (change["Step"] == "+1") and (change["Status"] == "same"):
                change["changeCompleted"] = True
  #NOTE: Each of the alternative non-valid scenarios need to be handled with extra error handling added...
#..
  return serviceInstance


def systemBeingChanged_UpdateStepFromServices(systemBeingChanged):
  currStepAllServices = systemBeingChanged["services"]["currentStep"]
  if systemBeingChanged["services"]["status"] == "In Process":
    currStepAllServices += 1
  systemBeingChanged["services"]["currentStep"] = currStepAllServices
  if systemBeingChanged["services"]["currentStep"] == systemBeingChanged["services"]["steps"]:
    systemBeingChanged["services"]["status"] = "Completed"
    currStepOverall = systemBeingChanged["currentStep"]
    if (systemBeingChanged["status"] == "In Process") and (systemBeingChanged["currentStep"] < systemBeingChanged["steps"]):
      currStepOverall += 1
    systemBeingChanged["currentStep"] = currStepOverall
  return systemBeingChanged
  
def systemBeingChanged_UpdateStep(systemBeingChanged, callSource):
  currStepOverall = systemBeingChanged["currentStep"]
  currStepOverall += 1
  systemBeingChanged["currentStep"] = currStepOverall
  for changesBlock in changes_manifest.changesManifest:
    if callSource in changesBlock["changeType"]:
      for changeKey in changesBlock:
        if changeKey == "changes":
          for change in changesBlock[changeKey]:
            affUnitName = "platform/system:" + systemBeingChanged["name"]
            if change["affectedUnit"] == affUnitName:
              if change["Step"] == "+1":
                change["changeCompleted"] = True
  return systemBeingChanged

#..
def systemBeingChanged_UpdateStatus(systemBeingChanged, newStatus):
  systemBeingChanged["status"] = newStatus
  for changesBlock in changes_manifest.changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          affUnitName = "platform/system:" + systemBeingChanged["name"]
          if change["affectedUnit"] == affUnitName:
            if change["Status"].replace('To ','') == newStatus:
              change["changeCompleted"] = True
  return systemBeingChanged
#..

#..
def systemBeingChanged_AllServices_UpdateStatus(systemBeingChanged, newStatus):
  systemBeingChanged["services"]["status"] = newStatus
  for changesBlock in changes_manifest.changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          affUnitName = "platform/system:" + systemBeingChanged["name"] + "/serviceTypes"
          if change["affectedUnit"] == affUnitName:
            if change["Status"].replace('To ','') == newStatus:
              change["changeCompleted"] = True
  return systemBeingChanged
#..

#..
def serviceType_UpdateStatus(systemBeingChanged, typeName, newStatus):
  for serviceType in systemBeingChanged["services"]["serviceTypes"]:
    if serviceType["type"] == typeName:
      serviceType["status"] = newStatus
  for changesBlock in changes_manifest.changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          affUnitName = "platform/system:" + systemBeingChanged["name"] + "/serviceTypes/" + typeName
          if change["affectedUnit"] == affUnitName:
            if change["Status"].replace('To ','') == newStatus:
              change["changeCompleted"] = True
  return systemBeingChanged
#..

#..
def serviceType_UpdateStep(systemBeingChanged, typeName, instanceName, newStatus): #NOTE: newStatus used here only to find the correct changeIndex in order to ensure that this only runs the intended number of times.  status will not be changed by this function.
  for serviceType in systemBeingChanged["services"]["serviceTypes"]:
    if serviceType["type"] == typeName:
      currStepServiceType = serviceType["currentStep"]
      currStepServiceType += 1
      serviceType["currentStep"] = currStepServiceType
  #First get changeIndex in order to make sure this only runs the intended number of times.
  chgIdx = "-1"
  for changesBlock in changes_manifest.changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          affUnitName = "platform/system:" + systemBeingChanged["name"] + "/serviceTypes/" + typeName + "/" + instanceName
          if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == newStatus):
            chgIdx = changesBlock["changeIndex"]
  for changesBlock in changes_manifest.changesManifest:
    if changesBlock["changeIndex"] == chgIdx:
      for changeKey in changesBlock:
        if changeKey == "changes":
          for change in changesBlock[changeKey]:
            affUnitName = "platform/system:" + systemBeingChanged["name"] + "/serviceTypes/" + typeName
            if change["affectedUnit"] == affUnitName:
              if change["Step"] == "+1":
                change["changeCompleted"] = True
  return systemBeingChanged
#..

#..
def systemBeingChanged_AllServices_UpdateStep(systemBeingChanged):
  currStepAllServices = systemBeingChanged["services"]["currentStep"]
  if (systemBeingChanged["services"]["status"] == "In Process") and (systemBeingChanged["services"]["currentStep"] < systemBeingChanged["services"]["steps"]):  
    currStepAllServices += 1
  systemBeingChanged["services"]["currentStep"] = currStepAllServices
  for changesBlock in changes_manifest.changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          affUnitName = "platform/system:" + systemBeingChanged["name"] + "/serviceTypes"
          if change["affectedUnit"] == affUnitName:
            if change["Step"] == "+1":
              change["changeCompleted"] = True
  return systemBeingChanged
#..

def overall_UpdateStatus_All(changeTaxonomy, newStatus):
  ## Highest-level deployment summary.  Corresponds with platformConfig.yaml
  changeTaxonomy["overallStatus"] = newStatus
  for changesBlock in changes_manifest.changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          if change["affectedUnit"] == "platform":
            if change["Status"].replace('To ','') == newStatus:
              change["changeCompleted"] = True
  return changeTaxonomy

#..
def overall_UpdateStep_All(changeTaxonomy):
  ## Highest-level deployment summary.  Corresponds with platformConfig.yaml
  overallCurrentStep = changeTaxonomy["currentStep"]
  if changeTaxonomy["overallStatus"] == "In Process":
    overallCurrentStep += 1
  changeTaxonomy["currentStep"] = overallCurrentStep
  for changesBlock in changes_manifest.changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          if change["affectedUnit"] == "platform":
            if (change["Step"] == "+1") and (change["Status"] == "same"):
              if change["changeCompleted"] == False:
                change["changeCompleted"] = True
                return changeTaxonomy
  return changeTaxonomy
#..

def images_UpdateStepAndStatus(images, instanceName, newStatus):
  currStepImages = images["currentStep"]
  if instanceName == None:
    images["status"] = newStatus
  if (images["status"] == "In Process") and (instanceName == None):
    currStepImages += 1
  images["currentStep"] = currStepImages
  if (images["status"] == "In Process") and (instanceName != None):
    imageInstanceCounter = 0
    for imageInstance in images["instances"]:
      if imageInstance == instanceName:
        images["instances"][imageInstance]["status"] = newStatus
        if newStatus == "In Process":
          images["instances"][imageInstance]["currentStep"] = 1
      if images["instances"][imageInstance]["status"] == "Completed":
        imageInstanceCounter += 1
    if imageInstanceCounter == len(images["instances"]):
      images["status"] = "Completed"
  return images


def systemBeingChanged_UpdateFoundationAndSystemStatusAndSteps(systemBeingChanged, command, newStatus, instanceName):
  ## Foundation of one system summary.  Corresponds with the one foundation within a given systemConfig.yaml file
  currStepFoundation = systemBeingChanged["foundation"]["currentStep"]
  systemBeingChanged["foundation"]["status"] = newStatus
  if (systemBeingChanged["foundation"]["status"] == "In Process") and (instanceName != None):
    currStepFoundation += 1
  if systemBeingChanged["foundation"]["status"] == "Completed":
    if "images" in systemBeingChanged.keys():
      if command == "off":
        systemBeingChanged["images"]["status"] = "Ignored because images should have been deleted with your foundation, if your configuration is correct.  "
    currStepOverall = systemBeingChanged["currentStep"]
    if (systemBeingChanged["status"] == "In Process") and (currStepOverall < systemBeingChanged["steps"]):
      currStepOverall += 1
    if (currStepOverall <= systemBeingChanged["steps"]):
      systemBeingChanged["currentStep"] = currStepOverall
  systemBeingChanged["foundation"]["currentStep"] = currStepFoundation
  return systemBeingChanged

def systemBeingChanged_UpdateFoundationStatusAndSteps(systemBeingChanged, newStatus):
  ## Foundation of one system summary.  Corresponds with the one foundation within a given systemConfig.yaml file
  currStepFoundation = systemBeingChanged["foundation"]["currentStep"]
  systemBeingChanged["foundation"]["status"] = newStatus
  if (systemBeingChanged["foundation"]["status"] == "In Process"):
    currStepFoundation += 1
  systemBeingChanged["foundation"]["currentStep"] = currStepFoundation
  for changesBlock in changes_manifest.changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          if change["affectedUnit"] == "platform/system:"+systemBeingChanged["name"]+"/foundation":
            if (change["Step"] == "+1") and ("To In Process" in change["Status"]):
              change["changeCompleted"] = True
            if "To Completed" in change["Status"]:
              change["changeCompleted"] = True
  return systemBeingChanged

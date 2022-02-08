## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    
#"End-to-end tests will go in this file.  "
import subprocess
import re
import ast
import sys

import logWriter

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

changesList = []
writeLogBoolean = False

def runComparer(level, changeReports, writeToLog):
  global changesList
  changesList.clear()
  global writeLogBoolean
  writeLogBoolean = writeToLog
  changeDictReverseCounter = 0
  numChangeDicts = len(changeReports)
  if numChangeDicts == 0:
    logString = "ERROR: Invalid number of dicts in changeReports."
    if writeLogBoolean:
      logWriter.writeMetaLog("acm", logString)
  elif numChangeDicts == 1:
    logString = "Found the first changeDict.  Skipping for now."
    if writeLogBoolean:
      logWriter.writeMetaLog("acm", logString)
  else:
    overallChecker(changeReports)
  systemsToChangeList = []
  numSystemsToChange = 0
  logString = "    SYSTEMS:  Each system in the platform will be summarized one at a time as follows:  "
  if writeLogBoolean:
    logWriter.writeMetaLog("acm", logString)
  for changeDict in reversed(changeReports):
    if changeDictReverseCounter < 2:
      lineDict = getLineDict(changeDict)
      systemsToChangeCounter = 0
      systemsToChange = lineDict['systemsToChange']
      numSystemsToChange = len(systemsToChange)
      for systemToChange in systemsToChange:
        systemToChangeSummary = {"changeDictReverseCounter":changeDictReverseCounter, "systemsToChangeCounter":systemsToChangeCounter, "systemToChange":systemToChange}
        systemsToChangeList.append(systemToChangeSummary)
        systemsToChangeCounter += 1
      changeDictReverseCounter += 1
  systemsToChangeChecker(level, systemsToChangeList, numSystemsToChange)
  logString = "CHANGE SUMMARY: "
  if writeLogBoolean:
    logWriter.writeMetaLog("acm", logString)
  if len(changesList) > 0:
    for change in changesList:
      for chg in change['changes']:
        logString = "... " + str(chg)
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
    return False
  else:
    logString = "... THERE WERE NO CHANGES. "
    if writeLogBoolean:
      logWriter.writeMetaLog("acm", logString)
    return True

def overallChecker(changeReports):
  global writeLogBoolean
  reverseCounter = 0
  command = ''
  overallStatusLast = ''
  overallStatusSecondToLast = ''
  currentStepLast = ''
  currentStepSecondToLast = ''
  stepsLast = ''
  stepsSecondToLast = ''
  for changeDict in reversed(changeReports):
    if reverseCounter < 2:
      lineDict = getLineDict(changeDict)
      command = lineDict['command']
      if reverseCounter == 0:
        overallStatusLast = lineDict['overallStatus']
        currentStepLast = lineDict['currentStep']
        stepsLast = lineDict['steps']
      if reverseCounter == 1:
        overallStatusSecondToLast = lineDict['overallStatus']
        currentStepSecondToLast = lineDict['currentStep']
        stepsSecondToLast = lineDict['steps']
      reverseCounter += 1
  logString = "PLATFORM LEVEL: "
  if writeLogBoolean:
    logWriter.writeMetaLog("acm", logString)
  logString = "    command is: " + command
  if writeLogBoolean:
    logWriter.writeMetaLog("acm", logString)
  if stepsLast == stepsSecondToLast:
    if overallStatusLast != overallStatusSecondToLast:
      logString = "    overallStatus changed from " + overallStatusSecondToLast + " to " + overallStatusLast
      if (overallStatusSecondToLast == "NOT Started") and (overallStatusLast == "In Process"):
        changeDict = { "key":"platformStart", "changes":[logString] }
      elif (overallStatusSecondToLast == "In Process") and (overallStatusLast == "Completed"):
        changeDict = { "key":"platformEnd", "changes":[logString] }
      else:
        logString = "ERROR: Failed to populate key in platformStart or in platformEnd. "
        logWriter.writeMetaLog("acm", logString)
        sys.exit(1)
      changesList.append(changeDict)
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
    elif overallStatusLast == overallStatusSecondToLast:
      logString = "    overallStatus did NOT change since the last step and is: " + overallStatusLast
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
    if currentStepLast != currentStepSecondToLast:
      logString = "    currentStep changed from " + str(currentStepSecondToLast) + " to " + str(currentStepLast) + " out of " + str(stepsLast) + " steps. "
      changeDict = { "key":"platformStart", "changes":[logString] }
      changesList.append(changeDict)
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
    elif currentStepLast == currentStepSecondToLast:
      logString = "    currentStep did NOT change since the last step and is: " + str(currentStepLast) + " out of " + str(stepsLast) + " steps. "
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
  else:
    logString = "ERROR: the total number of steps changed between changeDict instances.  This is NOT valid.  Skipping so you can review your configuration to identify and fix whatever caused this problem."
    changeDict = { "key":"platformStart", "changes":[logString] }
    changesList.append(changeDict)
    if writeLogBoolean:
      logWriter.writeMetaLog("acm", logString)

def foundationChecker(systemInstanceName, foundationLast, foundationSecondToLast):
  global writeLogBoolean
  if foundationLast['steps'] != foundationSecondToLast['steps']:
    logString = "ERROR: The number of steps is different between two foundations which should have identical numbers of steps. "
    if writeLogBoolean:
      logWriter.writeMetaLog("acm", logString)
      exit(1)
  else:
    if foundationLast['name'] == foundationSecondToLast['name']:
      changeKey = "platform/system:"+systemInstanceName+"/foundation"
      logString = "            FOUNDATION LEVEL: "
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
      logString = "                name: " + foundationLast['name']
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
      if foundationLast['status'] == foundationSecondToLast['status']:
        logString = "                foundation status did NOT change and is: " + foundationLast['status']
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
      elif foundationLast['status'] != foundationSecondToLast['status']:
        if foundationSecondToLast['status'] == "Completed":
          logString = "                ERROR: foundation status changed from " + foundationSecondToLast['status'] + " to " + foundationLast['status'] + ". Halting program so you can debug. "
          changeDict = { "key":changeKey, "changes":[logString] }
          changesList.append(changeDict)
          if writeLogBoolean:
            logWriter.writeMetaLog("acm", logString)
            exit(1)
        else:
          logString = "                foundation status changed from " + foundationSecondToLast['status'] + " to " + foundationLast['status']
          changeDict = { "key":changeKey, "changes":[logString] }
          changesList.append(changeDict)
          if writeLogBoolean:
            logWriter.writeMetaLog("acm", logString)
      if foundationLast['currentStep'] == foundationSecondToLast['currentStep']:
        logString = "                foundation currentStep did NOT change and is: " + str(foundationLast['currentStep']) + " out of " + str(foundationLast['steps']) + " steps. "
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
      elif foundationLast['currentStep'] != foundationSecondToLast['currentStep']:
        logString = "                foundation currentStep changed from " + str(foundationSecondToLast['currentStep']) + " to " + str(foundationLast['currentStep']) + " out of " + str(foundationLast['steps']) + " steps. "
        changeDict = { "key":changeKey, "changes":[logString] }
        changesList.append(changeDict)
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)

def systemsToChangeChecker(level, systemsToChangeList, numSystemsToChange):
  global writeLogBoolean
  for i in range(0, numSystemsToChange):
    instancesOfSystem = []
    #strip list to only those matching i
    for sysChange in systemsToChangeList:
      if sysChange['systemsToChangeCounter'] == i:
        sysInstance = sysChange
        instancesOfSystem.append(sysInstance)
    foundationLast = {}
    foundationSecondToLast = {}
    systemSummaryLast = {}
    systemSummarySecondToLast = {}
    servicesInSystemLast = {}
    servicesInSystemSecondToLast = {}
    hasFoundation = True
    for thisInstance in instancesOfSystem:
      if thisInstance['changeDictReverseCounter'] == 0:
        systemSummaryLast = thisInstance['systemToChange']
        if 'foundation' in thisInstance['systemToChange']:
          foundationLast = thisInstance['systemToChange']['foundation']
        else:
          hasFoundation = False
        if (level == 'platform') or (level == 'services'):
          servicesInSystemLast = thisInstance['systemToChange']['services']
      if thisInstance['changeDictReverseCounter'] == 1:
        systemSummarySecondToLast = thisInstance['systemToChange']
        if 'foundation' in thisInstance['systemToChange']:
          foundationSecondToLast = thisInstance['systemToChange']['foundation']
        if (level == 'platform') or (level == 'services'):
          servicesInSystemSecondToLast = thisInstance['systemToChange']['services']
    systemSummaryChecker(systemSummaryLast, systemSummarySecondToLast)
    if hasFoundation:
      foundationChecker(systemSummaryLast["name"], foundationLast, foundationSecondToLast)
    if (level == 'platform') or (level == 'services'):
      servicesInSystemChecker(systemSummaryLast["name"], servicesInSystemLast, servicesInSystemSecondToLast)
  logString = "////////////////////////////////////////////////////////////////////"
  if writeLogBoolean:
    logWriter.writeMetaLog("acm", logString)

def systemSummaryChecker(systemSummaryLast, systemSummarySecondToLast):
  global writeLogBoolean
  if systemSummaryLast['steps'] != systemSummarySecondToLast['steps']:
    logString = "ERROR: The number of steps is different between two foundations which should have identical numbers of steps. "
    if writeLogBoolean:
      logWriter.writeMetaLog("acm", logString)
      exit(1)
  else:
    if systemSummaryLast['name'] == systemSummarySecondToLast['name']:
      changeKey = "platform/system:"+systemSummaryLast['name']
      logString = "        " + systemSummaryLast['name'] + " SUMMARY LEVEL: "
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
      logString = "            name: " + systemSummaryLast['name']
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
      if systemSummaryLast['status'] == systemSummarySecondToLast['status']:
        logString = "            system summary status did NOT change and is: " + systemSummaryLast['status']
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
      elif systemSummaryLast['status'] != systemSummarySecondToLast['status']:
        if systemSummarySecondToLast['status'] == "Completed":
          logString = "                ERROR: system summary status changed from " + systemSummarySecondToLast['status'] + " to " + systemSummaryLast['status'] + ". Halting program so you can debug. "
          changeDict = { "key":changeKey, "changes":[logString] }
          changesList.append(changeDict)
          if writeLogBoolean:
            logWriter.writeMetaLog("acm", logString)
            import traceback
            traceback.print_stack()
            exit(1)
        else:
          logString = "            system summary status changed from " + str(systemSummarySecondToLast['status']) + " to " + str(systemSummaryLast['status'])
          changeDict = { "key":changeKey, "changes":[logString] }
          changesList.append(changeDict)
          if writeLogBoolean:
            logWriter.writeMetaLog("acm", logString)
      if systemSummaryLast['currentStep'] == systemSummarySecondToLast['currentStep']:
        logString = "            system summary currentStep did NOT change and is: " + str(systemSummaryLast['currentStep']) + " out of " + str(systemSummaryLast['steps']) + " steps. "
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
      elif systemSummaryLast['currentStep'] != systemSummarySecondToLast['currentStep']:
        logString = "            system summary currentStep changed from " + str(systemSummarySecondToLast['currentStep']) + " to " + str(systemSummaryLast['currentStep']) + " out of " + str(systemSummaryLast['steps']) + " steps. "
        changeDict = { "key":changeKey, "changes":[logString] }
        changesList.append(changeDict)
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)

def servicesInSystemChecker(systemInstanceName, servicesInSystemLast, servicesInSystemSecondToLast):
  global writeLogBoolean
  if servicesInSystemLast['steps'] != servicesInSystemSecondToLast['steps']:
    logString = "ERROR: The number of steps is different between two foundations which should have identical numbers of steps. "
    if writeLogBoolean:
      logWriter.writeMetaLog("acm", logString)
      exit(1)
  else:
    changeKey = "platform/system:"+systemInstanceName+"/services"
    logString = "            SERVICES SUMMARY LEVEL: "
    if writeLogBoolean:
      logWriter.writeMetaLog("acm", logString)
    if servicesInSystemLast['status'] == servicesInSystemSecondToLast['status']:
      logString = "                all services summary status did NOT change and is: " + servicesInSystemLast['status']
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
    elif servicesInSystemLast['status'] != servicesInSystemSecondToLast['status']:
      if servicesInSystemSecondToLast['status'] == "Completed":
        logString = "                ERROR: all services summary status changed from " + servicesInSystemSecondToLast['status'] + " to " + servicesInSystemLast['status'] + ". Halting program so you can debug. "
        changeDict = { "key":changeKey, "changes":[logString] }
        changesList.append(changeDict)
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
          exit(1)
      else:
        logString = "                all services summary status changed from " + servicesInSystemSecondToLast['status'] + " to " + servicesInSystemLast['status']
        changeDict = { "key":changeKey, "changes":[logString] }
        changesList.append(changeDict)
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
    if servicesInSystemLast['currentStep'] == servicesInSystemSecondToLast['currentStep']:
      logString = "                all services summary currentStep did NOT change and is: " + str(servicesInSystemLast['currentStep']) + " out of " + str(servicesInSystemLast['steps']) + " steps. "
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
    elif servicesInSystemLast['currentStep'] != servicesInSystemSecondToLast['currentStep']:
      logString = "                all services summary currentStep changed from " + str(servicesInSystemSecondToLast['currentStep']) + " to " + str(servicesInSystemLast['currentStep']) + " out of " + str(servicesInSystemLast['steps']) + " steps. "
      changeDict = { "key":changeKey, "changes":[logString] }
      changesList.append(changeDict)
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
    serviceTypesChecker(systemInstanceName, servicesInSystemLast['serviceTypes'], servicesInSystemSecondToLast['serviceTypes'])
  
def serviceTypesChecker(systemInstanceName, serviceTypesLast, serviceTypesSecondToLast):
#  changeKey = "platform/system:"+systemInstanceName+"/services"
  global writeLogBoolean
  logString = "                Each type of service is summarized as follows: "
  if writeLogBoolean:
    logWriter.writeMetaLog("acm", logString)
  typesList = []
  for serviceType in serviceTypesLast:
    typeName = serviceType['type']
    lastDict = serviceType
    secondToLastDict = {}
    for secondServiceType in serviceTypesSecondToLast:
      if secondServiceType['type'] == typeName:
        secondToLastDict = secondServiceType
    typeDict = {"type":typeName, "lastDict":lastDict, "secondToLastDict":secondToLastDict}
    typesList.append(typeDict)
  for type in typesList:
    changeKey = "platform/system:"+systemInstanceName+"/serviceTypes/"+type['type'] #tfBackend
    logString = "                    " + type['type'] + " summary is as follows: "
    if writeLogBoolean:
      logWriter.writeMetaLog("acm", logString)
    if type['lastDict']['steps'] != type['secondToLastDict']['steps']:
      logString = "ERROR: The number of steps is different between two service types which should have identical numbers of steps. "
      if writeLogBoolean:
        logWriter.writeMetaLog("acm", logString)
        exit(1)
    else:
      if type['lastDict']['status'] == type['secondToLastDict']['status']:
        logString = "                        " + type['type'] + " summary status did NOT change and is: " + type['lastDict']['status']
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
      elif type['lastDict']['status'] != type['secondToLastDict']['status']:
        if type['secondToLastDict']['status'] == "Completed":
          logString = "                ERROR: " + type['type'] + " summary status changed from " + type['secondToLastDict']['status'] + " to " + type['lastDict']['status'] + ". Halting program so you can debug. "
          changeDict = { "key":changeKey, "changes":[logString] }
          changesList.append(changeDict)
          if writeLogBoolean:
            logWriter.writeMetaLog("acm", logString)
            exit(1)
        else:
          logString = "                        " + type['type'] + " summary status changed from " + type['secondToLastDict']['status'] + " to " + type['lastDict']['status']
          changeDict = { "key":changeKey, "changes":[logString] }
          changesList.append(changeDict)
          if writeLogBoolean:
            logWriter.writeMetaLog("acm", logString)
      if type['lastDict']['currentStep'] == type['secondToLastDict']['currentStep']:
        logString = "                        " + type['type'] + " summary currentStep did NOT change and is: " + str(type['lastDict']['currentStep']) + " out of a total " + str(type['lastDict']['steps']) + " steps. "
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
      elif type['lastDict']['currentStep'] != type['secondToLastDict']['currentStep']:
        logString = "                        " + type['type'] + " summary currentStep changed from " + str(type['secondToLastDict']['currentStep']) + " to " + str(type['lastDict']['currentStep']) + " out of a total " + str(type['lastDict']['steps']) + " steps. "
        changeDict = { "key":changeKey, "changes":[logString] }
        changesList.append(changeDict)
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
      if len(type['lastDict']['instances']) > 0:
        logString = "                         INSTANCES OF " + type['type'] + " SERVICE TYPE ARE: "
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
        for lastKey in type['lastDict']['instances'].keys():
          for secondToLastKey in type['secondToLastDict']['instances'].keys():
            if lastKey == secondToLastKey:
#.
              if type['lastDict']['instances'][lastKey]['steps'] != type['secondToLastDict']['instances'][secondToLastKey]['steps']:
                logString = "ERROR: The number of steps is different between two instances of this service, which should have identical numbers of steps. "
                if writeLogBoolean:
                  logWriter.writeMetaLog("acm", logString)
                  exit(1)
              else:
                changeKey = "platform/system:"+systemInstanceName+"/serviceTypes/"+type['type']+"/"+lastKey #tfBackend
                logString = "                            " + lastKey + " instance of " + type['type']
                if writeLogBoolean:
                  logWriter.writeMetaLog("acm", logString)
                if type['lastDict']['instances'][lastKey]['status'] == type['secondToLastDict']['instances'][secondToLastKey]['status']:
                  logString = "                                " + lastKey + " summary status did NOT change and is: " + type['lastDict']['instances'][lastKey]['status']
                  if writeLogBoolean:
                    logWriter.writeMetaLog("acm", logString)
                elif type['lastDict']['instances'][lastKey]['status'] != type['secondToLastDict']['instances'][secondToLastKey]['status']:
                  if type['secondToLastDict']['instances'][secondToLastKey]['status'] == "Completed":
                    logString = "                ERROR: "+ lastKey + " summary status changed from " + type['secondToLastDict']['instances'][secondToLastKey]['status'] + " to " + type['lastDict']['instances'][lastKey]['status'] + ". Halting program so you can debug. "
                    changeDict = { "key":changeKey, "changes":[logString] }
                    changesList.append(changeDict)
                    if writeLogBoolean:
                      logWriter.writeMetaLog("acm", logString)
                      exit(1)
                  else:
                    logString = "                                " + lastKey + " summary status changed from " + type['secondToLastDict']['instances'][secondToLastKey]['status'] + " to " + type['lastDict']['instances'][lastKey]['status']
                    changeDict = { "key":changeKey, "changes":[logString] }
                    changesList.append(changeDict)
                    if writeLogBoolean:
                      logWriter.writeMetaLog("acm", logString)
                if type['lastDict']['instances'][lastKey]['currentStep'] == type['secondToLastDict']['instances'][secondToLastKey]['currentStep']:
                  logString = "                                " + lastKey + " summary currentStep did NOT change and is: " + str(type['lastDict']['instances'][lastKey]['currentStep']) + " out of a total " + str(type['lastDict']['instances'][lastKey]['steps']) + " steps. "
                  if writeLogBoolean:
                    logWriter.writeMetaLog("acm", logString)
                elif type['lastDict']['instances'][lastKey]['currentStep'] != type['secondToLastDict']['instances'][secondToLastKey]['currentStep']:
                  logString = "                                " + lastKey + " summary currentStep changed from " + str(type['secondToLastDict']['instances'][secondToLastKey]['currentStep']) + " to " + str(type['lastDict']['instances'][lastKey]['currentStep']) + " out of a total " + str(type['lastDict']['instances'][lastKey]['steps']) + " steps. "
                  changeDict = { "key":changeKey, "changes":[logString] }
                  changesList.append(changeDict)
                  if writeLogBoolean:
                    logWriter.writeMetaLog("acm", logString)
#.
      else:
        logString = "                         THERE ARE NO INSTANCES OF " + type['type'] + " SERVICE TYPE DEFINED IN YOUR CONFIGURATION. "
        if writeLogBoolean:
          logWriter.writeMetaLog("acm", logString)
  
def getLineDict(changeDict):
  intro = changeDict['line']
  theRest = intro[intro.find('{'):]
  lineDict = ast.literal_eval(theRest)
  return lineDict

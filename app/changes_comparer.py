## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import re
import ast
import sys

from log_writer import log_writer

class changes_comparer:
  
  def __init__(self):  
    pass

  ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
  changesList = []
  writeLogBoolean = False

  #@public
  def runComparer(self, level, changeReports, writeToLog):
    lw = log_writer()
    self.changesList.clear()
    self.writeLogBoolean = writeToLog
    changeDictReverseCounter = 0
    numChangeDicts = len(changeReports)
    if numChangeDicts == 0:
      logString = "ERROR: Invalid number of dicts in changeReports."
      if self.writeLogBoolean:
        lw.writeMetaLog("acm", logString)
  #    quit('water test!')
    elif numChangeDicts == 1:
      logString = "Found the first changeDict.  Skipping for now."
      if self.writeLogBoolean:
        lw.writeMetaLog("acm", logString)
  #    quit('aloha!')
    else:
  #    quit('koko!')
      self.overallChecker(changeReports)
    systemsToChangeList = []
    numSystemsToChange = 0
    logString = "    SYSTEMS:  Each system in the platform will be summarized one at a time as follows:  "
    if self.writeLogBoolean:
      lw.writeMetaLog("acm", logString)
    print('self.writeLogBoolean is: ', self.writeLogBoolean)
    print('len(changeReports) is: ', len(changeReports))
#    if len(changeReports) > 2:
#      quit('---567890poiuyt')
    for changeDict in reversed(changeReports):
      if changeDictReverseCounter < 2:
        lineDict = self.getLineDict(changeDict)
        systemsToChangeCounter = 0
        systemsToChange = lineDict['systemsToChange']
        numSystemsToChange = len(systemsToChange)
        for systemToChange in systemsToChange:
          systemToChangeSummary = {"changeDictReverseCounter":changeDictReverseCounter, "systemsToChangeCounter":systemsToChangeCounter, "systemToChange":systemToChange}
          systemsToChangeList.append(systemToChangeSummary)
          systemsToChangeCounter += 1
        changeDictReverseCounter += 1
    self.systemsToChangeChecker(level, systemsToChangeList, numSystemsToChange)
    logString = "CHANGE SUMMARY: "
    if self.writeLogBoolean:
      lw.writeMetaLog("acm", logString)
    if len(self.changesList) > 0:
      for change in self.changesList:
        for chg in change['changes']:
          logString = "... " + str(chg)
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)
      return False
    else:
      logString = "... THERE WERE NO CHANGES. "
      if self.writeLogBoolean:
        lw.writeMetaLog("acm", logString)
      return True

  #@private
  def overallChecker(self, changeReports):
    lw = log_writer()
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
        lineDict = self.getLineDict(changeDict)
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
    if self.writeLogBoolean:
      lw.writeMetaLog("acm", logString)
    logString = "    command is: " + command
    if self.writeLogBoolean:
      lw.writeMetaLog("acm", logString)
#    print("stepsLast is: ", stepsLast)
#    print("stepsSecondToLast is: ", stepsSecondToLast)
#    print("overallStatusLast is: ", overallStatusLast)
#    print("overallStatusSecondToLast is: ", overallStatusSecondToLast)
  #  quit('jonesy gogo')
    if stepsLast == stepsSecondToLast:
      if overallStatusLast != overallStatusSecondToLast:
        logString = "    overallStatus changed from " + overallStatusSecondToLast + " to " + overallStatusLast
        if (overallStatusSecondToLast == "NOT Started") and (overallStatusLast == "In Process"):
          changeDict = { "key":"platformStart", "changes":[logString] }
        elif (overallStatusSecondToLast == "In Process") and (overallStatusLast == "Completed"):
          changeDict = { "key":"platformEnd", "changes":[logString] }
        else:
          logString = "ERROR: Failed to populate key in platformStart or in platformEnd. "
          lw.writeMetaLog("acm", logString)
          sys.exit(1)
        self.changesList.append(changeDict)
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
      elif overallStatusLast == overallStatusSecondToLast:
        logString = "    overallStatus did NOT change since the last step and is: " + overallStatusLast
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
      if currentStepLast != currentStepSecondToLast:
        logString = "    currentStep changed from " + str(currentStepSecondToLast) + " to " + str(currentStepLast) + " out of " + str(stepsLast) + " steps. "
        changeDict = { "key":"platformStart", "changes":[logString] }
        self.changesList.append(changeDict)
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
      elif currentStepLast == currentStepSecondToLast:
        logString = "    currentStep did NOT change since the last step and is: " + str(currentStepLast) + " out of " + str(stepsLast) + " steps. "
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
    else:
      logString = "ERROR: the total number of steps changed between changeDict instances.  This is NOT valid.  Skipping so you can review your configuration to identify and fix whatever caused this problem."
      changeDict = { "key":"platformStart", "changes":[logString] }
      self.changesList.append(changeDict)
      if self.writeLogBoolean:
        lw.writeMetaLog("acm", logString)

  #@private
  def foundationChecker(self, systemInstanceName, foundationLast, foundationSecondToLast):
    lw = log_writer()
    if foundationLast['steps'] != foundationSecondToLast['steps']:
      logString = "ERROR: The number of steps is different between two foundations which should have identical numbers of steps. "
      if self.writeLogBoolean:
        lw.writeMetaLog("acm", logString)
        exit(1)
    else:
      if foundationLast['name'] == foundationSecondToLast['name']:
        changeKey = "platform/system:"+systemInstanceName+"/foundation"
        logString = "            FOUNDATION LEVEL: "
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
        logString = "                name: " + foundationLast['name']
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
        if foundationLast['status'] == foundationSecondToLast['status']:
          logString = "                foundation status did NOT change and is: " + foundationLast['status']
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)
        elif foundationLast['status'] != foundationSecondToLast['status']:
          if foundationSecondToLast['status'] == "Completed":
            logString = "                ERROR: foundation status changed from " + foundationSecondToLast['status'] + " to " + foundationLast['status'] + ". Halting program so you can debug. "
            changeDict = { "key":changeKey, "changes":[logString] }
            self.changesList.append(changeDict)
            if self.writeLogBoolean:
              lw.writeMetaLog("acm", logString)
              exit(1)
          else:
            logString = "                foundation status changed from " + foundationSecondToLast['status'] + " to " + foundationLast['status']
            changeDict = { "key":changeKey, "changes":[logString] }
            self.changesList.append(changeDict)
            if self.writeLogBoolean:
              lw.writeMetaLog("acm", logString)
        if foundationLast['currentStep'] == foundationSecondToLast['currentStep']:
          logString = "                foundation currentStep did NOT change and is: " + str(foundationLast['currentStep']) + " out of " + str(foundationLast['steps']) + " steps. "
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)
        elif foundationLast['currentStep'] != foundationSecondToLast['currentStep']:
          logString = "                foundation currentStep changed from " + str(foundationSecondToLast['currentStep']) + " to " + str(foundationLast['currentStep']) + " out of " + str(foundationLast['steps']) + " steps. "
          changeDict = { "key":changeKey, "changes":[logString] }
          self.changesList.append(changeDict)
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)

  #@private
  def systemsToChangeChecker(self, level, systemsToChangeList, numSystemsToChange):
    lw = log_writer()
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
          if (level == 'platform') or (level == 'services') or (level == 'servicetype') or (level == 'serviceinstance'):
            servicesInSystemLast = thisInstance['systemToChange']['services']
        if thisInstance['changeDictReverseCounter'] == 1:
          systemSummarySecondToLast = thisInstance['systemToChange']
          if 'foundation' in thisInstance['systemToChange']:
            foundationSecondToLast = thisInstance['systemToChange']['foundation']
          if (level == 'platform') or (level == 'services') or (level == 'servicetype') or (level == 'serviceinstance'):
            servicesInSystemSecondToLast = thisInstance['systemToChange']['services']
      self.systemSummaryChecker(systemSummaryLast, systemSummarySecondToLast)
      if hasFoundation:
        self.foundationChecker(systemSummaryLast["name"], foundationLast, foundationSecondToLast)
      if (level == 'platform') or (level == 'services') or (level == 'servicetype') or (level == 'serviceinstance'):
        self.servicesInSystemChecker(systemSummaryLast["name"], servicesInSystemLast, servicesInSystemSecondToLast)
    logString = "////////////////////////////////////////////////////////////////////"
    if self.writeLogBoolean:
      lw.writeMetaLog("acm", logString)

  #@private
  def systemSummaryChecker(self, systemSummaryLast, systemSummarySecondToLast):
    lw = log_writer()
    if systemSummaryLast['steps'] != systemSummarySecondToLast['steps']:
      logString = "ERROR: The number of steps is different between two foundations which should have identical numbers of steps. "
      if self.writeLogBoolean:
        lw.writeMetaLog("acm", logString)
        exit(1)
    else:
      if systemSummaryLast['name'] == systemSummarySecondToLast['name']:
        changeKey = "platform/system:"+systemSummaryLast['name']
        logString = "        " + systemSummaryLast['name'] + " SUMMARY LEVEL: "
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
        logString = "            name: " + systemSummaryLast['name']
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
        if systemSummaryLast['status'] == systemSummarySecondToLast['status']:
          logString = "            system summary status did NOT change and is: " + systemSummaryLast['status']
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)
        elif systemSummaryLast['status'] != systemSummarySecondToLast['status']:
          if systemSummarySecondToLast['status'] == "Completed":
            logString = "                ERROR: system summary status changed from " + systemSummarySecondToLast['status'] + " to " + systemSummaryLast['status'] + ". Halting program so you can debug. "
            changeDict = { "key":changeKey, "changes":[logString] }
            self.changesList.append(changeDict)
            if self.writeLogBoolean:
              lw.writeMetaLog("acm", logString)
              import traceback
              traceback.print_stack()
              exit(1)
          else:
            logString = "            system summary status changed from " + str(systemSummarySecondToLast['status']) + " to " + str(systemSummaryLast['status'])
            changeDict = { "key":changeKey, "changes":[logString] }
            self.changesList.append(changeDict)
            if self.writeLogBoolean:
              lw.writeMetaLog("acm", logString)
        if systemSummaryLast['currentStep'] == systemSummarySecondToLast['currentStep']:
          logString = "            system summary currentStep did NOT change and is: " + str(systemSummaryLast['currentStep']) + " out of " + str(systemSummaryLast['steps']) + " steps. "
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)
        elif systemSummaryLast['currentStep'] != systemSummarySecondToLast['currentStep']:
          logString = "            system summary currentStep changed from " + str(systemSummarySecondToLast['currentStep']) + " to " + str(systemSummaryLast['currentStep']) + " out of " + str(systemSummaryLast['steps']) + " steps. "
          changeDict = { "key":changeKey, "changes":[logString] }
          self.changesList.append(changeDict)
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)

  #@private
  def servicesInSystemChecker(self, systemInstanceName, servicesInSystemLast, servicesInSystemSecondToLast):
    lw = log_writer()
    if servicesInSystemLast['steps'] != servicesInSystemSecondToLast['steps']:
      logString = "ERROR: The number of steps is different between two foundations which should have identical numbers of steps. "
      if self.writeLogBoolean:
        lw.writeMetaLog("acm", logString)
        exit(1)
    else:
      changeKey = "platform/system:"+systemInstanceName+"/services"
      logString = "            SERVICES SUMMARY LEVEL: "
      if self.writeLogBoolean:
        lw.writeMetaLog("acm", logString)
      if servicesInSystemLast['status'] == servicesInSystemSecondToLast['status']:
        logString = "                all services summary status did NOT change and is: " + servicesInSystemLast['status']
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
      elif servicesInSystemLast['status'] != servicesInSystemSecondToLast['status']:
        if servicesInSystemSecondToLast['status'] == "Completed":
          logString = "                ERROR: all services summary status changed from " + servicesInSystemSecondToLast['status'] + " to " + servicesInSystemLast['status'] + ". Halting program so you can debug. "
          changeDict = { "key":changeKey, "changes":[logString] }
          self.changesList.append(changeDict)
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)
            exit(1)
        else:
          logString = "                all services summary status changed from " + servicesInSystemSecondToLast['status'] + " to " + servicesInSystemLast['status']
          changeDict = { "key":changeKey, "changes":[logString] }
          self.changesList.append(changeDict)
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)
      if servicesInSystemLast['currentStep'] == servicesInSystemSecondToLast['currentStep']:
        logString = "                all services summary currentStep did NOT change and is: " + str(servicesInSystemLast['currentStep']) + " out of " + str(servicesInSystemLast['steps']) + " steps. "
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
      elif servicesInSystemLast['currentStep'] != servicesInSystemSecondToLast['currentStep']:
        logString = "                all services summary currentStep changed from " + str(servicesInSystemSecondToLast['currentStep']) + " to " + str(servicesInSystemLast['currentStep']) + " out of " + str(servicesInSystemLast['steps']) + " steps. "
        changeDict = { "key":changeKey, "changes":[logString] }
        self.changesList.append(changeDict)
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
      self.serviceTypesChecker(systemInstanceName, servicesInSystemLast['serviceTypes'], servicesInSystemSecondToLast['serviceTypes'])
  
  #@private
  def serviceTypesChecker(self, systemInstanceName, serviceTypesLast, serviceTypesSecondToLast):
    lw = log_writer()
    logString = "                Each type of service is summarized as follows: "
    if self.writeLogBoolean:
      lw.writeMetaLog("acm", logString)
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
#    print('typesList is: ', typesList)
    for type in typesList:
      changeKey = "platform/system:"+systemInstanceName+"/serviceTypes/"+type['type'] #tfBackend
      logString = "                    " + type['type'] + " summary is as follows: "
      if self.writeLogBoolean:
        lw.writeMetaLog("acm", logString)
      if type['lastDict']['steps'] != type['secondToLastDict']['steps']:
        logString = "ERROR: The number of steps is different between two service types which should have identical numbers of steps. "
        if self.writeLogBoolean:
          lw.writeMetaLog("acm", logString)
          exit(1)
      else:
        if type['lastDict']['status'] == type['secondToLastDict']['status']:
          logString = "                        " + type['type'] + " summary status did NOT change and is: " + type['lastDict']['status']
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)
        elif type['lastDict']['status'] != type['secondToLastDict']['status']:
          if type['secondToLastDict']['status'] == "Completed":
            logString = "                ERROR: " + type['type'] + " summary status changed from " + type['secondToLastDict']['status'] + " to " + type['lastDict']['status'] + ". Halting program so you can debug. "
            changeDict = { "key":changeKey, "changes":[logString] }
            self.changesList.append(changeDict)
            if self.writeLogBoolean:
              lw.writeMetaLog("acm", logString)
              exit(1)
          else:
            logString = "                        " + type['type'] + " summary status changed from " + type['secondToLastDict']['status'] + " to " + type['lastDict']['status']
            changeDict = { "key":changeKey, "changes":[logString] }
            self.changesList.append(changeDict)
            if self.writeLogBoolean:
              lw.writeMetaLog("acm", logString)
        if type['lastDict']['currentStep'] == type['secondToLastDict']['currentStep']:
          logString = "                        " + type['type'] + " summary currentStep did NOT change and is: " + str(type['lastDict']['currentStep']) + " out of a total " + str(type['lastDict']['steps']) + " steps. "
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)
        elif type['lastDict']['currentStep'] != type['secondToLastDict']['currentStep']:
          logString = "                        " + type['type'] + " summary currentStep changed from " + str(type['secondToLastDict']['currentStep']) + " to " + str(type['lastDict']['currentStep']) + " out of a total " + str(type['lastDict']['steps']) + " steps. "
          changeDict = { "key":changeKey, "changes":[logString] }
          self.changesList.append(changeDict)
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)
        if len(type['lastDict']['instances']) > 0:
          logString = "                         INSTANCES OF " + type['type'] + " SERVICE TYPE ARE: "
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)
          for lastKey in type['lastDict']['instances'].keys():
            for secondToLastKey in type['secondToLastDict']['instances'].keys():
              if lastKey == secondToLastKey:
                if type['lastDict']['instances'][lastKey]['steps'] != type['secondToLastDict']['instances'][secondToLastKey]['steps']:
                  logString = "ERROR: The number of steps is different between two instances of this service, which should have identical numbers of steps. "
                  if self.writeLogBoolean:
                    lw.writeMetaLog("acm", logString)
                    exit(1)
                else:
                  changeKey = "platform/system:"+systemInstanceName+"/serviceTypes/"+type['type']+"/"+lastKey #tfBackend
                  logString = "                            " + lastKey + " instance of " + type['type']
                  if self.writeLogBoolean:
                    lw.writeMetaLog("acm", logString)
                  if type['lastDict']['instances'][lastKey]['status'] == type['secondToLastDict']['instances'][secondToLastKey]['status']:
                    logString = "                                " + lastKey + " summary status did NOT change and is: " + type['lastDict']['instances'][lastKey]['status']
                    if self.writeLogBoolean:
                      lw.writeMetaLog("acm", logString)
                  elif type['lastDict']['instances'][lastKey]['status'] != type['secondToLastDict']['instances'][secondToLastKey]['status']:
                    if type['secondToLastDict']['instances'][secondToLastKey]['status'] == "Completed":
                      logString = "                ERROR: "+ lastKey + " summary status changed from " + type['secondToLastDict']['instances'][secondToLastKey]['status'] + " to " + type['lastDict']['instances'][lastKey]['status'] + ". Halting program so you can debug. "
                      changeDict = { "key":changeKey, "changes":[logString] }
                      self.changesList.append(changeDict)
                      if self.writeLogBoolean:
                        lw.writeMetaLog("acm", logString)
                        exit(1)
                    else:
                      logString = "                                " + lastKey + " summary status changed from " + type['secondToLastDict']['instances'][secondToLastKey]['status'] + " to " + type['lastDict']['instances'][lastKey]['status']
                      changeDict = { "key":changeKey, "changes":[logString] }
                      self.changesList.append(changeDict)
                      if self.writeLogBoolean:
                        lw.writeMetaLog("acm", logString)
                  if type['lastDict']['instances'][lastKey]['currentStep'] == type['secondToLastDict']['instances'][secondToLastKey]['currentStep']:
                    logString = "                                " + lastKey + " summary currentStep did NOT change and is: " + str(type['lastDict']['instances'][lastKey]['currentStep']) + " out of a total " + str(type['lastDict']['instances'][lastKey]['steps']) + " steps. "
                    if self.writeLogBoolean:
                      lw.writeMetaLog("acm", logString)
                  elif type['lastDict']['instances'][lastKey]['currentStep'] != type['secondToLastDict']['instances'][secondToLastKey]['currentStep']:
                    logString = "                                " + lastKey + " summary currentStep changed from " + str(type['secondToLastDict']['instances'][secondToLastKey]['currentStep']) + " to " + str(type['lastDict']['instances'][lastKey]['currentStep']) + " out of a total " + str(type['lastDict']['instances'][lastKey]['steps']) + " steps. "
                    changeDict = { "key":changeKey, "changes":[logString] }
                    self.changesList.append(changeDict)
                    if self.writeLogBoolean:
                      lw.writeMetaLog("acm", logString)
        else:
          logString = "                         THERE ARE NO INSTANCES OF " + type['type'] + " SERVICE TYPE DEFINED IN YOUR CONFIGURATION. "
          if self.writeLogBoolean:
            lw.writeMetaLog("acm", logString)

  #@private
  def getLineDict(self, changeDict):
    intro = changeDict['line']
    theRest = intro[intro.find('{'):]
    lineDict = ast.literal_eval(theRest)
    return lineDict

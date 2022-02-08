import logWriter
import changes_taxonomy
import changes_comparer

changesManifest = []
changeIndex = 0
changeCounter = 0

def changePreview(level, command):
#  if level == 'platform':  ## Just the one single line below was indented.  nothing more.
  createStartOfPlatformRun()
  for changeKey in changes_taxonomy.changeTaxonomy:
    if changeKey =="systemsToChange":
      if command == 'on':
        for system in changes_taxonomy.changeTaxonomy[changeKey]:
          createManifestForASystem(level,system,command)
      elif command == 'off':
        for system in reversed(changes_taxonomy.changeTaxonomy[changeKey]):
          createManifestForASystem(level,system,command)
#  if level == 'platform':  ## Just the one single line below was indented.  nothing more.
  createEndOfPlatformRun()
  emitChangesToLogs()

def createManifestForASystem(level,system,command):
  systemString = "platform/system:"+system["name"]
#  if (level == 'platform') or (level == 'services'):  ##Just the one next line was indented.  nothing more.
  createStartOfASystem(systemString)
  #WORK ITEM:  The following two command=on/off blocks can be shrunk by putting the foundation and 
  #services code into their own functions instead of repeating the same redundant code in 
  #different order as we are doing below.
  if command == "on":
    for systemKey in system:
      if systemKey == "foundation":
        foundationString = systemString + "/foundation"
        createStartOfAFoundation(systemString, foundationString)
        createEndOfAFoundation(foundationString)
      if (level == 'platform') or (level == 'services'):
        if systemKey == "services":  
          serviceTypesString = systemString + "/serviceTypes"
          createStartOfAServicesSection(systemString, serviceTypesString)
          for serviceTypeKey in system[systemKey]:
            if serviceTypeKey == "serviceTypes":
              for serviceType in system[systemKey][serviceTypeKey]:
                serviceTypeSingleString = serviceTypesString + "/" + serviceType["type"]
                createStartOfAServiceType(serviceTypesString, serviceTypeSingleString)
                for serviceInstance in serviceType["instances"]:
                  serviceInstanceString = serviceTypeSingleString + "/" + serviceInstance
                  createStartOfAnInstanceOfAServiceType(serviceTypeSingleString, serviceInstanceString)
                  createEndOfAnInstanceOfAServiceType(serviceInstanceString)
                createEndOfAServiceType(serviceTypeSingleString)
          createEndOfAServicesSection(serviceTypesString)
#    if (level == 'platform') or (level == 'services'): ##Just the one next line was indented.  nothing more.  
    createEndOfASystem(systemString)
  if command == "off":
    for systemKey in system:
      if systemKey == "services":  
        serviceTypesString = systemString + "/serviceTypes"
        createStartOfAServicesSection(systemString, serviceTypesString)
        for serviceTypeKey in system[systemKey]:
          if serviceTypeKey == "serviceTypes":
            for serviceType in system[systemKey][serviceTypeKey]:
              serviceTypeSingleString = serviceTypesString + "/" + serviceType["type"]
              createStartOfAServiceType(serviceTypesString, serviceTypeSingleString)
              for serviceInstance in serviceType["instances"]:
                serviceInstanceString = serviceTypeSingleString + "/" + serviceInstance
                createStartOfAnInstanceOfAServiceType(serviceTypeSingleString, serviceInstanceString)
                createEndOfAnInstanceOfAServiceType(serviceInstanceString)
              createEndOfAServiceType(serviceTypeSingleString)
        createEndOfAServicesSection(serviceTypesString)
    for systemKey in system:
      if systemKey == "foundation":
        foundationString = systemString + "/foundation"
        createStartOfAFoundation(systemString, foundationString)
        createEndOfAFoundation(foundationString)
    createEndOfASystem(systemString)


##1.13 Start of new function to emit changes to logs
def emitChangesToLogs():
  global changesManifest  
  global changeCounter  
#  logString = "changeCounter is: " + str(changeCounter)  
#  logWriter.writeLogVerbose("acm", logString)
#  logString = "changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)  
  logString = "The current status of the " + str(len(changesManifest)) + " changes being made in this run is: "  
  logWriter.writeLogVerbose("acm", logString)
  for change in changesManifest:
    logString = change
    logWriter.writeLogVerbose("acm", logString)

##1.13 End of new function to emit changes to logs

##1.14 Start of new function to initialize change management data structures
def initializeChangesManagementDataStructures(level, command):
  changes_taxonomy.assembleChangeTaxonomy(level, command)
  logString = " At beginning, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  outputLine = "[ acm ] " + logString
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)

  changePreview(level, command)


##1.14 Start of new function to initialize change management data structures

#.......................................
def createStartOfPlatformRun():
  global changesManifest
  global changeIndex
  changeIndex = 1
  changeSummaryDict = {
    "changeIndex":changeIndex, 
	"changeType":"Start of platform run", 
    "key":"platformStart",
    "changes": [
	  {"affectedUnit":"platform", "Status":"To In Process", "Step":"Same", "changeCompleted":False}
	]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateStartOfPlatformRun(level, newStatus):
  #1 validate newStatus
  if (newStatus != "In Process") and (newStatus != "Completed"):
    logString = "ERROR: newStatus had an invalid value: " + newStatus + " .  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)
  #2 update changeTaxonomy
  changes_taxonomy.updateStartOfPlatformRun(newStatus)
  #3 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  match = False
  global changesManifest
  for change in changesManifest:
    if int(change['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
      print("change_key is: ", change['key'])
      for changeItems in changes_comparer.changesList:
        if changeItems['key'] == change['key']:
          for changeItem in changeItems['changes']:
            if "overallStatus changed from NOT Started to In Process" in changeItem:
              match = True
              #4 update change in changesManifest
              for changesBlock in changesManifest:
                for changeKey in changesBlock:
                  if changeKey == "changes":
                    for change in changesBlock[changeKey]:
                      if change["affectedUnit"] == "platform":
                        if change["Status"].replace('To ','') == newStatus:
                          change["changeCompleted"] = True
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  emitChangesToLogs()
  if match == False:
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)
  print("changes_comparer.changesList is: ", changes_comparer.changesList)
#  changes_comparer.changesList.clear()


#........................................
def createStartOfASystem(systemString):
  global changesManifest
  global changeIndex
  changeSummaryDict = {
    "changeIndex":changeIndex, 
    "changeType":"Start of a system", 
    "key":systemString,
    "changes": [
      {"affectedUnit":"platform", "Status":"same", "Step":"+1", "changeCompleted":False},
      {"affectedUnit":systemString, "Status":"To In Process", "Step":"Same", "changeCompleted":False}
    ]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateStartOfASystem(level, systemInstanceName, newStatus):
  #1 update changeTaxonomy
  changes_taxonomy.updateStartOfASystem(level, systemInstanceName, newStatus)
  #2 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
  match1 = False
  match2 = False
  global changesManifest
  for change in changesManifest:
    if int(change['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
      for changeItems in changes_comparer.changesList:
        if changeItems['key'] == change['key']:
          for changeItem in changeItems['changes']:
            if "system summary status changed from NOT Started to In Process" in changeItem:
              match1 = True
              for changeFields in change["changes"]:
                affUnitName = "platform/system:" + systemInstanceName
                if changeFields['affectedUnit'] == affUnitName:
                  if changeFields["Status"].replace('To ','') == newStatus:
                    changeFields["changeCompleted"] = True
        elif changeItems["key"] == "platformStart":
          for changeItem in changeItems['changes']:
            if "currentStep changed from" in changeItem:
              #ADD WORK ITEM TO CHECK THE SPECIFIC CURRENT STEP AND TOTAL STEPS TO COMPLEMENT THIS HIGH LEVEL CHECK.
              match2 = True
              for changeFields in change["changes"]:
                if changeFields["affectedUnit"] == "platform":
                  if (changeFields["Step"] == "+1") and (changeFields["Status"] == "same"):
                    if changeFields["changeCompleted"] == False:
                      changeFields["changeCompleted"] = True
  print('match1 and match2 are: ', match1, ' ', match2)
#  quit("bbb")
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  emitChangesToLogs()
  if (match1 == False) or (match2 == False):
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)
#..


#........................................
def createStartOfAFoundation(systemString, foundationString):
  global changesManifest
  global changeIndex
  changeSummaryDict = {
    "changeIndex":changeIndex, 
    "changeType":"Start of a foundation", 
    "key":systemString,
    "changes": [
      {"affectedUnit":systemString, "Status":"same", "Step":"+1", "changeCompleted":False},
      {"affectedUnit":foundationString, "Status":"To In Process", "Step":"+1", "changeCompleted":False}
    ]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateStartOfAFoundation(level, systemInstanceName, newStatus):
  #1 validate newStatus
  if (newStatus != "In Process"):
    logString = "ERROR: newStatus had an invalid value: " + newStatus + " .  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)
  #2 update changeTaxonomy
  changes_taxonomy.updateStartOfAFoundation(systemInstanceName, newStatus)
  #3 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  #4 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
  match1 = False
  match2 = False
  match3 = False
  global changesManifest
  for change in changesManifest:
    if int(change['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
      for changeItems in changes_comparer.changesList:
        if changeItems['key'] == change['key']+"/foundation":
          for changeItem in changeItems['changes']:
            if "foundation status changed from NOT Started to In Process" in changeItem:
              for changeElement in change['changes']:
                if changeElement["affectedUnit"] == "platform/system:"+systemInstanceName+"/foundation":
                  if (changeElement["Step"] == "+1") and ("To In Process" in changeElement["Status"]):
                    changeElement["changeCompleted"] = True
                    match1 = True
            elif "foundation currentStep changed from" in changeItem:
              #Bundling update to changesManifest in preceding block because of how the change is written in the changesManifest
              #But keeping this here as a validation check.
              match2 = True
        elif changeItems["key"] == change['key']:
          for changeItem in changeItems['changes']:
            if "system summary currentStep changed from" in changeItem:
              for changeElement in change['changes']:
                if changeElement["affectedUnit"] == "platform/system:" + systemInstanceName:
                  if changeElement["Step"] == "+1":
                    changeElement["changeCompleted"] = True
                    match3 = True
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  emitChangesToLogs()
  if (match1 == False) or (match2 == False) or (match3 == False):
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)

#........................................
def createEndOfAFoundation(foundationString):
  global changesManifest
  global changeIndex
  changeSummaryDict = {
    "changeIndex":changeIndex, 
    "changeType":"End of a foundation", 
    "key":foundationString,
    "changes": [
      {"affectedUnit":foundationString, "Status":"To Completed", "Step":"Same", "changeCompleted":False}
    ]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateEndOfAFoundation(level, systemInstanceName):
  #1 update changeTaxonomy
  changes_taxonomy.updateEndOfAFoundation(systemInstanceName)
  #2 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
  match = False
  global changesManifest
  for change in changesManifest:
    if int(change['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
      for changeItems in changes_comparer.changesList:
        print("changeItems['key']", changeItems['key'])
        print("change['key']", change['key'])
        if changeItems['key'] == change['key']:
          for changeItem in changeItems['changes']:
            if "foundation status changed from In Process to Completed" in changeItem:
              for changeElement in change['changes']:
                if changeElement["affectedUnit"] == "platform/system:"+systemInstanceName+"/foundation":
                  if "To Completed" in changeElement["Status"]:
                    changeElement["changeCompleted"] = True
                    match = True
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  emitChangesToLogs()
  if match == False:
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)

#.........................................
def createStartOfAServicesSection(systemString, serviceTypesString):
  global changesManifest
  global changeIndex
  changeSummaryDict = {
    "changeIndex":changeIndex, 
    "changeType":"Start of a services section", 
    "key":systemString,
    "changes": [
      {"affectedUnit":systemString, "Status":"same", "Step":"+1", "changeCompleted":False},
      {"affectedUnit":serviceTypesString, "Status":"To In Process", "Step":"same", "changeCompleted":False}
    ]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateStartOfAServicesSection(level, systemInstanceName):
  #1 update changeTaxonomy
  changes_taxonomy.updateStartOfAServicesSection(level, systemInstanceName)
  #2 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
  match1 = False
  match2 = False
  global changesManifest
  for change in changesManifest:
    if change["changeType"] == "Start of a services section":
      if int(change['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
        for changeItems in changes_comparer.changesList:
          print("changeItems['key']", changeItems['key'])
          print("changeItems", changeItems)
          print("change['key']", change['key'])
          if changeItems['key'] == change['key']:
            for changeItem in changeItems['changes']:
              if "system summary currentStep changed from" in changeItem:
                print("Q")
                for changeElement in change['changes']:
                  affUnitName = "platform/system:" + systemInstanceName
                  if changeElement["affectedUnit"] == affUnitName:
                    if changeElement["Step"] == "+1":
                      changeElement["changeCompleted"] = True
                      match1 = True
          if changeItems['key'] == change['key']+"/services":
            for changeItem in changeItems['changes']:
              if "all services summary status changed from NOT Started to In Process" in changeItem:
                print("R")
                for changeElement in change['changes']:
                  affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes"
                  if changeElement["affectedUnit"] == affUnitName:
                    if changeElement["Status"].replace('To ','') == "In Process":
                      changeElement["changeCompleted"] = True
                      match2 = True
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  emitChangesToLogs()
  print("xx match1 and match2 are: ", match1, " ", match2)
  if (match1 == False) or (match2 == False):
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)

def updateStartOfSkipServicesSection():
  logString = "**************************************************************************************************************"
  logWriter.writeLogVerbose("acm", logString)
  logString = "WARNING: All service-related objects are being marked in changesManifest and changeTaxonomy as if they are being operated on because you used the --force flag.  These objects are NOT being operated on.  Instead, we assume that you designed your systems so that these objects will be deleted when the foundation is deleted.  You must validate destruction of these objects yourself when developing your automation systems. "
  logWriter.writeLogVerbose("acm", logString)
  logString = "**************************************************************************************************************"
  logWriter.writeLogVerbose("acm", logString)

def updateEndOfSkipServicesSection():
  logString = "**************************************************************************************************************"
  logWriter.writeLogVerbose("acm", logString)
  logString = "WARNING: All service-related objects are being marked in changesManifest and changeTaxonomy as if they are being operated on because you used the --force flag.  These objects are NOT being operated on.  Instead, we assume that you designed your systems so that these objects will be deleted when the foundation is deleted.  You must validate destruction of these objects yourself when developing your automation systems. "
  logWriter.writeLogVerbose("acm", logString)
  logString = "**************************************************************************************************************"
  logWriter.writeLogVerbose("acm", logString)

#.........................................
def createStartOfAServiceType(serviceTypesString, serviceTypeSingleString):
  global changesManifest
  global changeIndex
  changeSummaryDict = {
    "changeIndex":changeIndex, 
    "changeType":"Start of a serviceType", 
    "key":serviceTypesString,
    "changes": [
      {"affectedUnit":serviceTypesString, "Status":"same", "Step":"+1", "changeCompleted":False},
      {"affectedUnit":serviceTypeSingleString, "Status":"To In Process", "Step":"same", "changeCompleted":False}
    ]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateStartOfAServiceType(level, systemInstanceName, typeName):
#  quit("b")
  #1 update changeTaxonomy
  print("s")
  changes_taxonomy.updateStartOfAServiceType(systemInstanceName, typeName)
  #2 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  print("ss")
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  print("sss")
  #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
  match1 = False
  match2 = False
  global changesManifest
  #2 update change in changesManifest
  for changesBlock in changesManifest:
    print("ssss")
    if changesBlock["changeType"] == "Start of a serviceType":
      print("sssss")
      if int(changesBlock['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
        print("ssssss")
        for changeItems in changes_comparer.changesList:
          if (changeItems['key'] == "platform/system:"+systemInstanceName+"/services") and (changesBlock['key'] == "platform/system:"+systemInstanceName+"/serviceTypes"):
            print("sssssss")
            for changeItem in changeItems['changes']:
              if "all services summary currentStep changed from" in changeItem:
                for changeElement in changesBlock['changes']:
                  affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes"
                  if changeElement["affectedUnit"] == affUnitName:
                    if changeElement["Step"] == "+1":
                      changeElement["changeCompleted"] = True
                      match1 = True
          if (changeItems['key'] == "platform/system:"+systemInstanceName+"/serviceTypes/"+typeName) and (changesBlock['key'] == "platform/system:"+systemInstanceName+"/serviceTypes"):
            print("ssssssss")
            for changeItem in changeItems['changes']:
              if (typeName) in changeItem:
                if " summary status changed from" in changeItem:
                  for changeElement in changesBlock['changes']:
                    affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes/" + typeName
                    if changeElement["affectedUnit"] == affUnitName:
                      if changeElement["Status"].replace('To ','') == "In Process":
                        changeElement["changeCompleted"] = True
                        match2 = True
  print("... match1 and match2 are: ", match1 , " ", match2)
#  quit("b")
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  emitChangesToLogs()
  if (match1 == False) or (match2 == False):
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)

#.........................................
def createStartOfAnInstanceOfAServiceType(serviceTypeSingleString, serviceInstanceString):
  global changesManifest
  global changeIndex
  changeSummaryDict = {
    "changeIndex":changeIndex, 
    "changeType":"Start of an instance of a serviceType", 
    "key":serviceTypeSingleString,
    "changes": [
      {"affectedUnit":serviceTypeSingleString, "Status":"same", "Step":"+1", "changeCompleted":False},
      {"affectedUnit":serviceInstanceString, "Status":"To In Process", "Step":"+1", "changeCompleted":False}
    ]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateStartOfAnInstanceOfAServiceType(level, systemInstanceName, typeName, instanceName):
  global changesManifest
  #1 update changeTaxonomy
  changes_taxonomy.updateStartOfAnInstanceOfAServiceType(systemInstanceName, typeName, instanceName)
  #2 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  #2 update change in changesManifest
  #First get changeIndex in order to make sure this only runs the intended number of times.
  global changesManifest
  chgIdx = "-1"
  for changesBlock in changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes/" + typeName + "/" + instanceName
          if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "In Process"):
            chgIdx = changesBlock["changeIndex"]
  #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
  match1 = False
  match2 = False
  #2 update change in changesManifest
  for changesBlock in changesManifest:
    if changesBlock["changeIndex"] == chgIdx:
      if changesBlock["changeType"] == "Start of an instance of a serviceType":
        if int(changesBlock['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
          for changeItems in changes_comparer.changesList:
            if changeItems['key'] == "platform/system:"+systemInstanceName+"/serviceTypes/"+typeName: #) and (changesBlock['key'] == "platform/system:"+systemInstanceName+"/serviceTypes"):
              for changeItem in changeItems['changes']:
                if typeName+" summary currentStep changed from " in changeItem:
                  for changeElement in changesBlock['changes']:
                    affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes/" + typeName
                    if changeElement["affectedUnit"] == affUnitName:
                      if changeElement["Step"] == "+1":
                        changeElement["changeCompleted"] = True
                        match1 = True
                    affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes/" + typeName + "/" + instanceName
                    if (changeElement["affectedUnit"] == affUnitName) and (changeElement["Step"] == "+1") and (changeElement["Status"].replace('To ','') == "In Process"):
                      changeElement["changeCompleted"] = True
                      match2 = True
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  emitChangesToLogs()
  if (match1 == False) or (match2 == False):
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)

#........................................
def createEndOfAnInstanceOfAServiceType(serviceInstanceString):
  global changesManifest
  global changeIndex
  changeSummaryDict = {
    "changeIndex":changeIndex, 
    "changeType":"End of an instance of a serviceType", 
    "key":serviceInstanceString,
    "changes": [
      {"affectedUnit":serviceInstanceString, "Status":"To Completed", "Step":"same", "changeCompleted":False}
    ]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateEndOfAnInstanceOfAServiceType(level, systemInstanceName, typeName, instanceName):
  #1 update changeTaxonomy
  changes_taxonomy.updateEndOfAnInstanceOfAServiceType(systemInstanceName, typeName, instanceName)
  #2 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  #2 update change in changesManifest
  #First get changeIndex in order to make sure this only runs the intended number of times.
  global changesManifest
  chgIdx = "-1"
  for changesBlock in changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes/" + typeName + "/" + instanceName
          if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "Completed"):
            chgIdx = changesBlock["changeIndex"]
  #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
  match = False
  #2 update change in changesManifest
  for changesBlock in changesManifest:
    if changesBlock["changeIndex"] == chgIdx:
      if changesBlock["changeType"] == "End of an instance of a serviceType":
        if int(changesBlock['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
          for changeItems in changes_comparer.changesList:
            if changeItems['key'] == "platform/system:"+systemInstanceName+"/serviceTypes/"+typeName+"/"+instanceName: 
              for changeItem in changeItems['changes']:
                if instanceName +" summary status changed from In Process to Completed" in changeItem:
                  for changeElement in changesBlock['changes']:
                    affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes/" + typeName + "/" + instanceName
                    if (changeElement["affectedUnit"] == affUnitName) and (changeElement["Step"] == "same") and (changeElement["Status"].replace('To ','') == "Completed"):
                      changeElement["changeCompleted"] = True
                      match = True
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  emitChangesToLogs()
  if match == False:
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)

#.........................................
def createEndOfAServiceType(serviceTypeSingleString):
  global changesManifest
  global changeIndex
  changeSummaryDict = {
    "changeIndex":changeIndex, 
    "changeType":"End of a serviceType", 
    "key":serviceTypeSingleString,
    "changes": [
      {"affectedUnit":serviceTypeSingleString, "Status":"To Completed", "Step":"same", "changeCompleted":False}
    ]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateEndOfAServiceType(level, systemInstanceName, typeName):
  #1 update changeTaxonomy
  changes_taxonomy.updateEndOfAServiceType(systemInstanceName, typeName)
#--
  #2 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  #2 update change in changesManifest
  #First get changeIndex in order to make sure this only runs the intended number of times.
  global changesManifest
  chgIdx = "-1"
  for changesBlock in changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes/" + typeName
          if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "Completed"):
            chgIdx = changesBlock["changeIndex"]
  #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
  match = False
  #2 update change in changesManifest
  for changesBlock in changesManifest:
    if changesBlock["changeIndex"] == chgIdx:
      if changesBlock["changeType"] == "End of a serviceType":
        if int(changesBlock['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
          for changeItems in changes_comparer.changesList:
            if changeItems['key'] == "platform/system:"+systemInstanceName+"/serviceTypes/"+typeName: 
              for changeItem in changeItems['changes']:
                if typeName +" summary status changed from In Process to Completed" in changeItem:
                  for changeElement in changesBlock['changes']:
                    affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes/" + typeName
                    if changeElement["affectedUnit"] == affUnitName:
                      if changeElement["Status"].replace('To ','') == "Completed":
                        changeElement["changeCompleted"] = True
                        match = True
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  emitChangesToLogs()
  if match == False:
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)

#.........................................
def createEndOfAServicesSection(serviceTypesString):
  global changesManifest
  global changeIndex
  changeSummaryDict = {
    "changeIndex":changeIndex, 
    "changeType":"End of a services section", 
    "key":serviceTypesString,
    "changes": [
      {"affectedUnit":serviceTypesString, "Status":"To Completed", "Step":"same", "changeCompleted":False}
    ]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateEndOfAServicesSection(level, systemInstanceName):
  #1 update changeTaxonomy
  changes_taxonomy.updateEndOfAServicesSection(systemInstanceName)
  #2 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  #2 update change in changesManifest
  #First get changeIndex in order to make sure this only runs the intended number of times.
  global changesManifest
  chgIdx = "-1"
  for changesBlock in changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes"
          if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "Completed"):
            chgIdx = changesBlock["changeIndex"]
  #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
  match = False
  #2 update change in changesManifest
  for changesBlock in changesManifest:
    if changesBlock["changeIndex"] == chgIdx:
      if changesBlock["changeType"] == "End of a services section":
        if int(changesBlock['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
          for changeItems in changes_comparer.changesList:
            if changeItems['key'] == "platform/system:"+systemInstanceName+"/services": 
              for changeItem in changeItems['changes']:
                if "all services summary status changed from In Process to Completed" in changeItem:
                  for changeElement in changesBlock['changes']:
                    affUnitName = "platform/system:" + systemInstanceName + "/serviceTypes"
                    if changeElement['affectedUnit'] == affUnitName:
                      if changeElement["Status"].replace('To ','') == "Completed":
                        changeElement["changeCompleted"] = True
                        match = True
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  #quit('4!')
  emitChangesToLogs()
  if match == False:
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)

#..........................................
def createEndOfASystem(systemString):
  global changesManifest
  global changeIndex
  changeSummaryDict = {
    "changeIndex":changeIndex, 
    "changeType":"End of a system", 
    "key":systemString,
    "changes": [
      {"affectedUnit":systemString, "Status":"To Completed", "Step":"Same", "changeCompleted":False}
    ]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateEndOfASystem(level, systemInstanceName):
  #1 update changeTaxonomy
  changes_taxonomy.updateEndOfASystem(systemInstanceName)
  #2 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  #3 update change in changesManifest
  #First get changeIndex in order to make sure this only runs the intended number of times.
  global changesManifest
  chgIdx = "-1"
  for changesBlock in changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          affUnitName = "platform/system:" + systemInstanceName
          if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "Completed"):
            chgIdx = changesBlock["changeIndex"]
  #4 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
  match = False
  #5 update change in changesManifest
  for changesBlock in changesManifest:
    if changesBlock["changeIndex"] == chgIdx:
      if changesBlock["changeType"] == "End of a system":
        if int(changesBlock['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
          for changeItems in changes_comparer.changesList:
            if changeItems['key'] == "platform/system:"+systemInstanceName: 
              for changeItem in changeItems['changes']:
                if "system summary status changed from In Process to Completed" in changeItem:
                  for changeElement in changesBlock['changes']:
                    affUnitName = "platform/system:" + systemInstanceName
                    if changeElement["affectedUnit"] == affUnitName:
                      if changeElement["Status"].replace('To ','') == "Completed":
                        changeElement["changeCompleted"] = True
                        match = True
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  emitChangesToLogs()
  if match == False:
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)

#..........................................
def createEndOfPlatformRun():
  global changesManifest
  global changeIndex
  changeSummaryDict = {
    "changeIndex":changeIndex, 
	"changeType":"End of platform run", 
    "key":"platformEnd",
    "changes": [
	  {"affectedUnit":"platform", "Status":"To Completed", "Step":"Same", "changeCompleted":False}
	]
  }
  changesManifest.append(changeSummaryDict)
  changeIndex += 1

def updateEndOfPlatformRun(level):
  #1 update changeTaxonomy
  changes_taxonomy.updateEndOfPlatformRun()
  #2 get list of changes in new changeTaxonomy
  outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(changes_taxonomy.changeTaxonomy)
  changes_taxonomy.storeChangeTaxonomy(level, outputLine)
  #3 update change in changesManifest
  #First get changeIndex in order to make sure this only runs the intended number of times.
  global changesManifest
  chgIdx = "-1"
  for changesBlock in changesManifest:
    for changeKey in changesBlock:
      if changeKey == "changes":
        for change in changesBlock[changeKey]:
          affUnitName = "platform"
          if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "Completed"):
            chgIdx = changesBlock["changeIndex"]
  #4 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
  match = False
  #5 update change in changesManifest
  for changesBlock in changesManifest:
    if changesBlock["changeIndex"] == chgIdx:
      if changesBlock["changeType"] == "End of platform run":
        if int(changesBlock['changeIndex']) == (len(changes_taxonomy.changeReports)-1):
          for changeItems in changes_comparer.changesList:
            if changeItems['key'] == "platformEnd": 
              for changeItem in changeItems['changes']:
                if "overallStatus changed from In Process to Completed" in changeItem:
                  for changeElement in changesBlock['changes']:
                    if changeElement["affectedUnit"] == "platform":  
                      if changeElement["Status"].replace('To ','') == "Completed":  
                        changeElement["changeCompleted"] = True  
                        match = True
  validateChangeManifest((len(changes_taxonomy.changeReports)-1))
  emitChangesToLogs()
  if match == False:
    logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
    logWriter.writeLogVerbose("acm", logString)
    exit(1)

###
def validateChangeManifest(index):
  global changesManifest
  for changesBlock in changesManifest:
    for changeKey in changesBlock:
      # Must be True before and including current index
      if int(changesBlock['changeIndex']) > index:
        if changeKey == "changes":
          for change in changesBlock[changeKey]:
            if change["changeCompleted"] == True:
              logString = "ERROR: Change Manifest shows a true flag that should be false.  Post an issue on our github site so we can examine what went wrong.  "
              logWriter.writeLogVerbose("acm", logString)
              exit(1)
      #Must be False after current index
      if int(changesBlock['changeIndex']) <= index:
        if changeKey == "changes":
          for change in changesBlock[changeKey]:
            if change["changeCompleted"] == False:
              logString = "ERROR: Change Manifest shows a false flag that should be true.  Post an issue on our github site so we can examine what caused this.  "
              logWriter.writeLogVerbose("acm", logString)
              exit(1)

#def printChangeManifestToLogs():
#  global changesManifest
#  for change in changesManifest:
#    logString = str(change)
#    logWriter.writeLogVerbose("acm", logString)

## Copyright 2023 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

from log_writer import log_writer

class changes_manifest:
  
  def __init__(self):  
    self.changesManifest = []
    self.changeIndex = 0
    self.changeCounter = 0
    pass
   
  changesManifest = []
  changeIndex = 0
  changeCounter = 0
  
  #@private  
  def changePreview(self, ct, level, command):  
    self.createStartOfApplianceRun()  
    for changeKey in ct.changeTaxonomy:  
      if changeKey =="systemsToChange":
        if command == 'on':
          for system in ct.changeTaxonomy[changeKey]:
            self.createManifestForASystem(level,system,command)
        elif command == 'off':
          for system in reversed(ct.changeTaxonomy[changeKey]):
            self.createManifestForASystem(level,system,command)
    self.createEndOfApplianceRun()
    self.emitChangesToLogs()

  #@private
  def createManifestForASystem(self,level,system,command):
    systemString = "appliance/system:"+system["name"]
    self.createStartOfASystem(systemString)
    #WORK ITEM:  The following two command=on/off blocks can be shrunk by putting the foundation and 
    #services code into their own functions instead of repeating the same redundant code in 
    #different order as we are doing below.
    if command == "on":
      for systemKey in system:
        if systemKey == "foundation":
          foundationString = systemString + "/foundation"
          self.createStartOfAFoundation(systemString, foundationString)
          self.createEndOfAFoundation(foundationString)
        if (level == 'appliance') or (level == 'services') or (level == 'servicetype') or (level == 'serviceinstance'):
          if systemKey == "services":  
            serviceTypesString = systemString + "/serviceTypes"
            self.createStartOfAServicesSection(systemString, serviceTypesString)
            for serviceTypeKey in system[systemKey]:
              if serviceTypeKey == "serviceTypes":
                for serviceType in system[systemKey][serviceTypeKey]:
                  serviceTypeSingleString = serviceTypesString + "/" + serviceType["type"]
                  self.createStartOfAServiceType(serviceTypesString, serviceTypeSingleString)
                  for serviceInstance in serviceType["instances"]:
                    serviceInstanceString = serviceTypeSingleString + "/" + serviceInstance
                    self.createStartOfAnInstanceOfAServiceType(serviceTypeSingleString, serviceInstanceString)
                    self.createEndOfAnInstanceOfAServiceType(serviceInstanceString)
                  self.createEndOfAServiceType(serviceTypeSingleString)
            self.createEndOfAServicesSection(serviceTypesString)
      self.createEndOfASystem(systemString)
    if command == "off":
      for systemKey in system:
        if systemKey == "services":  
          serviceTypesString = systemString + "/serviceTypes"
          self.createStartOfAServicesSection(systemString, serviceTypesString)
          for serviceTypeKey in system[systemKey]:
            if serviceTypeKey == "serviceTypes":
              for serviceType in system[systemKey][serviceTypeKey]:
                serviceTypeSingleString = serviceTypesString + "/" + serviceType["type"]
                self.createStartOfAServiceType(serviceTypesString, serviceTypeSingleString)
                for serviceInstance in serviceType["instances"]:
                  serviceInstanceString = serviceTypeSingleString + "/" + serviceInstance
                  self.createStartOfAnInstanceOfAServiceType(serviceTypeSingleString, serviceInstanceString)
                  self.createEndOfAnInstanceOfAServiceType(serviceInstanceString)
                self.createEndOfAServiceType(serviceTypeSingleString)
          self.createEndOfAServicesSection(serviceTypesString)
      for systemKey in system:
        if systemKey == "foundation":
          foundationString = systemString + "/foundation"
          self.createStartOfAFoundation(systemString, foundationString)
          self.createEndOfAFoundation(foundationString)
      self.createEndOfASystem(systemString)

  #@private
  def emitChangesToLogs(self):
    lw = log_writer()
    logString = "The current status of the " + str(len(self.changesManifest)) + " changes being made in this run is: "  
    lw.writeLogVerbose("acm", logString)
    for change in self.changesManifest:
      logString = change
      lw.writeLogVerbose("acm", logString)

  #@public
  def initializeChangesManagementDataStructures(self, ct, cc, level, command):
    ct.assembleChangeTaxonomy(level, command)
    logString = " At beginning, changeTaxonomy is: " + str(ct.changeTaxonomy)
    outputLine = "[ acm ] " + logString
    ct.storeChangeTaxonomy(cc, level, outputLine)
    self.changePreview(ct, level, command)

  #@private
  def createStartOfApplianceRun(self):
    self.changeIndex = 1
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
  	"changeType":"Start of appliance run", 
      "key":"applianceStart",
      "changes": [
  	  {"affectedUnit":"appliance", "Status":"To In Process", "Step":"Same", "changeCompleted":False}
	  ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1

  #@public
  def updateStartOfApplianceRun(self, ct, cc, level, newStatus):
    lw = log_writer()
    #1 validate newStatus
    if (newStatus != "In Process") and (newStatus != "Completed"):
      logString = "ERROR: newStatus had an invalid value: " + newStatus + " .  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)
    #2 update changeTaxonomy
    ct.updateStartOfApplianceRun(newStatus)
    #3 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine)
    match = False
    for change in self.changesManifest:
      if int(change['changeIndex']) == (len(ct.changeReports)-1):
        for changeItems in cc.changesList:
          if changeItems['key'] == change['key']:
            for changeItem in changeItems['changes']:
              if "overallStatus changed from NOT Started to In Process" in changeItem:
                match = True
                #4 update change in changesManifest
                for changesBlock in self.changesManifest:
                  for changeKey in changesBlock:
                    if changeKey == "changes":
                      for change in changesBlock[changeKey]:
                        if change["affectedUnit"] == "appliance":
                          if change["Status"].replace('To ','') == newStatus:
                            change["changeCompleted"] = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if match == False:
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@private
  def createStartOfASystem(self, systemString):
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
      "changeType":"Start of a system", 
      "key":systemString,
      "changes": [
        {"affectedUnit":"appliance", "Status":"same", "Step":"+1", "changeCompleted":False},
        {"affectedUnit":systemString, "Status":"To In Process", "Step":"Same", "changeCompleted":False}
      ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1

  #@public
  def updateStartOfASystem(self, ct, cc, level, systemInstanceName, newStatus):
    lw = log_writer()
    #1 update changeTaxonomy 
    ct.updateStartOfASystem(level, systemInstanceName, newStatus)
    #2 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine)
    #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
    match1 = False
    match2 = False
    for change in self.changesManifest:
      if int(change['changeIndex']) == (len(ct.changeReports)-1):
        for changeItems in cc.changesList:
          if changeItems['key'] == change['key']:
            for changeItem in changeItems['changes']:
              if "system summary status changed from NOT Started to In Process" in changeItem:
                match1 = True
                for changeFields in change["changes"]:
                  affUnitName = "appliance/system:" + systemInstanceName
                  if changeFields['affectedUnit'] == affUnitName:
                    if changeFields["Status"].replace('To ','') == newStatus:
                      changeFields["changeCompleted"] = True
          elif changeItems["key"] == "applianceStart":
            for changeItem in changeItems['changes']:
              if "currentStep changed from" in changeItem:
                #ADD WORK ITEM TO CHECK THE SPECIFIC CURRENT STEP AND TOTAL STEPS TO COMPLEMENT THIS HIGH LEVEL CHECK.
                match2 = True
                for changeFields in change["changes"]:
                  if changeFields["affectedUnit"] == "appliance":
                    if (changeFields["Step"] == "+1") and (changeFields["Status"] == "same"):
                      if changeFields["changeCompleted"] == False:
                        changeFields["changeCompleted"] = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if (match1 == False) or (match2 == False):
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@private
  def createStartOfAFoundation(self, systemString, foundationString):
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
      "changeType":"Start of a foundation", 
      "key":systemString,
      "changes": [
        {"affectedUnit":systemString, "Status":"same", "Step":"+1", "changeCompleted":False},
        {"affectedUnit":foundationString, "Status":"To In Process", "Step":"+1", "changeCompleted":False}
      ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1

  #@public
  def updateStartOfAFoundation(self, ct, cc, level, systemInstanceName, newStatus):
    lw = log_writer()
    #1 validate newStatus
    if (newStatus != "In Process"):
      logString = "ERROR: newStatus had an invalid value: " + newStatus + " .  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)
    #2 update changeTaxonomy
    ct.updateStartOfAFoundation(systemInstanceName, newStatus)
    #3 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine)
    #4 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
    match1 = False
    match2 = False
    match3 = False
    for change in self.changesManifest:
      if int(change['changeIndex']) == (len(ct.changeReports)-1):
        for changeItems in cc.changesList:
          if changeItems['key'] == change['key']+"/foundation":
            for changeItem in changeItems['changes']:
              if "foundation status changed from NOT Started to In Process" in changeItem:
                for changeElement in change['changes']:
                  if changeElement["affectedUnit"] == "appliance/system:"+systemInstanceName+"/foundation":
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
                  if changeElement["affectedUnit"] == "appliance/system:" + systemInstanceName:
                    if changeElement["Step"] == "+1":
                      changeElement["changeCompleted"] = True
                      match3 = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if (match1 == False) or (match2 == False) or (match3 == False):
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@private
  def createEndOfAFoundation(self, foundationString):
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
      "changeType":"End of a foundation", 
      "key":foundationString,
      "changes": [
        {"affectedUnit":foundationString, "Status":"To Completed", "Step":"Same", "changeCompleted":False}
      ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1

  #@public
  def updateEndOfAFoundation(self, ct, cc, level, systemInstanceName):
    lw = log_writer()
    #1 update changeTaxonomy
    ct.updateEndOfAFoundation(systemInstanceName)
    #2 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine)
    #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
    match = False
    for change in self.changesManifest:
      if int(change['changeIndex']) == (len(ct.changeReports)-1):
        for changeItems in cc.changesList:
          if changeItems['key'] == change['key']:
            for changeItem in changeItems['changes']:
              if "foundation status changed from In Process to Completed" in changeItem:
                for changeElement in change['changes']:
                  if changeElement["affectedUnit"] == "appliance/system:"+systemInstanceName+"/foundation":
                    if "To Completed" in changeElement["Status"]:
                      changeElement["changeCompleted"] = True
                      match = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if match == False:
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@private
  def createStartOfAServicesSection(self, systemString, serviceTypesString):
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
      "changeType":"Start of a services section", 
      "key":systemString,
      "changes": [
        {"affectedUnit":systemString, "Status":"same", "Step":"+1", "changeCompleted":False},
        {"affectedUnit":serviceTypesString, "Status":"To In Process", "Step":"same", "changeCompleted":False}
      ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1

  #@public
  def updateStartOfAServicesSection(self, ct, cc, level, systemInstanceName):
    lw = log_writer()
    #1 update changeTaxonomy
    ct.updateStartOfAServicesSection(systemInstanceName)
    #2 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine) 
    #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
    match1 = False
    match2 = False
    for change in self.changesManifest:
      if change["changeType"] == "Start of a services section":
        if int(change['changeIndex']) == (len(ct.changeReports)-1):
          for changeItems in cc.changesList:
            if changeItems['key'] == change['key']:
              for changeItem in changeItems['changes']:
                if "system summary currentStep changed from" in changeItem:
                  for changeElement in change['changes']:
                    affUnitName = "appliance/system:" + systemInstanceName
                    if changeElement["affectedUnit"] == affUnitName:
                      if changeElement["Step"] == "+1":
                        changeElement["changeCompleted"] = True
                        match1 = True
            if changeItems['key'] == change['key']+"/services":
              for changeItem in changeItems['changes']:
                print('+++ changeItem is: ', changeItem)
                if "all services summary status changed from NOT Started to In Process" in changeItem:
                  for changeElement in change['changes']:
                    affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes"
                    print("+++  affUnitName is: ", affUnitName)
                    if changeElement["affectedUnit"] == affUnitName:
                      if changeElement["Status"].replace('To ','') == "In Process":
                        changeElement["changeCompleted"] = True
                        match2 = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if (match1 == False) or (match2 == False):
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@public
  def updateStartOfSkipServicesSection(self):
    lw = log_writer()
    logString = "**************************************************************************************************************"
    lw.writeLogVerbose("acm", logString)
    logString = "WARNING: All service-related objects are being marked in changesManifest and changeTaxonomy as if they are being operated on because you used the --force flag.  These objects are NOT being operated on.  Instead, we assume that you designed your systems so that these objects will be deleted when the foundation is deleted.  You must validate destruction of these objects yourself when developing your automation systems. "
    lw.writeLogVerbose("acm", logString)
    logString = "**************************************************************************************************************"
    lw.writeLogVerbose("acm", logString)

  #@public
  def updateEndOfSkipServicesSection(self):
    lw = log_writer()
    logString = "**************************************************************************************************************"
    lw.writeLogVerbose("acm", logString)
    logString = "WARNING: All service-related objects are being marked in changesManifest and changeTaxonomy as if they are being operated on because you used the --force flag.  These objects are NOT being operated on.  Instead, we assume that you designed your systems so that these objects will be deleted when the foundation is deleted.  You must validate destruction of these objects yourself when developing your automation systems. "
    lw.writeLogVerbose("acm", logString)
    logString = "**************************************************************************************************************"
    lw.writeLogVerbose("acm", logString)

  #@private
  def createStartOfAServiceType(self, serviceTypesString, serviceTypeSingleString):
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
      "changeType":"Start of a serviceType", 
      "key":serviceTypesString,
      "changes": [
        {"affectedUnit":serviceTypesString, "Status":"same", "Step":"+1", "changeCompleted":False},
        {"affectedUnit":serviceTypeSingleString, "Status":"To In Process", "Step":"same", "changeCompleted":False}
      ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1

  #@public
  def updateStartOfAServiceType(self, ct, cc, level, systemInstanceName, typeName):
    lw = log_writer()
    #1 update changeTaxonomy
    ct.updateStartOfAServiceType(systemInstanceName, typeName)
    #2 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine)
    #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
    match1 = False
    match2 = False
    #2 update change in changesManifest
    for changesBlock in self.changesManifest:
      if changesBlock["changeType"] == "Start of a serviceType":
        if int(changesBlock['changeIndex']) == (len(ct.changeReports)-1):
          for changeItems in cc.changesList:
            if (changeItems['key'] == "appliance/system:"+systemInstanceName+"/services") and (changesBlock['key'] == "appliance/system:"+systemInstanceName+"/serviceTypes"):
              for changeItem in changeItems['changes']:
                if "all services summary currentStep changed from" in changeItem:
                  for changeElement in changesBlock['changes']:
                    affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes"
                    if changeElement["affectedUnit"] == affUnitName:
                      if changeElement["Step"] == "+1":
                        changeElement["changeCompleted"] = True
                        match1 = True
            if (changeItems['key'] == "appliance/system:"+systemInstanceName+"/serviceTypes/"+typeName) and (changesBlock['key'] == "appliance/system:"+systemInstanceName+"/serviceTypes"):
              for changeItem in changeItems['changes']:
                if (typeName) in changeItem:
                  if " summary status changed from" in changeItem:
                    for changeElement in changesBlock['changes']:
                      affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes/" + typeName
                      if changeElement["affectedUnit"] == affUnitName:
                        if changeElement["Status"].replace('To ','') == "In Process":
                          changeElement["changeCompleted"] = True
                          match2 = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if (match1 == False) or (match2 == False):
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@private
  def createStartOfAnInstanceOfAServiceType(self, serviceTypeSingleString, serviceInstanceString):
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
      "changeType":"Start of an instance of a serviceType", 
      "key":serviceTypeSingleString,
      "changes": [
        {"affectedUnit":serviceTypeSingleString, "Status":"same", "Step":"+1", "changeCompleted":False},
        {"affectedUnit":serviceInstanceString, "Status":"To In Process", "Step":"+1", "changeCompleted":False}
      ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1

  #@public
  def updateStartOfAnInstanceOfAServiceType(self, ct, cc, level, systemInstanceName, typeName, instanceName):
    lw = log_writer()
    #1 update changeTaxonomy
    ct.updateStartOfAnInstanceOfAServiceType(systemInstanceName, typeName, instanceName)
    #2 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine)
    #2 update change in changesManifest
    #First get changeIndex in order to make sure this only runs the intended number of times.
    chgIdx = "-1"
    for changesBlock in self.changesManifest:
      for changeKey in changesBlock:
        if changeKey == "changes":
          for change in changesBlock[changeKey]:
            affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes/" + typeName + "/" + instanceName
            if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "In Process"):
              chgIdx = changesBlock["changeIndex"]
    #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
    match1 = False
    match2 = False
    #2 update change in changesManifest
    for changesBlock in self.changesManifest:
      if changesBlock["changeIndex"] == chgIdx:
        if changesBlock["changeType"] == "Start of an instance of a serviceType":
          if int(changesBlock['changeIndex']) == (len(ct.changeReports)-1):
            for changeItems in cc.changesList:
              if changeItems['key'] == "appliance/system:"+systemInstanceName+"/serviceTypes/"+typeName: #) and (changesBlock['key'] == "appliance/system:"+systemInstanceName+"/serviceTypes"):
                for changeItem in changeItems['changes']:
                  if typeName+" summary currentStep changed from " in changeItem:
                    for changeElement in changesBlock['changes']:
                      affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes/" + typeName
                      if changeElement["affectedUnit"] == affUnitName:
                        if changeElement["Step"] == "+1":
                          changeElement["changeCompleted"] = True
                          match1 = True
                      affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes/" + typeName + "/" + instanceName
                      if (changeElement["affectedUnit"] == affUnitName) and (changeElement["Step"] == "+1") and (changeElement["Status"].replace('To ','') == "In Process"):
                        changeElement["changeCompleted"] = True
                        match2 = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if (match1 == False) or (match2 == False):
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@private
  def createEndOfAnInstanceOfAServiceType(self, serviceInstanceString):
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
      "changeType":"End of an instance of a serviceType", 
      "key":serviceInstanceString,
      "changes": [
        {"affectedUnit":serviceInstanceString, "Status":"To Completed", "Step":"same", "changeCompleted":False}
      ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1

  #@public
  def updateEndOfAnInstanceOfAServiceType(self, ct, cc, level, systemInstanceName, typeName, instanceName):
    lw = log_writer()
    #1 update changeTaxonomy
    ct.updateEndOfAnInstanceOfAServiceType(systemInstanceName, typeName, instanceName)
    #2 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine)
    #2 update change in changesManifest
    #First get changeIndex in order to make sure this only runs the intended number of times.
    chgIdx = "-1"
    for changesBlock in self.changesManifest:
      for changeKey in changesBlock:
        if changeKey == "changes":
          for change in changesBlock[changeKey]:
            affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes/" + typeName + "/" + instanceName
            if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "Completed"):
              chgIdx = changesBlock["changeIndex"]
    #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
    match = False
    #2 update change in changesManifest
    for changesBlock in self.changesManifest:
      if changesBlock["changeIndex"] == chgIdx:
        if changesBlock["changeType"] == "End of an instance of a serviceType":
          if int(changesBlock['changeIndex']) == (len(ct.changeReports)-1):
            for changeItems in cc.changesList:
              if changeItems['key'] == "appliance/system:"+systemInstanceName+"/serviceTypes/"+typeName+"/"+instanceName: 
                for changeItem in changeItems['changes']:
                  if instanceName +" summary status changed from In Process to Completed" in changeItem:
                    for changeElement in changesBlock['changes']:
                      affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes/" + typeName + "/" + instanceName
                      if (changeElement["affectedUnit"] == affUnitName) and (changeElement["Step"] == "same") and (changeElement["Status"].replace('To ','') == "Completed"):
                        changeElement["changeCompleted"] = True
                        match = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if match == False:
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@private
  def createEndOfAServiceType(self, serviceTypeSingleString):
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
      "changeType":"End of a serviceType", 
      "key":serviceTypeSingleString,
      "changes": [
        {"affectedUnit":serviceTypeSingleString, "Status":"To Completed", "Step":"same", "changeCompleted":False}
      ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1

  #@public
  def updateEndOfAServiceType(self, ct, cc, level, systemInstanceName, typeName):
    lw = log_writer()
    #1 update changeTaxonomy
    ct.updateEndOfAServiceType(systemInstanceName, typeName)
    #2 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine)
    #2 update change in changesManifest
    #First get changeIndex in order to make sure this only runs the intended number of times.
    chgIdx = "-1"
    for changesBlock in self.changesManifest:
      for changeKey in changesBlock:
        if changeKey == "changes":
          for change in changesBlock[changeKey]:
            affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes/" + typeName
            if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "Completed"):
              chgIdx = changesBlock["changeIndex"]
    #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
    match = False
    #2 update change in changesManifest
    for changesBlock in self.changesManifest:
      if changesBlock["changeIndex"] == chgIdx:
        if changesBlock["changeType"] == "End of a serviceType":
          if int(changesBlock['changeIndex']) == (len(ct.changeReports)-1):
            for changeItems in cc.changesList:
              if changeItems['key'] == "appliance/system:"+systemInstanceName+"/serviceTypes/"+typeName: 
                for changeItem in changeItems['changes']:
                  if typeName +" summary status changed from In Process to Completed" in changeItem:
                    for changeElement in changesBlock['changes']:
                      affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes/" + typeName
                      if changeElement["affectedUnit"] == affUnitName:
                        if changeElement["Status"].replace('To ','') == "Completed":
                          changeElement["changeCompleted"] = True
                          match = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if match == False:
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@private
  def createEndOfAServicesSection(self, serviceTypesString):
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
      "changeType":"End of a services section", 
      "key":serviceTypesString,
      "changes": [
        {"affectedUnit":serviceTypesString, "Status":"To Completed", "Step":"same", "changeCompleted":False}
      ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1
 
  #@public
  def updateEndOfAServicesSection(self, ct, cc, level, systemInstanceName):
    lw = log_writer()
    #1 update changeTaxonomy
    ct.updateEndOfAServicesSection(systemInstanceName)
    #2 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine)
    #2 update change in changesManifest
    #First get changeIndex in order to make sure this only runs the intended number of times.
    chgIdx = "-1"
    for changesBlock in self.changesManifest:
      for changeKey in changesBlock:
        if changeKey == "changes":
          for change in changesBlock[changeKey]:
            affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes"
            if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "Completed"):
              chgIdx = changesBlock["changeIndex"]
    #3 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
    match = False
    #2 update change in changesManifest
    for changesBlock in self.changesManifest:
      if changesBlock["changeIndex"] == chgIdx:
        if changesBlock["changeType"] == "End of a services section":
          if int(changesBlock['changeIndex']) == (len(ct.changeReports)-1):
            for changeItems in cc.changesList:
              if changeItems['key'] == "appliance/system:"+systemInstanceName+"/services": 
                for changeItem in changeItems['changes']:
                  if "all services summary status changed from In Process to Completed" in changeItem:
                    for changeElement in changesBlock['changes']:
                      affUnitName = "appliance/system:" + systemInstanceName + "/serviceTypes"
                      if changeElement['affectedUnit'] == affUnitName:
                        if changeElement["Status"].replace('To ','') == "Completed":
                          changeElement["changeCompleted"] = True
                          match = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if match == False:
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@private
  def createEndOfASystem(self, systemString):
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
      "changeType":"End of a system", 
      "key":systemString,
      "changes": [
        {"affectedUnit":systemString, "Status":"To Completed", "Step":"Same", "changeCompleted":False}
      ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1

  #@public
  def updateEndOfASystem(self, ct, cc, level, systemInstanceName):
    lw = log_writer()
    #1 update changeTaxonomy
    ct.updateEndOfASystem(systemInstanceName)
    #2 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine)
    #3 update change in changesManifest
    #First get changeIndex in order to make sure this only runs the intended number of times.
    chgIdx = "-1"
    for changesBlock in self.changesManifest:
      for changeKey in changesBlock:
        if changeKey == "changes":
          for change in changesBlock[changeKey]:
            affUnitName = "appliance/system:" + systemInstanceName
            if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "Completed"):
              chgIdx = changesBlock["changeIndex"]
    #4 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
    match = False
    #5 update change in changesManifest
    for changesBlock in self.changesManifest:
      if changesBlock["changeIndex"] == chgIdx:
        if changesBlock["changeType"] == "End of a system":
          if int(changesBlock['changeIndex']) == (len(ct.changeReports)-1):
            for changeItems in cc.changesList:
              if changeItems['key'] == "appliance/system:"+systemInstanceName: 
                for changeItem in changeItems['changes']:
                  if "system summary status changed from In Process to Completed" in changeItem:
                    for changeElement in changesBlock['changes']:
                      affUnitName = "appliance/system:" + systemInstanceName
                      if changeElement["affectedUnit"] == affUnitName:
                        if changeElement["Status"].replace('To ','') == "Completed":
                          changeElement["changeCompleted"] = True
                          match = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if match == False:
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@private
  def createEndOfApplianceRun(self):
    changeSummaryDict = {
      "changeIndex":self.changeIndex, 
      "changeType":"End of appliance run", 
      "key":"applianceEnd",
      "changes": [
  	  {"affectedUnit":"appliance", "Status":"To Completed", "Step":"Same", "changeCompleted":False}
	  ]
    }
    self.changesManifest.append(changeSummaryDict)
    self.changeIndex += 1

  #@public
  def updateEndOfApplianceRun(self, ct, cc, level):
    lw = log_writer()
    #1 update changeTaxonomy
    ct.updateEndOfApplianceRun()
    #2 get list of changes in new changeTaxonomy
    outputLine = "[ acm ] " + " After update, changeTaxonomy is: " + str(ct.changeTaxonomy)
    ct.storeChangeTaxonomy(cc, level, outputLine)
    #3 update change in changesManifest
    #First get changeIndex in order to make sure this only runs the intended number of times.
    chgIdx = "-1"
    for changesBlock in self.changesManifest:
      for changeKey in changesBlock:
        if changeKey == "changes":
          for change in changesBlock[changeKey]:
            affUnitName = "appliance"
            if (change["affectedUnit"] == affUnitName) and (change["Status"].replace('To ','') == "Completed"):
              chgIdx = changesBlock["changeIndex"]
    #4 update changes in changesManifest if and only if the required changes have been reported by the call to storeChangeTaxonomy()
    match = False
    #5 update change in changesManifest
    for changesBlock in self.changesManifest:
      if changesBlock["changeIndex"] == chgIdx:
        if changesBlock["changeType"] == "End of appliance run":
          if int(changesBlock['changeIndex']) == (len(ct.changeReports)-1):
            for changeItems in cc.changesList:
              if changeItems['key'] == "applianceEnd": 
                for changeItem in changeItems['changes']:
                  if "overallStatus changed from In Process to Completed" in changeItem:
                    for changeElement in changesBlock['changes']:
                      if changeElement["affectedUnit"] == "appliance":  
                        if changeElement["Status"].replace('To ','') == "Completed":  
                          changeElement["changeCompleted"] = True  
                          match = True
    self.validateChangeManifest((len(ct.changeReports)-1))
    self.emitChangesToLogs()
    if match == False:
      logString = "ERROR: Change Failed.  Halting program so you can find the source of the error.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

  #@private
  def validateChangeManifest(self, index):
    lw = log_writer()
    for changesBlock in self.changesManifest:
      for changeKey in changesBlock:
        # Must be True before and including current index
        if int(changesBlock['changeIndex']) > index:
          if changeKey == "changes":
            for change in changesBlock[changeKey]:
              if change["changeCompleted"] == True:
                print('index is: ', index)
                print('changesBlock[changeKey] is: ', changesBlock[changeKey])
                print('change is: ', change)
                logString = "ERROR: Change Manifest shows a true flag that should be false.  Post an issue on our github site so we can examine what went wrong.  "
                lw.writeLogVerbose("acm", logString)
                exit(1)
        #Must be False after current index
        if int(changesBlock['changeIndex']) <= index:
          if changeKey == "changes":
            for change in changesBlock[changeKey]:
              if change["changeCompleted"] == False:
                print("...   for debugging: changesBlock[changeKey] is: ", changesBlock[changeKey])
                print("...   for debugging: change is: ", change)
                print("...   for debugging: changesBlock['changeIndex'] is: ", changesBlock['changeIndex'])
                print('...   for debugging: index is: ', index)
                logString = "ERROR: Change Manifest shows a false flag that should be true.  Post an issue on our github site so we can examine what caused this.  "
                lw.writeLogVerbose("acm", logString)
                exit(1)

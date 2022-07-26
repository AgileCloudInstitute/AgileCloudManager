## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

from config_fileprocessor import config_fileprocessor
from workflow_system import workflow_system
from log_writer import log_writer
from changes_manifest import changes_manifest
from changes_taxonomy import changes_taxonomy
from changes_comparer import changes_comparer
import config_cliprocessor

class workflow_platform:
  
  def __init__(self):  
    pass
 
  #@public
  def onPlatform(self):
    wfsys = workflow_system()
    cfp = config_fileprocessor()
    cm_on = changes_manifest()
    ct_on = changes_taxonomy()
    cc_on = changes_comparer()
    lw = log_writer()
    command = 'on'
    test = config_cliprocessor.inputVars.get("test")
    typeOfTest = config_cliprocessor.inputVars.get("testType")
    yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    platformConfig = cfp.getPlatformConfig(yamlPlatformConfigFileAndPath)
    print('............................. 1 len(ct_on.changeReports) is: ', len(ct_on.changeReports))
    cm_on.initializeChangesManagementDataStructures(ct_on, cc_on, 'platform', command)
    print('............................. 2 len(ct_on.changeReports) is: ', len(ct_on.changeReports))
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_on.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    print('............................. 3 len(ct_on.changeReports) is: ', len(ct_on.changeReports))
    cm_on.updateStartOfPlatformRun(ct_on, cc_on, 'platform', "In Process")
    print('............................. 4 len(ct_on.changeReports) is: ', len(ct_on.changeReports))
    for systemInstanceName in platformConfig:
      cm_on.updateStartOfASystem(ct_on, cc_on, 'platform', systemInstanceName, "In Process")
      if cfp.systemHasFoundation(platformConfig.get(systemInstanceName)):
        cm_on.updateStartOfAFoundation(ct_on, cc_on, 'platform', systemInstanceName, "In Process")
        wfsys.onFoundation(systemInstanceName, platformConfig.get(systemInstanceName))
        cm_on.updateEndOfAFoundation(ct_on, cc_on, 'platform', systemInstanceName)
      else:
        logString = "WARNING: There is NOT any foundation block defined for the system named " + systemInstanceName + " in your acm.yaml file.  The program is continuing in case you are launching something that does not need a Foundation.  If your configuration requires a foundation, then a downstream error will occur unless you add a foundation block. "
        lw.writeLogVerbose("acm", logString)
      logString = "------------------ DONE WITH onFoundation() -------------------"
      lw.writeLogVerbose("acm", logString)
      cm_on.updateStartOfAServicesSection(ct_on, cc_on, 'platform', systemInstanceName)
      wfsys.onServices(cm_on, ct_on, cc_on, 'platform', systemInstanceName, platformConfig.get(systemInstanceName))
      cm_on.updateEndOfAServicesSection(ct_on, cc_on, 'platform', systemInstanceName)
      cm_on.updateEndOfASystem(ct_on, cc_on, 'platform', systemInstanceName)
      if (test==True) and (typeOfTest=="workflow"):
        print("stub test q stuff goes here.")
      logString = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
      lw.writeLogVerbose("acm", logString)
      lw.writeLogVerbose("acm", logString)
      lw.writeLogVerbose("acm", logString)
      logString = "+++++++++++++++ DONE WITH " + systemInstanceName + " SYSTEM. +++++++++++"
      lw.writeLogVerbose("acm", logString)
      logString = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
      lw.writeLogVerbose("acm", logString)
      lw.writeLogVerbose("acm", logString)
      lw.writeLogVerbose("acm", logString)
    cm_on.updateEndOfPlatformRun(ct_on, cc_on, 'platform')

  #@public
  def offPlatform(self):
    wfsys = workflow_system()
    cfp = config_fileprocessor()
    cm_off = changes_manifest()
    ct_off = changes_taxonomy()
    cc_off = changes_comparer()
    lw = log_writer()
    test = config_cliprocessor.inputVars.get("test")
    typeOfTest = config_cliprocessor.inputVars.get("testType")
    yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    platformConfig = cfp.getPlatformConfig(yamlPlatformConfigFileAndPath)
    systemInstanceNames = cfp.getSystemNames(platformConfig)
    cm_off.initializeChangesManagementDataStructures(ct_off, cc_off, 'platform', "off")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_off.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    cm_off.updateStartOfPlatformRun(ct_off, cc_off, 'platform', "In Process")
    for systemInstanceName in reversed(systemInstanceNames):
      useTheForce = platformConfig.get(systemInstanceName).get("forceDelete")
      cm_off.updateStartOfASystem(ct_off, cc_off, 'platform', systemInstanceName, "In Process")
      hasFoundation = cfp.systemHasFoundation(platformConfig.get(systemInstanceName))
      if (useTheForce == True) and (hasFoundation):
        quit("DEBUG has foundation in workflow_platform.py")
        cm_off.updateStartOfSkipServicesSection()
        cm_off.updateStartOfAServicesSection('platform', systemInstanceName)
        print("test and typeOfTest are: ", test, " ", typeOfTest)
        wfsys.skipServices('platform', systemInstanceName, yaml_infra_config_file_and_path)
        cm_off.updateEndOfAServicesSection('platform', systemInstanceName)
        cm_off.updateEndOfSkipServicesSection()
      else:
        cm_off.updateStartOfAServicesSection(ct_off, cc_off, 'platform', systemInstanceName)
        wfsys.offServices(cm_off, ct_off, cc_off, 'platform', systemInstanceName, platformConfig.get(systemInstanceName))
        cm_off.updateEndOfAServicesSection(ct_off, cc_off, 'platform', systemInstanceName)
        logString = "------------------ DONE WITH offServices() -------------------"
        lw.writeLogVerbose("acm", logString)
      if hasFoundation:
        cm_off.updateStartOfAFoundation(ct_off, cc_off, 'platform', systemInstanceName, "In Process")
        if (test==True) and (typeOfTest=="workflow"):
          pass
        else:
          wfsys.offFoundation(systemInstanceName, platformConfig.get(systemInstanceName))
        cm_off.updateEndOfAFoundation(ct_off, cc_off, 'platform', systemInstanceName)
      else:
        logString = "WARNING: There is NOT any foundation block in system named " + systemInstanceName + " .  The program is continuing in case you are launching a SaaS that does not need a Foundation.  If your configuration requires a foundation, then a downstream error will occur unless you add a foundation block. "
        lw.writeLogVerbose("acm", logString)
        if useTheForce == True:
          logString = "WARNING: YOU MUST VALIDATE WHAT IF ANYTHING HAPPENED with " + systemInstanceName + " because the --force flag works by deleting a foundation which will only delete system contents if all the system contents are bundled within the foundation's child objects by the cloud provider. Since your configuration does not include a foundation, the only things that happened might have been special cases defined in the documentation.  In order to make best use of the --force flag, you must write your configuration properly and validate your results in lower environments. "
          lw.writeLogVerbose("acm", logString)
      logString = "------------------ DONE WITH offFoundation() -------------------"
      lw.writeLogVerbose("acm", logString)
      cm_off.updateEndOfASystem(ct_off, cc_off, 'platform', systemInstanceName)
      logString = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
      lw.writeLogVerbose("acm", logString)
      lw.writeLogVerbose("acm", logString)
      lw.writeLogVerbose("acm", logString)
      logString = "+++++++++++++++ DONE WITH " + systemInstanceName + " SYSTEM. +++++++++++"
      lw.writeLogVerbose("acm", logString)
      logString = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
      lw.writeLogVerbose("acm", logString)
      lw.writeLogVerbose("acm", logString)
      lw.writeLogVerbose("acm", logString)
    cm_off.updateEndOfPlatformRun(ct_off, cc_off, 'platform')

## Copyright 2023 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

from config_fileprocessor import config_fileprocessor
from workflow_system import workflow_system
from log_writer import log_writer
from changes_manifest import changes_manifest
from changes_taxonomy import changes_taxonomy
from changes_comparer import changes_comparer

import sys

class workflow_appliance:
  
  def __init__(self):  
    pass
 
  #@public
  def onAppliance(self):
    import config_cliprocessor
    wfsys = workflow_system()
    cfp = config_fileprocessor()
    cm_on = changes_manifest()
    ct_on = changes_taxonomy()
    cc_on = changes_comparer()
    lw = log_writer()
    command = 'on'
    test = config_cliprocessor.inputVars.get("test")
    typeOfTest = config_cliprocessor.inputVars.get("testType")
    yamlApplianceConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    applianceConfig = cfp.getApplianceConfig(yamlApplianceConfigFileAndPath)
    cm_on.initializeChangesManagementDataStructures(ct_on, cc_on, 'appliance', command)
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_on.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    cm_on.updateStartOfApplianceRun(ct_on, cc_on, 'appliance', "In Process")
    for systemInstanceName in applianceConfig:
      cm_on.updateStartOfASystem(ct_on, cc_on, 'appliance', systemInstanceName, "In Process")
      sysCfg = cfp.getSystemConfig(applianceConfig, systemInstanceName)
      if cfp.systemHasFoundation(sysCfg):
        cm_on.updateStartOfAFoundation(ct_on, cc_on, 'appliance', systemInstanceName, "In Process")
        wfsys.onFoundation(systemInstanceName, sysCfg)
        cm_on.updateEndOfAFoundation(ct_on, cc_on, 'appliance', systemInstanceName)
      else:
        logString = "WARNING: There is NOT any foundation block defined for the system named " + systemInstanceName + " in your acm.yaml file.  The program is continuing in case you are launching something that does not need a Foundation.  If your configuration requires a foundation, then a downstream error will occur unless you add a foundation block. "
        lw.writeLogVerbose("acm", logString)
      logString = "------------------ DONE WITH onFoundation() -------------------"
      lw.writeLogVerbose("acm", logString)
      cm_on.updateStartOfAServicesSection(ct_on, cc_on, 'appliance', systemInstanceName)
      wfsys.onServices(cm_on, ct_on, cc_on, 'appliance', systemInstanceName, sysCfg)
      cm_on.updateEndOfAServicesSection(ct_on, cc_on, 'appliance', systemInstanceName)
      cm_on.updateEndOfASystem(ct_on, cc_on, 'appliance', systemInstanceName)
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
    cm_on.updateEndOfApplianceRun(ct_on, cc_on, 'appliance')

  #@public
  def offAppliance(self):
    import config_cliprocessor
    wfsys = workflow_system()
    cfp = config_fileprocessor()
    cm_off = changes_manifest()
    ct_off = changes_taxonomy()
    cc_off = changes_comparer()
    lw = log_writer()
    test = config_cliprocessor.inputVars.get("test")
    typeOfTest = config_cliprocessor.inputVars.get("testType")
    yamlApplianceConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    applianceConfig = cfp.getApplianceConfig(yamlApplianceConfigFileAndPath)
    systemInstanceNames = cfp.getSystemNames(applianceConfig)
    cm_off.initializeChangesManagementDataStructures(ct_off, cc_off, 'appliance', "off")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_off.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    cm_off.updateStartOfApplianceRun(ct_off, cc_off, 'appliance', "In Process")
    for systemInstanceName in reversed(systemInstanceNames):
      sysCfg = cfp.getSystemConfig(applianceConfig, systemInstanceName)
      useTheForce = sysCfg.get("forceDelete")
      cm_off.updateStartOfASystem(ct_off, cc_off, 'appliance', systemInstanceName, "In Process")
      hasFoundation = cfp.systemHasFoundation(sysCfg)
      if (useTheForce == True) and (hasFoundation):
        print("DEBUG has foundation in workflow_appliance.py")
        sys.exit(1)
        cm_off.updateStartOfSkipServicesSection()
        cm_off.updateStartOfAServicesSection('appliance', systemInstanceName)
        print("test and typeOfTest are: ", test, " ", typeOfTest)
        wfsys.skipServices('appliance', systemInstanceName, yaml_infra_config_file_and_path)
        cm_off.updateEndOfAServicesSection('appliance', systemInstanceName)
        cm_off.updateEndOfSkipServicesSection()
      else:
        cm_off.updateStartOfAServicesSection(ct_off, cc_off, 'appliance', systemInstanceName)
        wfsys.offServices(cm_off, ct_off, cc_off, 'appliance', systemInstanceName, sysCfg)
        cm_off.updateEndOfAServicesSection(ct_off, cc_off, 'appliance', systemInstanceName)
        logString = "------------------ DONE WITH offServices() -------------------"
        lw.writeLogVerbose("acm", logString)
      if hasFoundation:
        cm_off.updateStartOfAFoundation(ct_off, cc_off, 'appliance', systemInstanceName, "In Process")
        if (test==True) and (typeOfTest=="workflow"):
          pass
        else:
          wfsys.offFoundation(systemInstanceName, sysCfg)
        cm_off.updateEndOfAFoundation(ct_off, cc_off, 'appliance', systemInstanceName)
      else:
        logString = "WARNING: There is NOT any foundation block in system named " + systemInstanceName + " .  The program is continuing in case you are launching a SaaS that does not need a Foundation.  If your configuration requires a foundation, then a downstream error will occur unless you add a foundation block. "
        lw.writeLogVerbose("acm", logString)
        if useTheForce == True:
          logString = "WARNING: YOU MUST VALIDATE WHAT IF ANYTHING HAPPENED with " + systemInstanceName + " because the --force flag works by deleting a foundation which will only delete system contents if all the system contents are bundled within the foundation's child objects by the cloud provider. Since your configuration does not include a foundation, the only things that happened might have been special cases defined in the documentation.  In order to make best use of the --force flag, you must write your configuration properly and validate your results in lower environments. "
          lw.writeLogVerbose("acm", logString)
      logString = "------------------ DONE WITH offFoundation() -------------------"
      lw.writeLogVerbose("acm", logString)
      cm_off.updateEndOfASystem(ct_off, cc_off, 'appliance', systemInstanceName)
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
    cm_off.updateEndOfApplianceRun(ct_off, cc_off, 'appliance')
 
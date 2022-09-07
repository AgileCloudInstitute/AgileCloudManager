## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import sys
import shutil

from command_runner import command_runner
from controller_custom import controller_custom
from controller_terraform import controller_terraform
from controller_image import controller_image
from controller_arm import controller_arm
from controller_cf import controller_cf
from log_writer import log_writer
from config_keysassembler import config_keysassembler
from config_fileprocessor import config_fileprocessor
from changes_manifest import changes_manifest
from changes_taxonomy import changes_taxonomy
from changes_comparer import changes_comparer
from workflow_service_type import workflow_service_type

class workflow_system:
  
  def __init__(self):  
    pass
 
  #@public
  def onFoundation(self, systemInstanceName, systemConfig):
    import config_cliprocessor
    test = config_cliprocessor.inputVars.get("test")
    typeOfTest = config_cliprocessor.inputVars.get("testType")
    cr = command_runner()
    cfp = config_fileprocessor()
    ccf = controller_cf()
    ctf = controller_terraform()
    carm = controller_arm()
    cimg = controller_image()
    lw = log_writer()
    keyDir = cfp.getKeyDir(systemConfig)
    foundationInstanceName = systemConfig.get("foundation").get("instanceName")
    foundationTool = systemConfig.get("foundation").get("controller")
    operation = 'on'
    print('test is: ', test)
    print('typeOfTest is: ', typeOfTest )
#    quit('ss ---  yuio')
    if (test==True) and (typeOfTest=="workflow"):
      # Skip the else block in this case because we are just testing the workflow.
      pass
    else:
      if "preprocessor" in systemConfig.get("foundation").keys():
        preprocessor = systemConfig.get("foundation").get("preprocessor")
        cr.runPreOrPostProcessor(preprocessor, 'on')
      else:
        logString = 'NO preprocessor present.'
        lw.writeLogVerbose("acm", logString)
        pass
      if foundationTool == 'arm': 
        carm.createDeployment(systemConfig, systemConfig.get("foundation"), 'networkFoundation', 'networkFoundation', False)
      elif foundationTool == 'cloudformation':
        ccf.createStack(systemConfig, systemConfig.get("foundation"), keyDir, 'networkFoundation', None, foundationInstanceName)
        if "images" in systemConfig.get("foundation").keys():
          cimg.buildImages(systemConfig, keyDir)
        else:
          logString = "WARNING: This network foundation does not have any image builds associated with it.  If you intend not to build images in this network, then everything is fine.  But if you do want to build images with this network, then check your configuration and re-run this command.  "
          lw.writeLogVerbose("acm", logString)
      elif foundationTool =='terraform':
#        ctf.terraformCrudOperation(operation, systemInstanceName, keyDir, systemConfig, None, 'none', None, None, None) 
        ctf.terraformCrudOperation(operation, keyDir, systemConfig, None, 'none', 'networkFoundation', None, None) 
#            terraformCrudOperation(operation, keyDir, systemConfig, instance, typeParent, typeName, typeGrandChild, typeInstanceName)

        if ctf.terraformResult == "Applied": 
          if "images" in systemConfig.get("foundation").keys():
            cimg.buildImages(systemConfig, keyDir)
          else: 
            logString = "WARNING: This network foundation does not have any image builds associated with it.  If you intend not to build images in this network, then everything is fine.  But if you do want to build images with this network, then check your configuration and re-run this command.  "
            lw.writeLogVerbose("acm", logString)
        else:
          logString = "Foundation apply failed for " + systemInstanceName
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
      elif foundationTool.startswith("$customController."):
        controllerPath = foundationTool.replace("$customController.","")
        controllerCommand = systemConfig.get("foundation").get("controllerCommand")
        mappedVariables = systemConfig.get("foundation").get("mappedVariables")
        serviceType = None
        instance = systemConfig.get("foundation")
        ccust = controller_custom()
        ccust.runCustomController('on', systemConfig, controllerPath, controllerCommand, mappedVariables, serviceType, instance)
        if "images" in systemConfig.get("foundation").keys():
          cimg.buildImages(systemConfig, keyDir)
        else:
          logString = "WARNING: This network foundation does not have any image builds associated with it.  If you intend not to build images in this network, then everything is fine.  But if you do want to build images with this network, then check your configuration and re-run this command.  "
          lw.writeLogVerbose("acm", logString)
      else:
        logString = "The following value for foundationTool from your systemConfig is not supported: " + foundationTool
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
      if "postprocessor" in systemConfig.get("foundation").keys():
        postprocessor = systemConfig.get("foundation").get('postprocessor')
        cr.runPreOrPostProcessor(postprocessor, 'on')
      else:
        logString = 'NO postprocessor present.'
        lw.writeLogVerbose("acm", logString)
        pass

  #@public
  def offFoundation(self, systemInstanceName, systemConfig):
    import config_cliprocessor
    test = config_cliprocessor.inputVars.get("test")
    typeOfTest = config_cliprocessor.inputVars.get("testType")
    cr = command_runner()
    cfp = config_fileprocessor()
    ccf = controller_cf()
    ctf = controller_terraform()
    carm = controller_arm()
    lw = log_writer()
    keyDir = cfp.getKeyDir(systemConfig)
    if (test==True) and (typeOfTest=="workflow"):
      # Skip the else block in this case because we are just testing the workflow.
      pass
    else:
      if "preprocessor" in systemConfig.get("foundation").keys():
        preprocessor = systemConfig.get("foundation").get("preprocessor")
        cr.runPreOrPostProcessor(preprocessor, 'off')
      else:
        logString = 'NO preprocessor present.'
        lw.writeLogVerbose("acm", logString)
        pass
      #add code to confirm that output operation succeeded.
      #Also, if output showed there is no network foundation, then skip the rest of the off operations because there would be nothing to off in that case.
      #ADD LOGIC HERE TO PREPARE BEFORE DELETING THE FOUNDATION 
      ##########################################################################################
      ### off the Network Foundation and the Instance of the Call To The Foundation Module
      ##########################################################################################
      foundationTool = systemConfig.get("foundation").get("controller")
      operation = 'off'
      if foundationTool == 'arm':
        carm.destroyDeployment(systemConfig, systemConfig.get('foundation'), 'networkFoundation')
      elif foundationTool == 'cloudformation':
        ccf.destroyStack(systemConfig, systemConfig.get("foundation"), keyDir, 'networkFoundation')
      elif foundationTool == 'terraform':
#        ctf.terraformCrudOperation(operation, systemInstanceName, keyDir, systemConfig, None, 'none', None, None, None)
        ctf.terraformCrudOperation(operation, keyDir, systemConfig, None, 'none', 'networkFoundation', None, None)
        if ctf.terraformResult == "Destroyed": 
          logString = "off operation succeeded.  Now inside Python conditional block to do only after the off operation has succeeded. "
          lw.writeLogVerbose("acm", logString)
        else:
          logString = "Error: offFoundation operation failed.  "
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
      elif foundationTool.startswith('$customController.'):
        controllerPath = foundationTool.replace("$customController.","")
        controllerCommand = systemConfig.get("foundation").get("controllerCommand")
        mappedVariables = systemConfig.get("foundation").get("mappedVariables")
        serviceType = None
#        instance = None
        instance = systemConfig.get("foundation")
        ccust = controller_custom()
        ccust.runCustomController('off', systemConfig, controllerPath, controllerCommand, mappedVariables, serviceType, instance)
      else:
        logString = "The following value for foundationTool from your systemConfig is not supported: " + foundationTool
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
      if "postprocessor" in systemConfig.get("foundation").keys():
        postprocessor = systemConfig.get("foundation").get('postprocessor')
        cr.runPreOrPostProcessor(postprocessor, 'off')
      else:
        logString = 'NO postprocessor present.'
        lw.writeLogVerbose("acm", logString)
        pass
 
  #@public
  def onServices(self, cm, ct, cc, level, systemInstanceName, systemConfig):
    wst_on = workflow_service_type()
    typesToCreate = systemConfig.get("serviceTypes")
    for serviceType in typesToCreate:
      if (serviceType != "networkFoundation") and (serviceType != "subnetForBuilds") and (serviceType != "images"): #Make work item to check if this check for these 3 service types is still necessary.
        wst_on.onServiceType(cm, ct, cc, level, systemInstanceName, systemConfig, serviceType, typesToCreate)

  #@private
  def checkDestroyType(self, typeName, typesToDestroy):
    for serviceType in typesToDestroy:
      if typeName in serviceType:
        return True
    return False

  #@public
  def offServices(self, cm, ct, cc, level, systemInstanceName, systemConfig):
    wfst_off = workflow_service_type()
    lw = log_writer()
    #NOTE: The foundation for releaseDefinitions needs to be an controller_azdoproject in order for forcing deletion of a releaseDefinition
    typesToDestroy = dict(systemConfig.get("serviceTypes"))
    isTfBackend = self.checkDestroyType('tfBackend', typesToDestroy)
    isReleaseDef = self.checkDestroyType('releaseDefinitions', typesToDestroy)
    useTheForce = systemConfig.get("forceDelete") 
    if isTfBackend == True:
      if not useTheForce:
        logString = "Halting program because we are leaving the destruction of terraform backends to be a manual step in the UI portal in order to protect your data. "
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    elif (isReleaseDef == True):
      if useTheForce:
        if self.checkDestroyType('projects', typesToDestroy):
          typesToDestroy.pop('releaseDefinitions')
          logString = "WARNING:  ACM removed the releaseDefinitions from the list of objects to destroy because 1 your systemConfig contains a projects block and 2 you are using the --force flag.  ACM is assuming that the releaseDefinitions being skipped here are defined within the projects that your systemConfig defines, so that deleting each defined project would delete each of the releaseDefinitions defined within each project.  But if you have not configured your systemConfig properly, then the releaseDefinitions being skipped now might still remain in your deployment after this command completes its run.  "
          lw.writeLogVerbose("acm", logString)
        else:
          logString = "Halting program because we are leaving the destruction of releaseDefinitions to be a manual step in the UI portal in order to protect your data. If you would like to forcibly delete these releaseDefinitions using automation, then your you must do either one of two things: 1. add a forceDelete:True field to the system's configuration in platformConfig.yaml or 2. comment out the releaseDefinitions block in the systemConfig file while also incuding the containing project in the systemConfig file, so that deletion of the containing project will cascade delete the releaseDefinitions contained within the project."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
      else:
        logString = "Halting program because we are leaving the destruction of releaseDefinitions to be a manual step in the UI portal in order to protect your data. If you would like to forcibly delete these releaseDefinitions using automation, then your you must do either one of two things: 1. add a forceDelete:True field to the system's configuration in platformConfig.yaml or 2. comment out the releaseDefinitions block in the systemConfig file while also incuding the containing project in the systemConfig file, so that deletion of the containing project will cascade delete the releaseDefinitions contained within the project."
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    typeName = 'networkFoundation'
    if "foundation" not in systemConfig.keys():#len(foundationInstanceName) == 0:
      #Note: Leaving the following unhandled WARNING because some cases may involve a SaaS that does not have a network foundation.  
      logString = "WARNING: There is no foundation instanceName in your infrastructureConfig.yaml file.  If this is intended, everything is fine.  But if this is a mistake, then downstream errors may occur. "
      lw.writeLogVerbose("acm", logString)
    #add code to confirm that output operation succeeded.
    #Also, if output showed there is no network foundation, then skip the rest of the off operations because there would be nothing to off in that case.
    typeParent = 'systems'
    for typeName in typesToDestroy:
      if typeName != "networkFoundation" and (typeName != "subnetForBuilds") and (typeName != "images"):#Make work item to see if this if line can be removed now
        wfst_off.offServiceTypeGeneral(cm, ct, cc, level, systemInstanceName, systemConfig, typeName, typeParent)
    #Marking the releaseDefinitions as deleted in the changes_manifest because we are assuming that the containing projects have been deleted and have therefore caused the releaseDefinitions to be deleted in the --force operation.  But if your systemConfig is not correct, then the releaseDefinitions might still exist.  Check your systems and your config manually to validate your process.  
    if (isReleaseDef == True):
      if useTheForce:
        if self.checkDestroyType('projects', typesToDestroy):
          wfst_off.offServiceTypeRelease(cm, ct, cc, level, systemInstanceName, systemConfig)

  #@public
  def skipServices(self, level, systemInstanceName, yamlInfraConfig = 'default'):
    import config_cliprocessor

    lw = log_writer()
    test = config_cliprocessor.inputVars.get("test")
    typeOfTest = config_cliprocessor.inputVars.get("testType")
    infraConfigFileAndPath = yamlInfraConfig
    cfp = config_fileprocessor()
    typesToSkip = cfp.listTypesInSystem(infraConfigFileAndPath)
    for typeName in typesToSkip:
      logString = "All services of type " + typeName + "are being marked as completed because you used the --force flag in your command.  This block of code is not actually deleting those resources because the program will destroy the network foundation that you defined, which should destroy these services as part of the cascading foundation delete.  If these services remain after you run this operation during development, then change your configuration so that these services will be bundled within your network foundation's cascading delete. "
      lw.writeLogVerbose("acm", logString)
      changes_manifest.updateStartOfAServiceType(level, systemInstanceName, typeName)
      instanceNames = cfp.getSystemInstanceNames(infraConfigFileAndPath, typeName)
      for instanceName in instanceNames: 
        changes_manifest.updateStartOfAnInstanceOfAServiceType(level, systemInstanceName, typeName, instanceName)
        if (test==True) and (typeOfTest=="workflow"):
          pass
        else:
          outputDir = config_keysassembler.getOutputDir(instanceName)
          shutil.rmtree(outputDir)
        changes_manifest.updateEndOfAnInstanceOfAServiceType(level, systemInstanceName, typeName, instanceName)
      changes_manifest.updateEndOfAServiceType(level, systemInstanceName, typeName)

  def callOnFoundationDirectly(self):
    import config_cliprocessor
    cfp = config_fileprocessor()
    lw = log_writer()
    cm_fon = changes_manifest()
    ct_fon = changes_taxonomy()
    cc_fon = changes_comparer()
    systemToModify = config_cliprocessor.inputVars.get('systemName')
    systemConfig = None
    yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    platformConfig = cfp.getPlatformConfig(yamlPlatformConfigFileAndPath)
    for systemName in platformConfig:
      if systemName == systemToModify:
        systemConfig = platformConfig.get(systemName)
    if systemConfig == None:
      logString = "ERROR: The systemName that you specified does not exist in the platform configuration that you provided."
      quit(logString)
    cm_fon.initializeChangesManagementDataStructures(ct_fon, cc_fon, 'foundation', "on")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_fon.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    cm_fon.updateStartOfPlatformRun(ct_fon, cc_fon, 'foundation', "In Process")
    cm_fon.updateStartOfASystem(ct_fon, cc_fon, 'foundation', systemToModify, "In Process")
    cm_fon.updateStartOfAFoundation(ct_fon, cc_fon, 'foundation', systemToModify, "In Process")
    self.onFoundation(systemToModify, systemConfig)
    cm_fon.updateEndOfAFoundation(ct_fon, cc_fon, 'foundation', systemToModify)
    cm_fon.updateEndOfASystem(ct_fon, cc_fon, 'foundation', systemToModify)
    cm_fon.updateEndOfPlatformRun(ct_fon, cc_fon, 'foundation')

  def callOffFoundationDirectly(self):
    import config_cliprocessor
    cfp = config_fileprocessor()
    lw = log_writer()
    cm_foff = changes_manifest()
    ct_foff = changes_taxonomy()
    cc_foff = changes_comparer()
    systemToModify = config_cliprocessor.inputVars.get('systemName')
    systemConfig = None
    yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    platformConfig = cfp.getPlatformConfig(yamlPlatformConfigFileAndPath)
    for systemName in platformConfig:
      if systemName == systemToModify:
        systemConfig = platformConfig.get(systemName)
    if systemConfig == None:
      logString = "ERROR: The systemName that you specified does not exist in the platform configuration that you provided."
      quit(logString)
    cm_foff.initializeChangesManagementDataStructures(ct_foff, cc_foff, 'foundation', "off")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_foff.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    cm_foff.updateStartOfPlatformRun(ct_foff, cc_foff, 'foundation', "In Process")
    cm_foff.updateStartOfASystem(ct_foff, cc_foff, 'foundation', systemToModify, "In Process")
    cm_foff.updateStartOfAFoundation(ct_foff, cc_foff, 'foundation', systemToModify, "In Process")
    self.offFoundation(systemToModify, systemConfig)
    cm_foff.updateEndOfAFoundation(ct_foff, cc_foff, 'foundation', systemToModify)
    cm_foff.updateEndOfASystem(ct_foff, cc_foff, 'foundation', systemToModify)
    cm_foff.updateEndOfPlatformRun(ct_foff, cc_foff, 'foundation')

  def callOnServicesDirectly(self):
    import config_cliprocessor
    cfp = config_fileprocessor()
    lw = log_writer()
    cm_son = changes_manifest()
    ct_son = changes_taxonomy()
    cc_son = changes_comparer()
    systemToModify = config_cliprocessor.inputVars.get('systemName')
    systemConfig = None
    yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    platformConfig = cfp.getPlatformConfig(yamlPlatformConfigFileAndPath)
    for systemName in platformConfig:
      if systemName == systemToModify:
        systemConfig = platformConfig.get(systemName)
    if systemConfig == None:
      logString = "ERROR: The systemName that you specified does not exist in the platform configuration that you provided."
      quit(logString)
    cm_son.initializeChangesManagementDataStructures(ct_son, cc_son, 'services', "on")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_son.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    cm_son.updateStartOfPlatformRun(ct_son, cc_son, 'services', "In Process")
    cm_son.updateStartOfASystem(ct_son, cc_son, 'services', systemToModify, "In Process")
    cm_son.updateStartOfAServicesSection(ct_son, cc_son, 'services', systemToModify)
    self.onServices( cm_son, ct_son, cc_son, 'services', systemToModify, systemConfig)
    cm_son.updateEndOfAServicesSection(ct_son, cc_son, 'services', systemToModify)
    cm_son.updateEndOfASystem(ct_son, cc_son, 'services', systemToModify)
    cm_son.updateEndOfPlatformRun(ct_son, cc_son, 'services')

  def callOffServicesDirectly(self):
    import config_cliprocessor
    cfp = config_fileprocessor()
    lw = log_writer()
    cm_soff = changes_manifest()
    ct_soff = changes_taxonomy()
    cc_soff = changes_comparer()
    systemToModify = config_cliprocessor.inputVars.get('systemName')
    systemConfig = None
    yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    platformConfig = cfp.getPlatformConfig(yamlPlatformConfigFileAndPath)
    for systemName in platformConfig:
      if systemName == systemToModify:
        systemConfig = platformConfig.get(systemName)
    if systemConfig == None:
      logString = "ERROR: The systemName that you specified does not exist in the platform configuration that you provided."
      quit(logString)
    cm_soff.initializeChangesManagementDataStructures(ct_soff, cc_soff, 'services', "off")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_soff.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    cm_soff.updateStartOfPlatformRun(ct_soff, cc_soff, 'services', "In Process")
    cm_soff.updateStartOfASystem(ct_soff, cc_soff, 'services', systemToModify, "In Process")
    cm_soff.updateStartOfAServicesSection(ct_soff, cc_soff, 'services', systemToModify)
    self.offServices(cm_soff, ct_soff, cc_soff, 'services', systemToModify, systemConfig)
    cm_soff.updateEndOfAServicesSection(ct_soff, cc_soff, 'services', systemToModify)
    cm_soff.updateEndOfASystem(ct_soff, cc_soff, 'services', systemToModify)
    cm_soff.updateEndOfPlatformRun(ct_soff, cc_soff, 'services')

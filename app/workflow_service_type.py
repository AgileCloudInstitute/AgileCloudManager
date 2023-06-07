## Copyright 2023 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

import sys

from command_runner import command_runner
from controller_custom import controller_custom
from controller_terraform import controller_terraform
from controller_release import controller_release
from controller_azdoproject import controller_azdoproject
from controller_tfbackendazrm import controller_tfbackendazrm
from controller_arm import controller_arm
from controller_cf import controller_cf
from log_writer import log_writer
from config_fileprocessor import config_fileprocessor
from changes_manifest import changes_manifest
from changes_taxonomy import changes_taxonomy
from changes_comparer import changes_comparer

class workflow_service_type:
  
  def __init__(self):  
    pass

  #@public
  def onServiceType(self, cm, ct, cc, level, systemInstanceName, systemConfig, serviceType, typesToCreate):
    import config_cliprocessor
    lw = log_writer()
    if level == 'serviceinstance':
      instanceName = config_cliprocessor.inputVars.get('serviceInstance')
    cm.updateStartOfAServiceType(ct, cc, level, systemInstanceName, serviceType)
    instances = typesToCreate.get(serviceType).get("instances")
    for instance in instances:  
      if level == 'serviceinstance':
        if instance.get('instanceName') == instanceName:
          self.onServiceTypeInstance(cm, ct, cc, level, systemInstanceName, systemConfig, serviceType, instance)
      else:
        self.onServiceTypeInstance(cm, ct, cc, level, systemInstanceName, systemConfig, serviceType, instance)
    logString = "done with -- " + serviceType + " -----------------------------------------------------------------------------"
    lw.writeLogVerbose("acm", logString)
    cm.updateEndOfAServiceType(ct, cc, level, systemInstanceName, serviceType)

  def onServiceTypeInstance(self, cm, ct, cc, level, systemInstanceName, systemConfig, serviceType, instance):
    import config_cliprocessor
    test = config_cliprocessor.inputVars.get("test")
    typeOfTest = config_cliprocessor.inputVars.get("testType")
    cfp = config_fileprocessor()
    ccust = controller_custom()
    ccf = controller_cf()
    ctf = controller_terraform()
    ctfbknd = controller_tfbackendazrm()
    carm = controller_arm()
    crnr = command_runner()
    lw = log_writer()
    keyDir = cfp.getKeyDir(systemConfig)
    operation = 'on'
    instName = instance.get("instanceName")
    cm.updateStartOfAnInstanceOfAServiceType(ct, cc, level, systemInstanceName, serviceType, instName)
    if (test==True) and (typeOfTest=="workflow"):
      # Skip the else block when this workflow test is running.
      pass
    else:
      if "preprocessor" in instance.keys():
        preprocessor = instance.get("preprocessor") 
        crnr.runPreOrPostProcessor("pre", preprocessor, 'on') 
      else:
        pass
      instanceTool = instance.get("controller")
      if instanceTool =='arm':
        if serviceType == "tfBackend":
          armParamsDict = {"caller":'serviceInstance', "serviceType":serviceType}
          ctfbknd.createTfBackend(systemConfig, instance, armParamsDict)
        else:  
          carm.createDeployment(systemConfig, instance, 'serviceInstance', serviceType, False)
      elif instanceTool == 'cloudformation':
        ccf.createStack(systemConfig, instance, keyDir, 'serviceInstance', serviceType, instName)
      elif instanceTool.startswith('$customController.'):
        controllerPath = instanceTool.replace("$customController.","")
        controllerCommand = instance.get("controllerCommand")
        mappedVariables = instance.get("mappedVariables")
        ccust.runCustomController('on', systemConfig, controllerPath, controllerCommand, mappedVariables, serviceType, instance)
      elif instanceTool.startswith('$customControllerAPI.'):
        controllerPath = instanceTool.replace("$customControllerAPI.","")
        mappedVariables = instance.get("mappedVariables")
        ccust.runCustomControllerAPI('on', systemConfig, controllerPath, mappedVariables, serviceType, instance)
      else:
        if serviceType == "tfBackend":
          paramsDict = {}
          ctfbknd.createTfBackend(systemConfig, instance, paramsDict)
        elif serviceType == "releaseDefinitions":
          logString = "WARNING: releaseDefinitions is a reserved name that will have special meaning and requirements in future releases.  Choose a different name for your service types to avoid problems later.  "
          lw.writeLogVerbose("acm", logString)
          crls = controller_release()
          crls.onPipeline('projects', systemConfig, instance)
        elif serviceType == 'projects':
          ctrlrazproj = controller_azdoproject()
          ctrlrazproj.onProject(serviceType, systemConfig, instance)
        else:
          ctf.terraformCrudOperation(operation, keyDir, systemConfig, instance, 'systems', serviceType, None, instName)
      postprocessor = instance.get("postprocessor")
      if postprocessor:
        crnr.runPreOrPostProcessor("post", postprocessor, 'on')
      else:
        pass
    cm.updateEndOfAnInstanceOfAServiceType(ct, cc, level, systemInstanceName, serviceType, instName)

  #@public
  def offServiceTypeGeneral(self, cm, ct, cc, level, systemInstanceName, systemConfig, typeName, typeParent):
    import config_cliprocessor
    lw = log_writer()
    if level == 'serviceinstance':
      instanceName = config_cliprocessor.inputVars.get('serviceInstance')
    cm.updateStartOfAServiceType(ct, cc, level, systemInstanceName, typeName)
    for typeOfService in systemConfig.get("serviceTypes"):
      if typeOfService == typeName:
        instances = systemConfig.get("serviceTypes").get(typeOfService).get("instances")
        for instance in instances:
          if level == 'serviceinstance':
            if instance.get('instanceName') == instanceName:
              self.offServiceTypeGeneralInstance(cm, ct, cc, level, systemInstanceName, systemConfig, typeName, typeParent, instance)
          else:
            self.offServiceTypeGeneralInstance(cm, ct, cc, level, systemInstanceName, systemConfig, typeName, typeParent, instance)
    cm.updateEndOfAServiceType(ct, cc, level, systemInstanceName, typeName)
    logString = "done with -- " + typeName + " -----------------------------------------------------------------------------"
    lw.writeLogVerbose("acm", logString)

  def offServiceTypeRelease(self, cm, ct, cc, level, systemInstanceName, systemConfig):
    cm.updateStartOfAServiceType(ct, cc, level, systemInstanceName, 'releaseDefinitions')
    instanceNames = []
    for item in systemConfig:
      if item == "serviceTypes":
        for sType in systemConfig.get(item):
          if sType == "releaseDefinitions":
            for rdInstance in systemConfig.get(item).get(sType).get("instances"):
              instanceNames.append(rdInstance.get("instanceName"))
    for instName in instanceNames:
      ##NOTE: THE REASON WE ARE NOT CREATING A SEPARATE FUNCTION TO DESTROY THESE INSTANCES IS THAT THIS CODE IS 
      # ONLY CALLED WHEN USETHEFORCE HAS BEEN SET FOR RELEASEDEF TYPE.  USETHEFORCE WILL DELETE THE 
      # ENCLOSING PROJECT WHICH IN TURN WILL DESTROY THE RELEASEDEFS CONTAINED IN THE PROJECT.  AND 
      # ALSO, WE HAVE A RULE TO NOT DESTROY RELEASEDEF TYPES UNLESS USETHEFORCE IS SPECIFIED.
      cm.updateStartOfAnInstanceOfAServiceType(ct, cc, level, systemInstanceName, 'releaseDefinitions', instName)
      cm.updateEndOfAnInstanceOfAServiceType(ct, cc, level, systemInstanceName, 'releaseDefinitions', instName)
    cm.updateEndOfAServiceType(ct, cc, level, systemInstanceName, 'releaseDefinitions')

  def offServiceTypeGeneralInstance(self, cm, ct, cc, level, systemInstanceName, systemConfig, typeName, typeParent, instance):
    import config_cliprocessor
    test = config_cliprocessor.inputVars.get("test")
    typeOfTest = config_cliprocessor.inputVars.get("testType")
    cfp = config_fileprocessor()
    ccust = controller_custom()
    ccf = controller_cf()
    ctf = controller_terraform()
    carm = controller_arm()
    lw = log_writer()
    crnr = command_runner()
    keyDir = cfp.getKeyDir(systemConfig)
    operation = "off"
    instName = instance.get("instanceName")
    cm.updateStartOfAnInstanceOfAServiceType(ct, cc, level, systemInstanceName, typeName, instName)
    if (test==True) and (typeOfTest=="workflow"):
      pass
    else:
      if "preprocessor" in instance.keys():
        preprocessor = instance.get("preprocessor")
        crnr.runPreOrPostProcessor("pre", preprocessor, 'off')
      else:
        logString = 'NO preprocessor present.'
        lw.writeLogVerbose("acm", logString)
        pass
      instanceTool = instance.get("controller")
      if typeName == 'projects':
        ctrlrazproj = controller_azdoproject()
        ctrlrazproj.offProject(typeName, systemConfig, instance)
      else:
        if instanceTool == 'arm':
          carm.destroyDeployment(systemConfig, instance, 'serviceInstance')
          pass
        elif instanceTool == 'terraform':
          ctf.terraformCrudOperation(operation, keyDir, systemConfig, instance, typeParent, typeName, None, instName)
          if ctf.terraformResult == "Destroyed": 
            logString = "off operation succeeded.  Now inside Python conditional block to do only after the off operation has succeeded. "
            lw.writeLogVerbose("acm", logString)
          else:
            logString = "Error: off operation failed.  "
            lw.writeLogVerbose("acm", logString)
            sys.exit(1)
        elif instanceTool == 'cloudformation':
          ccf.destroyStack(systemConfig, instance, keyDir, 'serviceInstance')
        elif instanceTool.startswith('$customController.'):
          controllerPath = instanceTool.replace("$customController.","")
          controllerCommand = instance.get("controllerCommand")
          mappedVariables = instance.get("mappedVariables")
          ccust.runCustomController(operation, systemConfig, controllerPath, controllerCommand, mappedVariables, typeName, instance)
        elif instanceTool.startswith('$customControllerAPI.'):
          controllerPath = instanceTool.replace("$customControllerAPI.","")
          mappedVariables = instance.get("mappedVariables")
          ccust.runCustomControllerAPI(operation, systemConfig, controllerPath, mappedVariables, typeName, instance)
        else:
          logString = "Error: The value selected for instanceTool is not supportd:  "+instanceTool
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)

      if "postprocessor" in instance.keys():
        postprocessor = instance.get("postprocessor")
        crnr.runPreOrPostProcessor("post", postprocessor, 'off')
      else:
        logString = 'NO postprocessor present.'
        lw.writeLogVerbose("acm", logString)
        pass
    cm.updateEndOfAnInstanceOfAServiceType(ct, cc, level, systemInstanceName, typeName, instName)

  def callOnServiceDirectly(self, level):
    import config_cliprocessor
    cfp = config_fileprocessor()
    lw = log_writer()
    cm_son = changes_manifest()
    ct_son = changes_taxonomy()
    cc_son = changes_comparer()
    systemToModify = config_cliprocessor.inputVars.get('systemName')
    serviceType = config_cliprocessor.inputVars.get('serviceType')
    systemConfig = None
    yamlApplianceConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    applianceConfig = cfp.getApplianceConfig(yamlApplianceConfigFileAndPath)
    for systemName in applianceConfig:
      if systemName == systemToModify:
        systemConfig = cfp.getSystemConfig(applianceConfig, systemName)
    if systemConfig == None: 
      print("220 systemToModify is: ", systemToModify)
      print("221 applianceConfig is: ", str(applianceConfig))
      logString = "ERROR: The systemName that you specified does not exist in the appliance configuration that you provided."
      print(logString)
      sys.exit(1) 
    cm_son.initializeChangesManagementDataStructures(ct_son, cc_son, level, "on")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_son.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    cm_son.updateStartOfApplianceRun(ct_son, cc_son, level, "In Process")
    cm_son.updateStartOfASystem(ct_son, cc_son, level, systemToModify, "In Process")
    cm_son.updateStartOfAServicesSection(ct_son, cc_son, level, systemToModify)
    typesToCreate = systemConfig.get("serviceTypes")
    for typeOfService in typesToCreate.keys():
      if typeOfService == serviceType:
        self.onServiceType(cm_son, ct_son, cc_son, level, systemToModify, systemConfig, serviceType, typesToCreate)
    cm_son.updateEndOfAServicesSection(ct_son, cc_son, level, systemToModify)
    cm_son.updateEndOfASystem(ct_son, cc_son, level, systemToModify)
    cm_son.updateEndOfApplianceRun(ct_son, cc_son, level)

  def callOffServiceDirectly(self, level):
    import config_cliprocessor
    cfp = config_fileprocessor()
    lw = log_writer()
    cm_stoff = changes_manifest()
    ct_stoff = changes_taxonomy()
    cc_stoff = changes_comparer()
    systemToModify = config_cliprocessor.inputVars.get('systemName')
    svcTyp = config_cliprocessor.inputVars.get('serviceType')
    systemConfig = None
    yamlApplianceConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    applianceConfig = cfp.getApplianceConfig(yamlApplianceConfigFileAndPath)
    for systemName in applianceConfig:
      if systemName == systemToModify:
        systemConfig = cfp.getSystemConfig(applianceConfig, systemName)
    if systemConfig == None:
      print("255 systemToModify is: ", systemToModify)
      print("256 applianceConfig is: ", str(applianceConfig))
      print("yamlApplianceConfigFileAndPath is: ", yamlApplianceConfigFileAndPath)
      logString = "ERROR: The systemName that you specified does not exist in the appliance configuration that you provided."
      print(logString)
      sys.exit(1)
    cm_stoff.initializeChangesManagementDataStructures(ct_stoff, cc_stoff, level, "on")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_stoff.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    cm_stoff.updateStartOfApplianceRun(ct_stoff, cc_stoff, level, "In Process")
    cm_stoff.updateStartOfASystem(ct_stoff, cc_stoff, level, systemToModify, "In Process")
    cm_stoff.updateStartOfAServicesSection(ct_stoff, cc_stoff, level, systemToModify)
    #NOTE: The foundation for releaseDefinitions needs to be a controller_azdoproject in order to force deletion of a releaseDefinition
    typesToDestroy = dict(systemConfig.get("serviceTypes"))
    isTfBackend = self.checkDestroyType('tfBackend', typesToDestroy)
    useTheForce = systemConfig.get("forceDelete") 
    if isTfBackend == True:
      if not useTheForce:
        logString = "Halting program because we are leaving the destruction of terraform backends to be a manual step in the UI portal in order to protect your data. "
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    if svcTyp == "releaseDefinitions":
        logString = "Note: releaseDefinitions is a reserved name for service types that will have meaning in future releases.  "
        lw.writeLogVerbose("acm", logString)
        logString = "Halting program because we are leaving the destruction of releaseDefinitions to be a manual step in the UI portal in order to protect your data. If you would like to forcibly delete these releaseDefinitions using automation, then your you must do either one of two things: 1. add a forceDelete:True field to the system's configuration in acm.yaml while running appliance off or services off, or 2. delete the containing project in order to cascade delete the releaseDefinitions contained within the project.  You can delete the containing project using either the serviceType off or serviceInstance off cli commands.  "
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    typeName = 'networkFoundation'
    if "foundation" not in systemConfig.keys():
      #Note: Leaving the following unhandled WARNING because some cases may involve a SaaS that does not have a network foundation.  
      logString = "WARNING: There is no foundation in your acm.yaml file.  If this is intended, everything is fine.  But if this is a mistake, then downstream errors may occur. "
      lw.writeLogVerbose("acm", logString)
    #add code to confirm that output operation succeeded.
    #Also, if output showed there is no network foundation, then skip the rest of the off operations because there would be nothing to off in that case.
    typeParent = 'systems'
    for typeName in typesToDestroy:
      if typeName == svcTyp:
        self.offServiceTypeGeneral(cm_stoff, ct_stoff, cc_stoff, level, systemToModify, systemConfig, typeName, typeParent)
    cm_stoff.updateEndOfAServicesSection(ct_stoff, cc_stoff, level, systemToModify)
    cm_stoff.updateEndOfASystem(ct_stoff, cc_stoff, level, systemToModify)
    cm_stoff.updateEndOfApplianceRun(ct_stoff, cc_stoff, level)

  #@private
  def checkDestroyType(self, typeName, typesToDestroy):
    for serviceType in typesToDestroy:
      if typeName in serviceType:
        return True
    return False

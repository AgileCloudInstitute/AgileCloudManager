## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

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
    print('instances is:', instances)
#    if serviceType == 'releaseDefinitions':
#      quit('dfghjk')

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
    keyDir = cfp.getKeyDir(systemConfig)
    operation = 'on'
    instName = instance.get("instanceName")
    cm.updateStartOfAnInstanceOfAServiceType(ct, cc, level, systemInstanceName, serviceType, instName)
    print('test is: ', test)
    print('typeOfTest is: ', typeOfTest )
#    quit('nn ---  yuio')
    if (test==True) and (typeOfTest=="workflow"):
      # Skip the else block when this workflow test is running.
      pass
    else:
      if "preprocessor" in instance.keys():
        preprocessor = instance.get("preprocessor")
        crnr.runPreOrPostProcessor(preprocessor, 'on') 
      else:
        pass
      instanceTool = instance.get("controller")
      print('instanceTool is: ', instanceTool)
      print('serviceType is: ', serviceType)
      if instanceTool =='arm':
        if serviceType == "tfBackend":
          armParamsDict = {"caller":'serviceInstance', "serviceType":serviceType}
          ctfbknd.createTfBackend(systemConfig, instance, armParamsDict)
          print('hkjgfdsa')
          quit('BREAK tfBackend1')
        else:  
          carm.createDeployment(systemConfig, instance, 'serviceInstance', serviceType, False)
      elif instanceTool == 'cloudformation':
        ccf.createStack(systemConfig, instance, keyDir, 'serviceInstance', serviceType, instName)
      elif instanceTool.startswith('$customController.'):
        controllerPath = instanceTool.replace("$customController.","")
        controllerCommand = instance.get("controllerCommand")
        mappedVariables = instance.get("mappedVariables")
        ccust.runCustomController('on', systemConfig, controllerPath, controllerCommand, mappedVariables, serviceType, instance)
      else:
        if serviceType == "tfBackend":
          paramsDict = {}
          ctfbknd.createTfBackend(systemConfig, instance, paramsDict)
        elif serviceType == "releaseDefinitions":
          crls = controller_release()
#          crls.onPipeline(serviceType, systemConfig, instance)
          crls.onPipeline('projects', systemConfig, instance)
        elif serviceType == 'projects':
          ctrlrazproj = controller_azdoproject()
          ctrlrazproj.onProject(serviceType, systemConfig, instance)
        else:
#          ctf.terraformCrudOperation(operation, systemInstanceName, keyDir, systemConfig, instance, 'systems', None, None, instName)
          ctf.terraformCrudOperation(operation, keyDir, systemConfig, instance, 'systems', serviceType, None, instName)
#              terraformCrudOperation(operation, keyDir, systemConfig, instance, typeParent, typeName, typeGrandChild, typeInstanceName)

      postprocessor = instance.get("postprocessor")
      if postprocessor:
        crnr.runPreOrPostProcessor(postprocessor, 'on')
      else:
        pass
    quit('BREAK tfBackend2')
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
        logString = 'preprocessor is: '+ str(preprocessor)
        lw.writeLogVerbose("acm", logString)
        crnr.runPreOrPostProcessor(preprocessor, 'off')
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
        elif instanceTool == 'terraform':
#          ctf.terraformCrudOperation(operation, systemInstanceName, keyDir, systemConfig, instance, typeParent, None, None, instName)
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
        else:
          logString = "Error: The value selected for instanceTool is not supportd:  "+instanceTool
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
      if "postprocessor" in instance.keys():
        postprocessor = instance.get("postprocessor")
        logString = 'postprocessor is: '+ str(postprocessor)
        lw.writeLogVerbose("acm", logString)
        crnr.runPreOrPostProcessor(postprocessor, 'off')
      else:
        logString = 'NO postprocessor present.'
        lw.writeLogVerbose("acm", logString)
        pass
    cm.updateEndOfAnInstanceOfAServiceType(ct, cc, level, systemInstanceName, typeName, instName)

#############################################################################################################



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
    yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    platformConfig = cfp.getPlatformConfig(yamlPlatformConfigFileAndPath)
    for systemName in platformConfig:
      if systemName == systemToModify:
        systemConfig = platformConfig.get(systemName)
    if systemConfig == None:
      logString = "ERROR: The systemName that you specified does not exist in the platform configuration that you provided."
      quit(logString)
    cm_son.initializeChangesManagementDataStructures(ct_son, cc_son, level, "on")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_son.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    cm_son.updateStartOfPlatformRun(ct_son, cc_son, level, "In Process")
    cm_son.updateStartOfASystem(ct_son, cc_son, level, systemToModify, "In Process")
    cm_son.updateStartOfAServicesSection(ct_son, cc_son, level, systemToModify)
    typesToCreate = systemConfig.get("serviceTypes")
    print('typesToCreate.keys() is: ', typesToCreate.keys())
#    quit('uytrewq')
    for typeOfService in typesToCreate.keys():
      if typeOfService == serviceType:
        self.onServiceType(cm_son, ct_son, cc_son, level, systemToModify, systemConfig, serviceType, typesToCreate)
#    print('ct_son.changeTaxonomy is: ', ct_son.changeTaxonomy)
#    quit('--11--00--88--')
    cm_son.updateEndOfAServicesSection(ct_son, cc_son, level, systemToModify)
    cm_son.updateEndOfASystem(ct_son, cc_son, level, systemToModify)
    cm_son.updateEndOfPlatformRun(ct_son, cc_son, level)
#    quit('---000---999')

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
    yamlPlatformConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
    platformConfig = cfp.getPlatformConfig(yamlPlatformConfigFileAndPath)
    for systemName in platformConfig:
      if systemName == systemToModify:
        systemConfig = platformConfig.get(systemName)
    if systemConfig == None:
      logString = "ERROR: The systemName that you specified does not exist in the platform configuration that you provided."
      quit(logString)
    cm_stoff.initializeChangesManagementDataStructures(ct_stoff, cc_stoff, level, "on")
    logString = "This run of the Agile Cloud Manager will complete " + str(len(cm_stoff.changesManifest)) + " changes. "
    lw.writeLogVerbose("acm", logString)
    cm_stoff.updateStartOfPlatformRun(ct_stoff, cc_stoff, level, "In Process")
    cm_stoff.updateStartOfASystem(ct_stoff, cc_stoff, level, systemToModify, "In Process")
    cm_stoff.updateStartOfAServicesSection(ct_stoff, cc_stoff, level, systemToModify)
    #NOTE: The foundation for releaseDefinitions needs to be an controller_azdoproject in order for forcing deletion of a releaseDefinition
    typesToDestroy = dict(systemConfig.get("serviceTypes"))
    isTfBackend = self.checkDestroyType('tfBackend', typesToDestroy)
#    isReleaseDef = self.checkDestroyType('releaseDefinitions', typesToDestroy)
    useTheForce = systemConfig.get("forceDelete") 

    print('typesToDestroy.keys() is: ', typesToDestroy.keys())
#    print('isReleaseDef is: ', isReleaseDef)
    print('useTheForce is: ', useTheForce)
#    quit('jhgfvcx')
    if isTfBackend == True:
      if not useTheForce:
        logString = "Halting program because we are leaving the destruction of terraform backends to be a manual step in the UI portal in order to protect your data. "
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
#    elif (isReleaseDef == True):
#      if useTheForce:
#        if self.checkDestroyType('projects', typesToDestroy):
#          typesToDestroy.pop('releaseDefinitions')
#          logString = "WARNING:  ACM removed the releaseDefinitions from the list of objects to destroy because 1 your systemConfig contains a projects block and 2 you are using the --force flag.  ACM is assuming that the releaseDefinitions being skipped here are defined within the projects that your systemConfig defines, so that deleting each defined project would delete each of the releaseDefinitions defined within each project.  But if you have not configured your systemConfig properly, then the releaseDefinitions being skipped now might still remain in your deployment after this command completes its run.  "
#          lw.writeLogVerbose("acm", logString)
#          logString = "WARNING: The releaseDefinitions service type is also NOT being included in the change logs for this destroy run because we are assuming that you have configured your system so that deletion of the containing project will include a cascading delete of all releaseDefinitions contained within each project.  "
#          lw.writeLogVerbose("acm", logString)
#        else:
#          logString = "Halting program because we are leaving the destruction of releaseDefinitions to be a manual step in the UI portal in order to protect your data. If you would like to forcibly delete these releaseDefinitions using automation, then your you must do either one of two things: 1. add a forceDelete:True field to the system's configuration in platformConfig.yaml or 2. comment out the releaseDefinitions block in the systemConfig file while also incuding the containing project in the systemConfig file, so that deletion of the containing project will cascade delete the releaseDefinitions contained within the project."
#          lw.writeLogVerbose("acm", logString)
#          sys.exit(1)
#      else:
    if svcTyp == "releaseDefinitions":
        logString = "Halting program because we are leaving the destruction of releaseDefinitions to be a manual step in the UI portal in order to protect your data. If you would like to forcibly delete these releaseDefinitions using automation, then your you must do either one of two things: 1. add a forceDelete:True field to the system's configuration in acm.yaml while running platform off or services off, or 2. delete the containing project in order to cascade delete the releaseDefinitions contained within the project.  You can delete the containing project using either the serviceType off or serviceInstance off cli commands.  "
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
      if typeName == svcTyp:
        self.offServiceTypeGeneral(cm_stoff, ct_stoff, cc_stoff, level, systemToModify, systemConfig, typeName, typeParent)
    cm_stoff.updateEndOfAServicesSection(ct_stoff, cc_stoff, level, systemToModify)
    cm_stoff.updateEndOfASystem(ct_stoff, cc_stoff, level, systemToModify)
    cm_stoff.updateEndOfPlatformRun(ct_stoff, cc_stoff, level)

  #@private
  def checkDestroyType(self, typeName, typesToDestroy):
    for serviceType in typesToDestroy:
      if typeName in serviceType:
        return True
    return False


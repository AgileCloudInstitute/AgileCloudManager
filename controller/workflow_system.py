## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import sys
import shutil

import config_fileprocessor
import command_runner
import controller_terraform
import controller_image
import controller_release
import controller_azdoproject
import logWriter
import config_keysassembler
import controller_tfbackendazrm
import controller_arm
import changes_manifest
import config_cliprocessor
import controller_cf
import command_builder

def onFoundation(command, systemInstanceName, keyDir, source, yamlInfraConfig = 'default'):
  test = config_cliprocessor.inputVars.get("test")
  typeOfTest = config_cliprocessor.inputVars.get("testType")
  infraConfigFileAndPath = yamlInfraConfig
  if yamlInfraConfig == "default":
    infraConfigFileAndPath = config_cliprocessor.inputVars.get('yamlInfraConfigFileAndPath')
  else:
    infraConfigFileAndPath = config_cliprocessor.inputVars.get('acmConfigPath')+command_builder.getSlashForOS() + yamlInfraConfig
  typeName = 'networkFoundation'
#  quit(infraConfigFileAndPath)
  foundationInstanceName = config_fileprocessor.getFoundationInstanceName(infraConfigFileAndPath)
  foundationTool = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'tool')

  operation = command

  if (test==True) and (typeOfTest=="workflow"):
    # Skip the else block in this case because we are just testing the workflow.
    pass
  else:
    preprocessor = config_fileprocessor.getPreProcessor(infraConfigFileAndPath, 'networkFoundation', None, None)
    if preprocessor:
      print('preprocessor is: ', str(preprocessor))
#      quit('Hi!')
      command_runner.runPreOrPostProcessor(preprocessor, 'on')
    else:
      print('NO preprocessor present.')
      pass
#    quit('debug preprocessor')
    if foundationTool == 'arm':
      controller_arm.createDeployment(infraConfigFileAndPath, keyDir, 'networkFoundation', None, foundationInstanceName)
    elif foundationTool == 'cloudformation':
      controller_cf.createStack(infraConfigFileAndPath, keyDir, 'networkFoundation', None, foundationInstanceName)
      hasImageBuilds = config_fileprocessor.checkTopLevelType(infraConfigFileAndPath, 'imageBuilds')
      if hasImageBuilds:
        controller_image.buildImages(systemInstanceName, infraConfigFileAndPath, operation, keyDir)
      else:
        logString = "WARNING: This network foundation does not have any image builds associated with it.  If you intend not to build images in this network, then everything is fine.  But if you do want to build images with this network, then check your configuration and re-run this command.  "
        logWriter.writeLogVerbose("acm", logString)
    elif foundationTool =='terraform':
      controller_terraform.terraformCrudOperation(operation, systemInstanceName, keyDir, infraConfigFileAndPath, 'none', typeName, None, None, foundationInstanceName)
      if command_runner.terraformResult == "Applied": 
        hasImageBuilds = config_fileprocessor.checkTopLevelType(infraConfigFileAndPath, 'imageBuilds')
        if hasImageBuilds:
          controller_image.buildImages(systemInstanceName, infraConfigFileAndPath, operation, keyDir)
        else:
          logString = "WARNING: This network foundation does not have any image builds associated with it.  If you intend not to build images in this network, then everything is fine.  But if you do want to build images with this network, then check your configuration and re-run this command.  "
          logWriter.writeLogVerbose("acm", logString)
      else:
        logString = "Foundation apply failed for " + systemInstanceName
        logWriter.writeLogVerbose("acm", logString)
        sys.exit(1)
    else:
      logString = "The following value for foundationTool from your systemConfig is not supported: " + foundationTool
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
    postprocessor = config_fileprocessor.getPostProcessor(infraConfigFileAndPath, 'networkFoundation', None, None)
    if postprocessor:
      print('postprocessor is: ', str(postprocessor))
      command_runner.runPreOrPostProcessor(postprocessor, 'on')
    else:
      print('NO postprocessor present.')
      pass
#    quit('debug postprocessor')

def offFoundation(systemInstanceName, keyDir, infraConfigFileAndPath):
  test = config_cliprocessor.inputVars.get("test")
  typeOfTest = config_cliprocessor.inputVars.get("testType")
  if (test==True) and (typeOfTest=="workflow"):
    # Skip the else block in this case because we are just testing the workflow.
    pass
  else:
    preprocessor = config_fileprocessor.getPreProcessor(infraConfigFileAndPath, 'networkFoundation', None, None)
    if preprocessor:
      print('preprocessor is: ', str(preprocessor))
#      quit('Hi!')
      command_runner.runPreOrPostProcessor(preprocessor, 'off')
    else:
      print('NO preprocessor present.')
      pass
#    quit('debug preprocessor')
    #add code to confirm that output operation succeeded.
    #Also, if output showed there is no network foundation, then skip the rest of the off operations because there would be nothing to off in that case.
    #ADD LOGIC HERE TO PREPARE BEFORE DELETING THE FOUNDATION 
    ##########################################################################################
    ### off the Network Foundation and the Instance of the Call To The Foundation Module
    ##########################################################################################
    typeName = 'networkFoundation'
    foundationInstanceName = config_fileprocessor.getFoundationInstanceName(infraConfigFileAndPath)
    foundationTool = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'tool')
    operation = 'off'
    if foundationTool == 'arm':
      controller_arm.destroyDeployment(systemInstanceName, keyDir, infraConfigFileAndPath, 'networkFoundation', None, None)
    elif foundationTool == 'cloudformation':
      controller_cf.destroyStack(infraConfigFileAndPath, keyDir, 'networkFoundation', None, foundationInstanceName)
    elif foundationTool == 'terraform':
      controller_terraform.terraformCrudOperation(operation, systemInstanceName, keyDir, infraConfigFileAndPath, 'none', typeName, None, None, foundationInstanceName)
      if command_runner.terraformResult == "Destroyed": 
        logString = "off operation succeeded.  Now inside Python conditional block to do only after the off operation has succeeded. "
        logWriter.writeLogVerbose("acm", logString)
      else:
        logString = "Error: offFoundation operation failed.  "
        logWriter.writeLogVerbose("acm", logString)
        sys.exit(1)
    postprocessor = config_fileprocessor.getPostProcessor(infraConfigFileAndPath, 'networkFoundation', None, None)
    if postprocessor:
      print('postprocessor is: ', str(postprocessor))
      command_runner.runPreOrPostProcessor(postprocessor, 'off')
    else:
      print('NO postprocessor present.')
      pass
#    quit('debug postprocessor')

def onServices(command, level, systemInstanceName, keyDir, infraConfigFileAndPath):
  test = config_cliprocessor.inputVars.get("test")
  typeOfTest = config_cliprocessor.inputVars.get("testType")
  foundationTool = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'tool')
  foundTypeName = 'networkFoundation'
  foundationInstanceName = config_fileprocessor.getFoundationInstanceName(infraConfigFileAndPath)
  if len(foundationInstanceName) == 0:
    #Note: Leaving the following unhandled WARNING because some cases may involve a SaaS that does not have a network foundation.  
    logString = "WARNING: There is no foundation instanceName in your infrastructureConfig.yaml file.  If this is intended, everything is fine.  But if this is a mistake, then downstream errors may occur. "
    logWriter.writeLogVerbose("acm", logString)
  else:  
#    instanceNames = [foundationInstanceName]
    operation = 'output'
    if (test==True) and (typeOfTest=="workflow"):
      # Skip the else block when this workflow test is running.
      pass
    else:
      if foundationTool == 'terraform':
        controller_terraform.terraformCrudOperation(operation, systemInstanceName, keyDir, infraConfigFileAndPath, 'none', foundTypeName, None, None, foundationInstanceName)
  operation = 'on'
  typesToCreate = config_fileprocessor.listTypesInSystem(infraConfigFileAndPath)
  for serviceType in typesToCreate:
    if (serviceType != "networkFoundation") and (serviceType != "subnetForBuilds") and (serviceType != "images"): #Make work item to check if this check for these 3 service types is still necessary.
      changes_manifest.updateStartOfAServiceType(level, systemInstanceName, serviceType)
      instanceNames = config_fileprocessor.getSystemInstanceNames(infraConfigFileAndPath, serviceType)
      for instName in instanceNames:  
        changes_manifest.updateStartOfAnInstanceOfAServiceType(level, systemInstanceName, serviceType, instName)
        if (test==True) and (typeOfTest=="workflow"):
          # Skip the else block when this workflow test is running.
          pass
        else:
          preprocessor = config_fileprocessor.getPreProcessor(infraConfigFileAndPath, 'serviceInstance', serviceType, instName)
          if preprocessor:
            print('preprocessor is: ', str(preprocessor))
      #      quit('Hi!')
            command_runner.runPreOrPostProcessor(preprocessor, 'on')
          else:
            print('NO preprocessor present.')
            pass
#          quit('debug preprocessor')
          instanceTool = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, serviceType, instName, 'tool')
          if instanceTool =='arm':
            controller_arm.createDeployment(infraConfigFileAndPath, keyDir, 'serviceInstance', serviceType, instName)
          elif instanceTool == 'cloudformation':
            controller_cf.createStack(infraConfigFileAndPath, keyDir, 'serviceInstance', serviceType, instName)
          else:# instanceTool != 'arm':
            if serviceType == "tfBackend":
              controller_tfbackendazrm.createTfBackend(systemInstanceName, instName, infraConfigFileAndPath, keyDir)
            elif serviceType == "releaseDefinitions":
              controller_release.onPipeline(command, systemInstanceName, instName, infraConfigFileAndPath, keyDir)
            elif serviceType == 'projects':
              controller_azdoproject.onProject("on", systemInstanceName, instName, infraConfigFileAndPath, keyDir)
            else:
              controller_terraform.terraformCrudOperation(operation, systemInstanceName, keyDir, infraConfigFileAndPath, 'systems', serviceType, None, None, instName)
          postprocessor = config_fileprocessor.getPostProcessor(infraConfigFileAndPath, 'serviceInstance', serviceType, instName)
          if postprocessor:
            print('postprocessor is: ', str(postprocessor))
            command_runner.runPreOrPostProcessor(postprocessor, 'on')
          else:
            print('NO postprocessor present.')
            pass
#          quit('debug postprocessor')
        changes_manifest.updateEndOfAnInstanceOfAServiceType(level, systemInstanceName, serviceType, instName)
      logString = "done with -- " + serviceType + " -----------------------------------------------------------------------------"
      logWriter.writeLogVerbose("acm", logString)
      changes_manifest.updateEndOfAServiceType(level, systemInstanceName, serviceType)

def checkDestroyType(typeName, infraConfigFileAndPath):
  typesToDestroy = config_fileprocessor.listTypesInSystem(infraConfigFileAndPath)
  for serviceType in typesToDestroy:
    if typeName in serviceType:
      return True
  return False

  
def offServices(level, systemInstanceName, keyDir, yamlPlatformConfigFileAndPath, infraConfigFileAndPath = 'default'):
  test = config_cliprocessor.inputVars.get("test")
  typeOfTest = config_cliprocessor.inputVars.get("testType")
  #NOTE: The foundation for releaseDefinitions needs to be an controller_azdoproject in order for forcing deletion of a releaseDefinition
  typesToDestroy = config_fileprocessor.listTypesInSystem(infraConfigFileAndPath)
  isTfBackend = checkDestroyType('tfBackend', infraConfigFileAndPath)
  isReleaseDef = checkDestroyType('releaseDefinitions', infraConfigFileAndPath)
  if yamlPlatformConfigFileAndPath != None:
    useTheForce = config_fileprocessor.getForce(yamlPlatformConfigFileAndPath, 'systems', systemInstanceName)
  else:
    useTheForce = False
  foundationTool = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'tool')
#  quit('do!')
  if isTfBackend == True:
    logString = "Halting program because we are leaving the destruction of terraform backends to be a manual step in the UI portal in order to protect your data. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  elif (isReleaseDef == True):
    if useTheForce:
      if checkDestroyType('projects', infraConfigFileAndPath):
        typesToDestroy.remove('releaseDefinitions')
        logString = "WARNING:  ACM removed the releaseDefinitions from the list of objects to destroy because 1 your systemConfig contains a projects block and 2 you are using the --force flag.  ACM is assuming that the releaseDefinitions being skipped here are defined within the projects that your systemConfig defines, so that deleting each defined project would delete each of the releaseDefinitions defined within each project.  But if you have not configured your systemConfig properly, then the releaseDefinitions being skipped now might still remain in your deployment after this command completes its run.  "
        logWriter.writeLogVerbose("acm", logString)
      else:
        logString = "Halting program because we are leaving the destruction of releaseDefinitions to be a manual step in the UI portal in order to protect your data. If you would like to forcibly delete these releaseDefinitions using automation, then your you must do either one of two things: 1. add a forceDelete:True field to the system's configuration in platformConfig.yaml or 2. comment out the releaseDefinitions block in the systemConfig file while also incuding the containing project in the systemConfig file, so that deletion of the containing project will cascade delete the releaseDefinitions contained within the project."
        logWriter.writeLogVerbose("acm", logString)
        sys.exit(1)
    else:
      logString = "Halting program because we are leaving the destruction of releaseDefinitions to be a manual step in the UI portal in order to protect your data. If you would like to forcibly delete these releaseDefinitions using automation, then your you must do either one of two things: 1. add a forceDelete:True field to the system's configuration in platformConfig.yaml or 2. comment out the releaseDefinitions block in the systemConfig file while also incuding the containing project in the systemConfig file, so that deletion of the containing project will cascade delete the releaseDefinitions contained within the project."
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
  typeName = 'networkFoundation'
  foundationInstanceName = config_fileprocessor.getFoundationInstanceName(infraConfigFileAndPath)
  if len(foundationInstanceName) == 0:
    #Note: Leaving the following unhandled WARNING because some cases may involve a SaaS that does not have a network foundation.  
    logString = "WARNING: There is no foundation instanceName in your infrastructureConfig.yaml file.  If this is intended, everything is fine.  But if this is a mistake, then downstream errors may occur. "
    logWriter.writeLogVerbose("acm", logString)
  else:  
    if (test==True) and (typeOfTest=="workflow"):
      pass
    else:
      if foundationTool == 'terraform':
        operation = 'output'
        controller_terraform.terraformCrudOperation(operation, systemInstanceName, keyDir, infraConfigFileAndPath, 'none', typeName, None, None, foundationInstanceName)
      elif foundationTool == 'cloudformation':
        #pass here because aws cloudformation destroy-stack command might not need variables
        pass
    logString = "---------------------------------------------------------------------------------------------------------------"
    logWriter.writeLogVerbose("acm", logString)
  operation = 'off'
  #add code to confirm that output operation succeeded.
  #Also, if output showed there is no network foundation, then skip the rest of the off operations because there would be nothing to off in that case.
  typeParent = 'systems'
#  quit('gogo')
  for typeName in typesToDestroy:
    if typeName != "networkFoundation" and (typeName != "subnetForBuilds") and (typeName != "images"):
      changes_manifest.updateStartOfAServiceType(level, systemInstanceName, typeName)
      #changes_taxonomy.updateTheTaxonomy(systemInstanceName, "systems", typeName, None, "In Process")
      instanceNames = config_fileprocessor.getSystemInstanceNames(infraConfigFileAndPath, typeName)
      for instName in instanceNames:
        changes_manifest.updateStartOfAnInstanceOfAServiceType(level, systemInstanceName, typeName, instName)
        if (test==True) and (typeOfTest=="workflow"):
          pass
        else:
          preprocessor = config_fileprocessor.getPreProcessor(infraConfigFileAndPath, 'serviceInstance', typeName, instName)
          if preprocessor:
            print('preprocessor is: ', str(preprocessor))
      #      quit('Hi!')
            command_runner.runPreOrPostProcessor(preprocessor, 'off')
          else:
            print('NO preprocessor present.')
            pass
          instanceTool = config_fileprocessor.getSystemPropertyValue(infraConfigFileAndPath, typeName, instName, 'tool')
          if typeName == 'projects':
            controller_azdoproject.offProject(systemInstanceName, instName, infraConfigFileAndPath, keyDir)
          else:
#            quit("oh!")
            if instanceTool == 'arm':
              controller_arm.destroyDeployment(systemInstanceName, keyDir, infraConfigFileAndPath, 'serviceInstance', typeName, instName)
            elif instanceTool == 'terraform':
              controller_terraform.terraformCrudOperation(operation, systemInstanceName, keyDir, infraConfigFileAndPath, typeParent, typeName, None, None, instName)
              if command_runner.terraformResult == "Destroyed": 
                logString = "off operation succeeded.  Now inside Python conditional block to do only after the off operation has succeeded. "
                logWriter.writeLogVerbose("acm", logString)
              else:
                logString = "Error: off operation failed.  "
                logWriter.writeLogVerbose("acm", logString)
                sys.exit(1)
            elif instanceTool == 'cloudformation':
              controller_cf.destroyStack(infraConfigFileAndPath, keyDir, 'serviceInstance', typeName, instName)
            else:
              logString = "Error: The value selected for instanceTool is not supportd:  "+instanceTool
              logWriter.writeLogVerbose("acm", logString)
              sys.exit(1)
          postprocessor = config_fileprocessor.getPostProcessor(infraConfigFileAndPath, 'serviceInstance', typeName, instName)
          if postprocessor:
            print('postprocessor is: ', str(postprocessor))
            command_runner.runPreOrPostProcessor(postprocessor, 'off')
          else:
            print('NO postprocessor present.')
            pass
        changes_manifest.updateEndOfAnInstanceOfAServiceType(level, systemInstanceName, typeName, instName)
      changes_manifest.updateEndOfAServiceType(level, systemInstanceName, typeName)
      logString = "done with -- " + typeName + " -----------------------------------------------------------------------------"
      logWriter.writeLogVerbose("acm", logString)
#..
  #Marking the releaseDefinitions as deleted in the changes_manifest because we are assuming that the containing projects have been deleted and have therefore caused the releaseDefinitions to be deleted in the --force operation.  But if your systemConfig is not correct, then the releaseDefinitions might still exist.  Check your systems and your config manually to validate your process.  
  if (isReleaseDef == True):
    if useTheForce:
      if checkDestroyType('projects', infraConfigFileAndPath):
        changes_manifest.updateStartOfAServiceType(level, systemInstanceName, 'releaseDefinitions')
        instanceNames = config_fileprocessor.getSystemInstanceNames(infraConfigFileAndPath, 'releaseDefinitions')
        for instName in instanceNames:
          changes_manifest.updateStartOfAnInstanceOfAServiceType(level, systemInstanceName, 'releaseDefinitions', instName)
          changes_manifest.updateEndOfAnInstanceOfAServiceType(level, systemInstanceName, 'releaseDefinitions', instName)
        changes_manifest.updateEndOfAServiceType(level, systemInstanceName, 'releaseDefinitions')


def skipServices(level, systemInstanceName, keyDir, yamlInfraConfig = 'default'):
  test = config_cliprocessor.inputVars.get("test")
  typeOfTest = config_cliprocessor.inputVars.get("testType")
  infraConfigFileAndPath = yamlInfraConfig
  typesToSkip = config_fileprocessor.listTypesInSystem(infraConfigFileAndPath)
  typeParent = 'systems'
  for typeName in typesToSkip:
    logString = "All services of type " + typeName + "are being marked as completed because you used the --force flag in your command.  This block of code is not actually deleting those resources because the program will destroy the network foundation that you defined, which should destroy these services as part of the cascading foundation delete.  If these services remain after you run this operation during development, then change your configuration so that these services will be bundled within your network foundation's cascading delete. "
    logWriter.writeLogVerbose("acm", logString)
#    changes_taxonomy.updateTheTaxonomy(systemInstanceName, None, "services", None, "In Process")
    changes_manifest.updateStartOfAServiceType(level, systemInstanceName, typeName)
    instanceNames = config_fileprocessor.getSystemInstanceNames(infraConfigFileAndPath, typeName)
    for instanceName in instanceNames: 
      changes_manifest.updateStartOfAnInstanceOfAServiceType(level, systemInstanceName, typeName, instanceName)
      #changes_taxonomy.updateTheTaxonomy(systemInstanceName, typeParent, typeName, instanceName, "In Process")
      #changes_taxonomy.updateTheTaxonomy(systemInstanceName, typeParent, typeName, instanceName, "Completed")
      if (test==True) and (typeOfTest=="workflow"):
        pass
      else:
        outputDir = config_keysassembler.getOutputDir(instanceName)
        shutil.rmtree(outputDir)
      changes_manifest.updateEndOfAnInstanceOfAServiceType(level, systemInstanceName, typeName, instanceName)
#    changes_taxonomy.updateTheTaxonomy(systemInstanceName, "systems", typeName, None, "Completed")
#    changes_taxonomy.updateTheTaxonomy(systemInstanceName, None, "services", None, "Completed")
    changes_manifest.updateEndOfAServiceType(level, systemInstanceName, typeName)

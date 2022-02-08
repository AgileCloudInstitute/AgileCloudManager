## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import os
import config_fileprocessor
import controller_packer
import command_runner
import logWriter
import command_builder

def buildImages(systemInstanceName, infraConfigFileAndPath, operation, keyDir):
  app_parent_path = os.path.dirname(os.path.realpath("..\\")) + '\\'
  app_parent_path = command_builder.formatPathForOS(app_parent_path)
  operation = 'on'
  ###Next Build The Images
  imageSpecs = config_fileprocessor.getImageSpecs(infraConfigFileAndPath)
  typesToFilterImagesFrom = config_fileprocessor.listTypesInImageBuilds(infraConfigFileAndPath)
  for imageTypeName in typesToFilterImagesFrom:
    if imageTypeName == "images":
#      logWriter.updateTheTaxonomy(systemInstanceName, None, "imageBuilds", None, "In Process")
      instanceNames = config_fileprocessor.getImageInstanceNames(infraConfigFileAndPath, imageTypeName)
      operation = 'build'
      controller_packer.packerCrudOperation(operation, systemInstanceName, keyDir, imageTypeName, instanceNames, infraConfigFileAndPath)
      if command_runner.success_packer == 'true':
        logString = "done with -- " + imageTypeName + " -----------------------------------------------------------------------------"
        logWriter.writeLogVerbose("acm", logString)
      else:
        logString = "Failed Packer Build.  Stopping program so you can diagnose the problem. "
        logWriter.writeLogVerbose("acm", logString)
        sys.exit(1)

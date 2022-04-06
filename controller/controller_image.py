## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import os
import sys
import yaml
import datetime
import time
import config_fileprocessor
import controller_packer
import logWriter
import command_builder
import command_runner
import controller_cf

imageIsAvailable = False

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
      for instName in instanceNames:
        instanceTool = config_fileprocessor.getImagePropertyValue(infraConfigFileAndPath, imageTypeName, instName, 'tool')
        if instanceTool == 'packer':
          operation = 'build'
          controller_packer.packerCrudOperation(operation, systemInstanceName, keyDir, imageTypeName, instName, infraConfigFileAndPath)
        elif instanceTool == 'cloudformation':
          controller_cf.createStack(infraConfigFileAndPath, keyDir, 'image', 'images', instName)
          region = config_fileprocessor.getTopLevelProperty(infraConfigFileAndPath, 'networkFoundation', 'region')
          stackName = config_fileprocessor.getImagePropertyValue(infraConfigFileAndPath, imageTypeName, instName, 'stackName')
          getImgIdCmd = 'aws cloudformation --region '+region+' describe-stacks --stack-name '+stackName
          logString = 'getImgIdCmd is: '+ getImgIdCmd
          logWriter.writeLogVerbose("acm", logString)
          jsonStatus = command_runner.getShellJsonResponse(getImgIdCmd)
          logString = 'getImgIdCmd response is: '+ str(jsonStatus)
          logWriter.writeLogVerbose("acm", logString)
          stacks = yaml.safe_load(jsonStatus)['Stacks']
          stackCounter = 0
          for stack in stacks:
            if (stack['StackName'] == stackName) and (stack['StackStatus'] == 'CREATE_COMPLETE'):
              stackCounter += 1
              val = 'empty'
              dateTimeCode = str(datetime.datetime.now()).replace(' ','').replace('-','').replace(':','').replace('.','')
              imgName = instName+'_'+dateTimeCode
              for outputVar in stack['Outputs']:
                if outputVar['OutputKey'] == 'EC2InstanceId':
                  val = outputVar['OutputValue']
              if val == 'empty':
                logString = 'Failed to retrieve instance id from stack: '+stackName
                logWriter.writeLogVerbose("acm", logString)
                sys.exit(1)
              createImageCmd = 'aws ec2 create-image --instance-id '+val+' --name '+imgName
              logString = 'createImageCmd is: '+ createImageCmd
              logWriter.writeLogVerbose("acm", logString)
              createImageJsonStatus = command_runner.getShellJsonResponse(createImageCmd)
              logString = 'createImageCmd response is: '+ str(createImageJsonStatus)
              logWriter.writeLogVerbose("acm", logString)
              amiData = yaml.safe_load(createImageJsonStatus)
              logString = 'AMI being created has id: '+ str(amiData['ImageId'])
              logWriter.writeLogVerbose("acm", logString)
              getAmiByIdCmd =  'aws ec2 describe-images --region '+region+' --image-ids '+amiData['ImageId']
              logString = 'getAmiByIdCmd is: '+ getAmiByIdCmd
              logWriter.writeLogVerbose("acm", logString)
              getAmiByIdJsonStatus = yaml.safe_load(command_runner.getShellJsonResponse(getAmiByIdCmd))
              logString = 'Number of AMIs with id '+amiData['ImageId']+' returned is '+str(len(getAmiByIdJsonStatus))
              logWriter.writeLogVerbose("acm", logString)
              if len(getAmiByIdJsonStatus) > 1:
                logString = 'ERROR: More than one AMI returned with ID.'
                logWriter.writeLogVerbose("acm", logString)
                sys.exit(1)
              isNewAmiAvailable(getAmiByIdCmd, getAmiByIdJsonStatus, 0)
              global imageIsAvailable
              if imageIsAvailable:
                logString = 'SUCCESS: new ami with id '+amiData['ImageId']+' has been successfully created'
                logWriter.writeLogVerbose("acm", logString)
              else:
                logString = 'xx .. ERROR: Image with id '+amiData['ImageId']+' failed to become available.  Halting program so you can examine what went wrong. ' 
                logWriter.writeLogVerbose("acm", logString)
                sys.exit(1)
              imageIsAvailable = False
          if stackCounter > 1:
            logString = 'ERROR: Only one stack with name '+stackName+'should have status CREATE_COMPLETE, but there are: '+str(stackCounter) 
            logWriter.writeLogVerbose("acm", logString)
            sys.exit(1)
          controller_cf.destroyStack(infraConfigFileAndPath, keyDir, 'image', 'images', instName)
        else:
          logString = "Your config file specified an image build tool not supported: "+instanceTool+" . Halting program so you can check your configuration."
          logWriter.writeLogVerbose("acm", logString)
          sys.exit(1)

def isNewAmiAvailable(getAmiByIdCmd, responseJson, counter):
  if counter < 50:
    for image in responseJson['Images']:
      logString = "image['State'] is: "+image['State']
      logWriter.writeLogVerbose("acm", logString)
      if image['State'] == 'available':
        global imageIsAvailable
        imageIsAvailable = True
        return
      elif image['State'] == 'pending': 
        counter += 1
        logString = 'State of image with id '+image['ImageId']+' is: '+image['State']+' . Going to sleep 30 seconds and then retry attempt number: '+str(counter)
        logWriter.writeLogVerbose("acm", logString)
        time.sleep(30)
        getAmiByIdJsonStatus = yaml.safe_load(command_runner.getShellJsonResponse(getAmiByIdCmd))
        logString = 'Number of AMIs returned is '+str(len(getAmiByIdJsonStatus))
        logWriter.writeLogVerbose("acm", logString)
        if len(getAmiByIdJsonStatus) > 1:
          logString = 'ERROR: More than one AMI returned with ID.'
          logWriter.writeLogVerbose("acm", logString)
          sys.exit(1)
        isNewAmiAvailable(getAmiByIdCmd, getAmiByIdJsonStatus, counter)
      else: 
        logString = 'State of image with id '+image['ImageId']+' is: '+image['State']+' . Halting program so you can examine what happened. '
        logWriter.writeLogVerbose("acm", logString)
        sys.exit(1)
  else:
    logString = 'ERROR: Image failed to become avalable after '+str(counter)+' attempts.  Halting program so you can examine what went wrong. '
    sys.exit(1)

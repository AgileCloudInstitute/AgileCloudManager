## Copyright 2024 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    
  
import yaml
import sys
import time
import datetime
import subprocess
import os

from command_runner import command_runner
from command_builder import command_builder
from command_formatter import command_formatter
from config_fileprocessor import config_fileprocessor
from log_writer import log_writer

class controller_cf:
  
  def __init__(self):  
    pass
   
  #@public
  def createStack(self, systemConfig, instance, keyDir, caller, serviceType, instName):
    import config_cliprocessor
    cfp = config_fileprocessor()
    #NOTE: THIS SETS THE REGION SEPARATELY FOR ANY INSTANCE THAT DEFINES A region KEY, AND THEN DEFAULTS TO THE FOUNDATION'S region KEY IF THERE IS NO region KEY IN ANY GIVEN INSTANCE. 
    region = None
    if "region" in instance.keys():
      region = instance.get("region")
    if region == None:
      if "foundation" in systemConfig.keys():
        region = systemConfig.get("foundation").get("region")
      else:
        logString = "ERROR: There is no key named 'region' in either the instance or in the foundation of your system config file. "
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    if region.startswith("$config"):
      region = cfp.getValueFromConfig(keyDir, region, "region")
    self.configureSecrets(keyDir, region)
    ## STEP 1: Populate variables
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    outputDict = {}
    if caller == 'networkFoundation':
      serviceType = 'networkFoundation'
      templateName = instance.get("templateName")
      stackName = instance.get("stackName")
    elif caller == 'serviceInstance':
      templateName = instance.get("templateName")
      stackName = instance.get("stackName")
      imageName = instance.get("imageName")
      if imageName:
        if imageName.startswith("$config"):
          imageName = cfp.getValueFromConfig(keyDir, imageName, "imageName")
        outputDict['ImageNameRoot'] = imageName
    elif caller == 'image':
      templateName = instance.get("templateName")
      stackName = instance.get("stackName")
    if stackName.startswith("$config"):
      stackName = cfp.getValueFromConfig(keyDir, stackName, "stackName")

    cb = command_builder()
    cf = command_formatter()
    deployVarsFragment = cb.getVarsFragment(systemConfig, serviceType, instance, instance.get('mappedVariables'), 'cloudformation', self, outputDict)
    cfTemplateFileAndPath = userCallingDir+templateName
    cfTemplateFileAndPath = cf.formatPathForOS(cfTemplateFileAndPath)
    self.configureSecrets(keyDir,region)

    lw = log_writer()

    ## STEP 2: Check to see if stack already exists
    checkExistCmd = 'aws cloudformation describe-stacks --stack-name '+stackName + ' --region '+region
    logString = "checkExistCmd is: "+checkExistCmd
    lw.writeLogVerbose("acm", logString)
    cr = command_runner()
    if self.checkIfStackExists(checkExistCmd):
      createChangeSetCommand = 'aws cloudformation create-change-set --change-set-name my-change --stack-name '+stackName+' --template-body file://'+cfTemplateFileAndPath+' '+str(deployVarsFragment)+' --output text --query Id '
      print("instance is: ", instance)
      capString = self.getCapabilities(instance)
      if capString != '':
        createChangeSetCommand = createChangeSetCommand+capString
      logString = 'createChangeSetCommand is: '+createChangeSetCommand
      lw.writeLogVerbose("acm", logString)
      jsonStatus = cr.getShellJsonResponse(createChangeSetCommand)
      logString = 'Initial response from stack command is: '+str(jsonStatus)
      lw.writeLogVerbose("acm", logString)
      describeChangesCmd = 'aws cloudformation describe-change-set --change-set-name '+str(jsonStatus)
      logString = 'describeChangesCmd is: '+ describeChangesCmd
      lw.writeLogVerbose("acm", logString)
      jsonStatus = cr.getShellJsonResponse(describeChangesCmd)
      logString = 'describeChangesCmd response is: ', str(jsonStatus)
      lw.writeLogVerbose("acm", logString)
      jsonStatus = yaml.safe_load(jsonStatus)
      respStatus = jsonStatus['Status']
      changeSetId = jsonStatus['ChangeSetId']
      logString = 'describeChangesCmd response Status is: ', str(respStatus)
      lw.writeLogVerbose("acm", logString)
      logString = 'changeSetId is: '+ changeSetId
      lw.writeLogVerbose("acm", logString)
      deleteChangeSetCmd = 'aws cloudformation delete-change-set --change-set-name '+str(changeSetId)
      logString = "deleteChangeSetCmd is: " + deleteChangeSetCmd
      lw.writeLogVerbose("acm", logString)
      jsonStatus = cr.getShellJsonResponse(deleteChangeSetCmd)
      logString = 'deleteChangeSetCmd response is: ', str(jsonStatus)
      lw.writeLogVerbose("acm", logString)
      if respStatus == 'FAILED':
        logString = 'WARNING: There are NO changes to make, so we are returning without creating or updating the stack. '
        lw.writeLogVerbose("acm", logString)
        return
      elif respStatus == 'CREATE_COMPLETE':
        print("instance is: ", instance)
        cfDeployCommand = 'aws cloudformation update-stack --stack-name '+stackName+' --template-body file://'+cfTemplateFileAndPath+' '+str(deployVarsFragment)
        capString = self.getCapabilities(instance)
        if capString != '':
          cfDeployCommand = cfDeployCommand+capString
        logString = 'Response from check existance of stack command is: True'
        lw.writeLogVerbose("acm", logString)
        logString = "cfDeployCommand is: "+cfDeployCommand
        lw.writeLogVerbose("acm", logString)
        jsonStatus = cr.getShellJsonResponse(cfDeployCommand)
        logString = 'Initial response from stack command is: ', str(jsonStatus)
        lw.writeLogVerbose("acm", logString)
        ## Check status of deployment repeatedly until deployment has completed.
        if not self.checkStatusOfStackCommand('update', stackName):
          logString = 'ERROR: Stack update command failed.'
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
      else:
        logString = "ERROR: The aws cloudformation describe-change-set command returned a value that was not either FAILED or CREATE_COMPLETE .  Halting the program so that you can debug the cause of the problem."
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    else:
      cfDeployCommand = 'aws cloudformation create-stack --stack-name '+stackName+' --template-body file://'+cfTemplateFileAndPath+' '+str(deployVarsFragment)
      capString = self.getCapabilities(instance)
      if capString != '':
        cfDeployCommand = cfDeployCommand+capString
      logString = 'Response from check existance of stack command is: False'
      lw.writeLogVerbose("acm", logString)
      logString = 'cfDeployCommand is: '+cfDeployCommand
      lw.writeLogVerbose("acm", logString)
      jsonStatus = cr.getShellJsonResponse(cfDeployCommand)
      logString = 'Initial response from stack command is: '+ str(jsonStatus)
      lw.writeLogVerbose("acm", logString)
      ## Check status of deployment repeatedly until deployment has completed.
      if not self.checkStatusOfStackCommand('create', stackName):
        logString = 'ERROR: Stack create command failed.'
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    self.destroySecrets()

  #@private
  def getCapabilities(self, instance):
    capString = ''
    rootStr = ' --capabilities'
    if (instance.get("controller") == "cloudformation") and ("capabilities" in instance.keys()):
      for cap in instance.get("capabilities"):
        spaceCap = ' '+cap
        capString += spaceCap
    if capString != None:
      capString = rootStr+capString
    return capString

  #@public
  def destroyStack(self, systemConfig, instance, keyDir, caller):
    import config_cliprocessor
    cr = command_runner()
    cf = command_formatter()
    lw = log_writer()
    cfp = config_fileprocessor()
    #NOTE: THIS SETS THE REGION SEPARATELY FOR ANY INSTANCE THAT DEFINES A region KEY, AND THEN DEFAULTS TO THE FOUNDATION'S region KEY IF THERE IS NO region KEY IN ANY GIVEN INSTANCE. 
    region = None
    if "region" in instance.keys():
      region = instance.get("region")
    if region == None:
      if "foundation" in systemConfig.keys():
        region = systemConfig.get("foundation").get("region")
      else:
        logString = "ERROR: There is no key named 'region' in either the instance or in the foundation of your system config file. "
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    if region.startswith("$config"):
      region = cfp.getValueFromConfig(keyDir, region, "region")
    if region.startswith("$config"):
      region = cfp.getValueFromConfig(keyDir, region, "region")
    self.configureSecrets(keyDir,region)
    ## STEP 1: Populate variables
    app_parent_path = config_cliprocessor.inputVars.get('app_parent_path')
    if caller == 'networkFoundation':
      templateName = systemConfig.get("foundation").get("templateName")
      stackName = systemConfig.get("foundation").get("stackName")
    elif caller == 'serviceInstance':
      templateName = instance.get("templateName")
      stackName = instance.get("stackName")
    elif caller == 'image':
      templateName = instance.get("templateName")
      stackName = instance.get("stackName")

    if stackName.startswith("$config"):
      stackName = cfp.getValueFromConfig(keyDir, stackName, "stackName")
    
    thisStackId = self.getStackId(stackName)
    logString = 'thisStackId is: '+ thisStackId
    lw.writeLogVerbose("acm", logString)
    if caller == 'networkFoundation':
      if "images" in systemConfig.get("foundation").keys():
        self.deleteImagesAndSnapshots(region, thisStackId, systemConfig, keyDir)
    if thisStackId == 'none':
      logString = 'WARNING: No stacks with the name '+stackName+' are currently in the CREATE_COMPLETE state when this run is initiated.  We are therefore skipping the delete process for this stack and continuing the program flow to proceed with any downstream steps.  '
      lw.writeLogVerbose("acm", logString)
    else:
      ## STEP 2: Assemble and run deployment command
      cfTemplateFileAndPath = app_parent_path+templateName
      cfTemplateFileAndPath = cf.formatPathForOS(cfTemplateFileAndPath)
      cfDeployCommand = 'aws cloudformation delete-stack --stack-name '+stackName
      logString = 'cfDeployCommand to delete is: '+cfDeployCommand 
      lw.writeLogVerbose("acm", logString)
      jsonStatus = cr.getShellJsonResponse(cfDeployCommand)
      logString = 'Initial response from stack command is: '+ str(jsonStatus)
      lw.writeLogVerbose("acm", logString)
      self.trackStackProgress(thisStackId, region)
    self.destroySecrets()

  #@private
  def deleteImagesAndSnapshots(self, region, thisStackId, systemConfig, keyDir, counter=0):
    lw = log_writer()
    cr = command_runner()
    cfp = config_fileprocessor()
    #Get AWS user id and image name root for use in subsequent cli commands
    if isinstance(thisStackId, str):
      if (":" in thisStackId) and (thisStackId.count(":")==5):
        awsUserId = thisStackId.split(":")[4]
        if (awsUserId.isdigit()) and (len(awsUserId)==12):
          if "images" in systemConfig.get("foundation").keys():
            for image in systemConfig.get("foundation").get("images"):
              imageNameRoot = image.get("imageName")
              if imageNameRoot.startswith("$config"): 
                imageNameRoot = cfp.getValueFromConfig(keyDir, imageNameRoot, "imageName")
        else:
          logString = "ERROR: aws user id is malformed: "+awsUserId
          lw.writeLogVerbose("acm", logString)
          exit(1)
      else:
        logString = "ERROR: Malformed stack id does not contain 5 instances colon separator character : "+thisStackId
        lw.writeLogVerbose("acm", logString)
        exit(1)
    else:
      logString = "ERROR: StackId is not a string."
      lw.writeLogVerbose("acm", logString)
    
    # 1. Return image id and snapshot id for each of all images that contain root name and that were created by current user
    getImageAndSnapshotIdsCommand='aws ec2 describe-images --owners '+awsUserId+' --filters "Name=name,Values='+imageNameRoot+'*" --query "Images[*].[ImageId,BlockDeviceMappings[].Ebs[].SnapshotId]"[] --no-paginate'
    logString = "getImageAndSnapshotIdsCommand is: "+getImageAndSnapshotIdsCommand
    lw.writeLogVerbose("acm", logString)
    jsonResponse = cr.getShellJsonResponse(getImageAndSnapshotIdsCommand)
    responseData = yaml.safe_load(jsonResponse)
    if len(responseData) == 0:
      logString = "INFO: No images or snapshots were returned that included the characters "+imageNameRoot+" and that are owned by the user with user id "+awsUserId
      lw.writeLogVerbose("acm", logString)
    else:
      logString = "Number of items image and snapshot ids list is: "+str(len(responseData))
      lw.writeLogVerbose("acm", logString)
      imageIdsList = []
      snapshotsIdsList = []
      for item in responseData:
        if type(item) == str:
          if item.startswith("ami-"):
            imageIdsList.append(item)
        elif type(item) == list:
          for snapshot in item:
            if snapshot.startswith("snap-"):
              snapshotsIdsList.append(snapshot)
      # 2. Deregister each image by id
      logString = "About to deregister each image by looping through the following list of image ids: "+str(imageIdsList)
      lw.writeLogVerbose("acm", logString)
      for thisImageId in imageIdsList:
        deregisterImageCommand = "aws ec2 deregister-image --image-id "+thisImageId
        logString = "deregisterImageCommand is: "+deregisterImageCommand
        lw.writeLogVerbose("acm", logString)
        imgDeregResponse = cr.getShellJsonResponse(deregisterImageCommand)
        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        logString = "Response returned by running deregisterImageCommand is: "+str(imgDeregResponse)
        lw.writeLogVerbose("acm", logString)
        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
      
      # 4. Delete snapshot by id
      logString = "About to delete each snapshot by looping through the following list of snapshot ids: "+str(snapshotsIdsList)
      lw.writeLogVerbose("acm", logString)
      for thisSnapshotId in snapshotsIdsList:
        deleteSnapshotCommand = "aws ec2 delete-snapshot --snapshot-id "+thisSnapshotId
        logString = "deleteSnapshotCommand is: "+deleteSnapshotCommand
        lw.writeLogVerbose("acm", logString)
        snapDeleteResponse = cr.getShellJsonResponse(deleteSnapshotCommand)
        print("----------------------------------------------------------------")
        logString = "Response returned by running deleteSnapshotCommand is: "+str(snapDeleteResponse)
        lw.writeLogVerbose("acm", logString)
        print("----------------------------------------------------------------")
    
    # 5. Return image id and snapshot id for each of all images that contain root name and that were created by current user
    responseData = self.getImageAndSnapshotIds(awsUserId, imageNameRoot)
    print("len(responseData) is: ", str(len(responseData)))
    if len(responseData) != 0:
      if counter < 5:
        counter += 1
        logString = "Sleeping 30 seconds because deletions of snapshots and images have not yet been reported in the AWS portal. "
        lw.writeLogVerbose("acm", logString)
        responseData = self.getImageAndSnapshotIds(awsUserId, imageNameRoot)
        if len(responseData) != 0:
          logString = "About to re-run the delete images and snapshots function.  Attempt number "+counter+". "  
          lw.writeLogVerbose("acm", logString)  
          self.deleteImagesAndSnapshots(region, thisStackId, systemConfig, keyDir, counter)  
      else:
        logString = "ERROR: There are still images and snapshots whose names start with "+imageNameRoot+" that are owned by the current user.  "
        lw.writeLogVerbose("acm", logString)
        exit(1)

  #@private
  def getImageAndSnapshotIds(self, awsUserId, imageNameRoot):
    lw = log_writer()
    cr = command_runner()
    logString = "About to check to confirm whether or not the images and snapshots have been deleted whose names start with "+imageNameRoot+"  have been deleted. "
    lw.writeLogVerbose("acm", logString)  
    getImageAndSnapshotIdsCommand='aws ec2 describe-images --owners '+awsUserId+' --filters "Name=name,Values='+imageNameRoot+'*" --query "Images[*].[ImageId,BlockDeviceMappings[].Ebs[].SnapshotId]"[] --no-paginate'
    logString = "getImageAndSnapshotIdsCommand is: "+getImageAndSnapshotIdsCommand
    lw.writeLogVerbose("acm", logString)
    jsonResponse = cr.getShellJsonResponse(getImageAndSnapshotIdsCommand)
    responseData = yaml.safe_load(jsonResponse)
    return responseData

  #@private
  def trackStackProgress(self, stackId, region):
    cr = command_runner()
    lw = log_writer()
    thisStatus = 'empty'
    n=0
    while thisStatus!='DELETE_COMPLETE':
      checkCmd = 'aws cloudformation describe-stacks --stack-name '+stackId + ' --region '+region
      logString = 'checkCmd to describe stacks is: '+checkCmd
      lw.writeLogVerbose("acm", logString)
      jsonStatus = cr.getShellJsonResponse(checkCmd)
      responseData = yaml.safe_load(jsonStatus)
      for item in responseData['Stacks']:
        status = item['StackStatus']
        aStackId = item['StackId']
        if stackId == aStackId:
          thisStatus = status
          if status == 'DELETE_COMPLETE':
            logString = "Delete operation completed on stack."
            lw.writeLogVerbose("acm", logString)
            return
      n+=1
      if n>15:
        keepGoing = False
        for item in responseData['Stacks']:
          status = item['StackStatus']
          aStackId = item['StackId']
          if stackId == aStackId:
            thisStatus = status
            if status == 'DELETE_IN_PROGRESS':
              logString = "INFO: Delete operation is continuing to run on stack, but is taking longer than expected."
              lw.writeLogVerbose("acm", logString)
              keepGoing = True
        if not keepGoing:
          logString = "ERROR:  Quitting because operation failed to complete after " + str(n) + " attempts. "
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
      logString = "Operation still in process.  About to sleep 30 seconds before trying progress check number: " + str(n)
      lw.writeLogVerbose("acm", logString)
      time.sleep(30)
    return

  #@private
  def getStackId(self, stackName):
    cr = command_runner()
    lw = log_writer()
    idToReturn = 'none'
    checkCmd = 'aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE'
    jsonStatus = cr.getShellJsonResponse(checkCmd)
    responseData = yaml.safe_load(jsonStatus)
    for item in responseData['StackSummaries']:
      name = item['StackName']
      status = item['StackStatus']
      stackId = item['StackId']
      if (name == stackName) and (status == 'CREATE_COMPLETE'):
        logString = name+ ' : '+ status+ ' : '+ stackId
        lw.writeLogVerbose("acm", logString)
        idToReturn = stackId
    if idToReturn != 'none':
      return idToReturn
    else:
      checkCmd = 'aws cloudformation list-stacks --stack-status-filter DELETE_FAILED'
      jsonStatus = cr.getShellJsonResponse(checkCmd)
      responseData = yaml.safe_load(jsonStatus)
      for item in responseData['StackSummaries']:
        name = item['StackName']
        status = item['StackStatus']
        stackId = item['StackId']
        if (name == stackName) and (status == 'DELETE_FAILED'):
          logString = name+ ' : '+ status+ ' : '+ stackId
          lw.writeLogVerbose("acm", logString)
          idToReturn = stackId
      return idToReturn

  #@private
  def checkStatusOfStackCommand(self, operation, stackName):
    cr = command_runner()
    lw = log_writer()
    counter = 0
    status = 'NOT_STARTED'
    logicalResourceId = 'empty'
    if operation == 'create':
      successStatus = 'CREATE_COMPLETE'
    elif operation == 'update':
      successStatus = 'UPDATE_COMPLETE'
    elif operation == 'destroy':
      successStatus = 'DELETE_COMPLETE'
    failureStatus = 'ROLLBACK_COMPLETE'
    while (status != successStatus) or(status != failureStatus):
      cfStatusCommand = 'aws cloudformation describe-stack-events --stack-name '+stackName
      logString = 'cfStatusCommand to describe stack events is: '+cfStatusCommand
      lw.writeLogVerbose("acm", logString)
      jsonStatus = cr.getShellJsonResponse(cfStatusCommand)
      responseYaml = yaml.safe_load(jsonStatus)
      for event in responseYaml['StackEvents']:
        for eventItem in event:
          if eventItem == 'ResourceType':
            if event[eventItem] == 'AWS::CloudFormation::Stack':
              logicalResourceId = event['LogicalResourceId']
              status = event['ResourceStatus']
              counter +=1
              logString = 'Matching event number: '+ str(counter)
              lw.writeLogVerbose("acm", logString)
              if (status == successStatus) and (logicalResourceId == stackName):
                logString = "... Stack Completed!"
                lw.writeLogVerbose("acm", logString)
                return True
              elif (status == failureStatus) and (logicalResourceId == stackName):
                logString = "... Stack failed with status ROLLBACK_COMPLETE !"
                lw.writeLogVerbose("acm", logString)
                return False
      #Wait before each re-try to allow remote process enough time to complete.
      time.sleep(15)
    return False

  #@private
  def checkIfStackExists(self, cmd,counter=0):
    lw = log_writer()
    process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
    data = process.stdout
    err = process.stderr
    try:
      if process:
        data, err = process.communicate()
        if process.returncode != 0:
          print("ERROR: The subprocess command returned a non-zero return code: ", process.returncode)
    except AttributeError: #This should handle CompletedpProcess error.  
      pass
    logString = "data string is: " + str(data)
    lw.writeLogVerbose("acm", logString)
    logString = "err is: " + str(err)
    lw.writeLogVerbose("acm", logString)
    logString = "process.returncode is: " + str(process.returncode)
    lw.writeLogVerbose("acm", logString)
    if process.returncode == 0:
      logString = str(data)
      lw.writeLogVerbose("shell", logString)
      return True
    elif (process.returncode == 254) or (process.returncode == '254') or (process.returncode == 255) or (process.returncode == '255'):
      return False
    else:
      if counter == 0:
        counter +=1 
        logString = "Sleeping 30 seconds before running the command a second time in case a latency problem caused the first attempt to fail. "
        lw.writeLogVerbose('acm', logString)
        import time
        time.sleep(30)
        self.checkIfStackExists(cmd,counter)
      else:
        logString = "Error: " + str(err)
        lw.writeLogVerbose("shell", logString)
        logString = "Error: Return Code is: " + str(process.returncode)
        lw.writeLogVerbose("shell", logString)
        logString = "ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem."
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
 
  #@private
  def configureSecrets(self, keyDir,region): 
    cf = command_formatter()
    keyDir = cf.formatKeyDir(keyDir)
    sourceKeysFile = keyDir + "keys.yaml"
    cfp = config_fileprocessor()
    #get the source variables into a new array
    if os.path.isfile(sourceKeysFile):
      AWSAccessKeyId = cfp.getFirstLevelValue(sourceKeysFile, 'AWSAccessKeyId')
      AWSSecretKey = cfp.getFirstLevelValue(sourceKeysFile, 'AWSSecretKey')
      outputDir = cf.formatPathForOS(os.path.expanduser('~/.aws'))
      if not os.path.isdir(outputDir):
        os.mkdir(outputDir)
      fileName = outputDir+'/credentials'
      with open(fileName, 'w') as f:
        defaultLine = '[default]\n'
        f.write(defaultLine)
        idLine = 'aws_access_key_id='+AWSAccessKeyId+'\n'
        f.write(idLine)
        keyLine = 'aws_secret_access_key='+AWSSecretKey+'\n'
        f.write(keyLine)
      configFileName = outputDir+'/config'
      with open(configFileName, 'w') as f:
        defaultLine = '[default]\n'
        f.write(defaultLine)
        regionLine = 'region='+region+'\n'
        f.write(regionLine)
    else:
      logString = "ERROR: "+sourceKeysFile+" is not a valid path. "
      print(logString)
      sys.exit(1)

  #@private
  def destroySecrets(self):
    cf = command_formatter()
    filename = cf.formatPathForOS(os.path.expanduser('~/.aws') + '/credentials')
    try:
      os.remove(filename)
    except OSError:
      pass
    filename = cf.formatPathForOS(os.path.expanduser('~/.aws') + '/config')
    try:
      os.remove(filename)
    except OSError:
      pass

  #@public
  def buildCloudFormationImage(self, systemConfig, image, keyDir):
    cr = command_runner()
    lw = log_writer()
    cfp = config_fileprocessor()
    self.createStack(systemConfig, image, keyDir, 'image', 'images', image.get("instanceName"))
    region = systemConfig.get("foundation").get("region")
    if region.startswith("$config"):
      region = cfp.getValueFromConfig(keyDir, region, "region")
    stackName = image.get("stackName")
    if stackName.startswith("$config"):
      stackName = cfp.getValueFromConfig(keyDir, stackName, "stackName")
    self.configureSecrets(keyDir,region)
    getImgIdCmd = 'aws cloudformation --region '+region+' describe-stacks --stack-name '+stackName
    logString = 'getImgIdCmd is: '+ getImgIdCmd
    lw.writeLogVerbose("acm", logString)
    jsonStatus = cr.getShellJsonResponse(getImgIdCmd)
    logString = 'getImgIdCmd response is: '+ str(jsonStatus)
    lw.writeLogVerbose("acm", logString)
    stacks = yaml.safe_load(jsonStatus)['Stacks']
    stackCounter = 0
    for stack in stacks:
      if (stack['StackName'] == stackName) and (stack['StackStatus'] == 'CREATE_COMPLETE'):
        stackCounter += 1
        val = 'empty'
        dateTimeCode = str(datetime.datetime.now()).replace(' ','').replace('-','').replace(':','').replace('.','')
        imageNameRoot = image.get("imageName")
        print("i imageNameRoot is: ", imageNameRoot)
        if imageNameRoot.startswith("$config"): 
          imageNameRoot = cfp.getValueFromConfig(keyDir, imageNameRoot, "imageName")
        imgName = imageNameRoot+'_'+dateTimeCode
        for outputVar in stack['Outputs']:
          if outputVar['OutputKey'] == 'EC2InstanceId':
            val = outputVar['OutputValue']
        if val == 'empty':
          logString = 'Failed to retrieve instance id from stack: '+stackName
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
        createImageCmd = 'aws ec2 create-image --instance-id '+val+' --name '+imgName
        logString = 'createImageCmd is: '+ createImageCmd
        lw.writeLogVerbose("acm", logString)
        createImageJsonStatus = cr.getShellJsonResponse(createImageCmd)
        logString = 'createImageCmd response is: '+ str(createImageJsonStatus)
        lw.writeLogVerbose("acm", logString)
        amiData = yaml.safe_load(createImageJsonStatus)
        logString = 'AMI being created has id: '+ str(amiData['ImageId'])
        lw.writeLogVerbose("acm", logString)
        self.configureSecrets(keyDir,region)
        getAmiByIdCmd =  'aws ec2 describe-images --region '+region+' --image-ids '+amiData['ImageId']
        logString = 'getAmiByIdCmd is: '+ getAmiByIdCmd
        lw.writeLogVerbose("acm", logString)
        getAmiByIdJsonStatus = yaml.safe_load(cr.getShellJsonResponse(getAmiByIdCmd))
        logString = 'Number of AMIs with id '+amiData['ImageId']+' returned is '+str(len(getAmiByIdJsonStatus))
        lw.writeLogVerbose("acm", logString)
        if len(getAmiByIdJsonStatus) > 1:
          logString = 'ERROR: More than one AMI returned with ID.'
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
        self.isNewAmiAvailable(getAmiByIdCmd, getAmiByIdJsonStatus, 0)
        global imageIsAvailable
        if imageIsAvailable:
          logString = 'SUCCESS: new ami with id '+amiData['ImageId']+' has been successfully created'
          lw.writeLogVerbose("acm", logString)
        else:
          logString = 'ERROR: Image with id '+amiData['ImageId']+' failed to become available.  Halting program so you can examine what went wrong. ' 
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
        imageIsAvailable = False
    self.destroySecrets()
    if stackCounter > 1:
      logString = 'ERROR: Only one stack with name '+stackName+'should have status CREATE_COMPLETE, but there are: '+str(stackCounter) 
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    self.destroyStack(systemConfig, image, keyDir, 'image')

  #@private
  def isNewAmiAvailable(self, getAmiByIdCmd, responseJson, counter):
    cr = command_runner()
    lw = log_writer()
    if counter < 50:
      for image in responseJson['Images']:
        logString = "image['State'] is: "+image['State']
        lw.writeLogVerbose("acm", logString)
        if image['State'] == 'available':
          global imageIsAvailable
          imageIsAvailable = True
          return
        elif image['State'] == 'pending': 
          counter += 1
          logString = 'State of image with id '+image['ImageId']+' is: '+image['State']+' . Going to sleep 30 seconds and then retry attempt number: '+str(counter)
          lw.writeLogVerbose("acm", logString)
          time.sleep(30)
          getAmiByIdJsonStatus = yaml.safe_load(cr.getShellJsonResponse(getAmiByIdCmd))
          logString = 'Number of AMIs returned is '+str(len(getAmiByIdJsonStatus))
          lw.writeLogVerbose("acm", logString)
          if len(getAmiByIdJsonStatus) > 1:
            logString = 'ERROR: More than one AMI returned with ID.'
            lw.writeLogVerbose("acm", logString)
            sys.exit(1)
          self.isNewAmiAvailable(getAmiByIdCmd, getAmiByIdJsonStatus, counter)
        else: 
          logString = 'State of image with id '+image['ImageId']+' is: '+image['State']+' . Halting program so you can examine what happened. '
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
    else:
      logString = 'ERROR: Image failed to become avalable after '+str(counter)+' attempts.  Halting program so you can examine what went wrong. '
      sys.exit(1)

  #@public
  def getVarFromCloudFormationOutput(self, keyDir, outputVarName, stackName, region):
    cr = command_runner()
    lw = log_writer()
    self.configureSecrets(keyDir,region)
    getOutputsCommand = 'aws cloudformation describe-stacks --stack-name '+stackName + ' --region ' + region
    logString = 'getOutputsCommand is: '+getOutputsCommand
    lw.writeLogVerbose("acm", logString)
    jsonStatus = cr.getShellJsonResponse(getOutputsCommand)
    jsonStatus = yaml.safe_load(jsonStatus)
    stacks = jsonStatus['Stacks']
    for stack in stacks:
      for output in stack['Outputs']:
        if outputVarName == output['OutputKey']:
          self.destroySecrets()
          return output['OutputValue'].replace(' ','')
    self.destroySecrets()
    return 'empty' 

  #@public
  def getMostRecentImage(self, systemConfig, keyDir, outputDict):
    cr = command_runner()
    lw = log_writer() 
    cfp = config_fileprocessor()
    region = systemConfig.get("foundation").get("region")
    if region.startswith("$config"):
      region = cfp.getValueFromConfig(keyDir, region, "region")
    self.configureSecrets(keyDir, region)
    listImagesCommand = 'aws ec2 describe-images --owners self --filters "Name=state,Values=available"'
    logString = 'listImagesCommand is: '+listImagesCommand
    lw.writeLogVerbose("acm", logString)
    jsonStatus = cr.getShellJsonResponse(listImagesCommand)
    logString = 'Initial response from listImagesCommand is: '+str(jsonStatus)
    lw.writeLogVerbose("acm", logString)
    images = yaml.safe_load(jsonStatus)['Images']
    nameRoot = outputDict['ImageNameRoot']
    imageNamesList = []
    datesList = []
    imageNameIdDict = {}
    for image in images:
      if (image['State'] == 'available') and (nameRoot in image['Name']):
        imageNamesList.append(image['Name'])
        imageNameIdDict[image['Name']] = image['ImageId']
    for name in imageNamesList:
      datesList.append(name.split('_')[1])
    mostRecentDate = max(datesList)
    mostRecentImageName = nameRoot+'_'+mostRecentDate
    return imageNameIdDict[mostRecentImageName]

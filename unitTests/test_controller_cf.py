#from msilib.schema import ServiceControl
import unittest
import os
import platform
import os
import shutil
import json
import sys
import pathlib
import time
  
#Run the tests in this file by 
    ## First, navigating the terminal to the folder that is the PARENT of the folder that contains the agile-cloud-manager code.
    ## Second, make sure the directory structure is correct, including sibling directories for required repos, etc. 
    ## Third, running the following command in the terminal:
       #python -m unittest agile-cloud-manager/unit-tests/test_controller_cf.py
  
class TestControllerCf(unittest.TestCase):
  
  def addAcmDirToPath(self):
    acmDir = str(pathlib.Path(__file__).parent.resolve().parent.resolve())+'/app'
    acmDir = self.formatPathForOS(acmDir)
    sys.path.insert(0, acmDir)
  
  def setAcmVariables(self, config_cliprocessor, inputType='sanitized'):
    # If inputType contains a special directory name, then split out that special directory name
    if inputType.count('_') == 1:
      inputParts = inputType.split('_')
      inputType = inputParts[1]

    # inputsDir is where the key files originate.  These will be sourced before you use ACM
    if inputType == 'sanitized':
      inputsDir = str(pathlib.Path(__file__).parent.resolve())+'/input-files'
    elif inputType == 'secret':
      if platform.system() == 'Windows':
        inputsDir = os.path.expanduser('~') + '/acm/keys/starter/'
      elif platform.system() == 'Linux':
        inputsDir = os.path.expanduser('~') + '/acmconfig/'
    else:
      inputsDir = os.path.expanduser('~') + '/acm/keys/'+inputType+'/'
    inputsDir = self.formatPathForOS(inputsDir)
    # acmKeysDir is the staging ground that ACM will use to create and destroy transitory key files during operations.
    acmKeysDir = self.getAcmKeysDir()
    acmKeysDir = self.formatPathForOS(acmKeysDir)
    varsFileAndPath = acmKeysDir+'/keys.tfvars'
    varsFileAndPath = self.formatPathForOS(varsFileAndPath)
    userCallingDir = str(os.path.abspath("."))+'\\'
    userCallingDir = self.formatPathForOS(userCallingDir)
    #Get logsPath
    if platform.system() == 'Windows':
      #putting log into acmKeysDir because this is just a test.
      verboseLogFilePath = acmKeysDir + '/logs'
      verboseLogFilePath = self.formatPathForOS(verboseLogFilePath)
      pathlib.Path(verboseLogFilePath).mkdir(parents=True, exist_ok=True)
    elif platform.system() == 'Linux':
      verboseLogFilePath = '/var/log/acm/'
    dynamicVarsPath = os.path.expanduser('~') + '/acm/dynamicvars/'
    dynamicVarsPath = self.formatPathForOS(dynamicVarsPath)
    if not os.path.exists(dynamicVarsPath):
      os.makedirs(dynamicVarsPath)
    relativePathToInstances = "\\calls-to-modules\\instances\\"
    relativePathToInstances = self.formatPathForOS(relativePathToInstances)
    config_cliprocessor.inputVars['relativePathToInstances'] = relativePathToInstances
    config_cliprocessor.inputVars['dynamicVarsPath'] = dynamicVarsPath
    config_cliprocessor.inputVars['dirOfYamlKeys'] = inputsDir
    if inputType == 'sanitized':
      config_cliprocessor.inputVars['dirOfOutput'] = inputsDir
    elif inputType == 'secret':
      config_cliprocessor.inputVars['dirOfOutput'] = self.formatPathForOS(str(pathlib.Path(inputsDir).parent.resolve())+'/')
    else:
      config_cliprocessor.inputVars['dirOfOutput'] = self.formatPathForOS(str(pathlib.Path(inputsDir).parent.resolve())+'/')
      acmAdmin = userCallingDir + '/acmAdmin'
      acmAdmin = self.formatPathForOS(acmAdmin)
      varsPath = acmAdmin + '/vars'
      tfvarsFileAndPath = varsPath+"\\keys.tfvars"
      tfvarsFileAndPath = self.formatPathForOS(tfvarsFileAndPath)
      tfBackendFileAndPath = varsPath+"/backend.tfvars"
      tfBackendFileAndPath = self.formatPathForOS(tfBackendFileAndPath)
      config_cliprocessor.inputVars["tfBackendFileAndPath"] = tfBackendFileAndPath
      print('tfBackendFileAndPath is: ', tfBackendFileAndPath)
      if platform.system() == 'Windows':
        dependenciesBinariesPath = acmAdmin + '/binaries/'
        dependenciesBinariesPath = self.formatPathForOS(dependenciesBinariesPath)
      elif platform.system() == 'Linux':
        dependenciesBinariesPath = '/opt/acm/'
      config_cliprocessor.inputVars['dependenciesBinariesPath'] = dependenciesBinariesPath
    config_cliprocessor.inputVars["tfvarsFileAndPath"] = varsFileAndPath
    config_cliprocessor.inputVars["userCallingDir"] = userCallingDir
    config_cliprocessor.inputVars["verboseLogFilePath"] = verboseLogFilePath
    path = pathlib.Path(userCallingDir)
    app_parent_path = str(path.parent)+'\\'
    app_parent_path = self.formatPathForOS(app_parent_path)
    config_cliprocessor.inputVars["app_parent_path"] = app_parent_path

  def getPython(self):
    if platform.system() == 'Windows':
      pythonName = 'python'
    elif platform.system() == 'Linux':
      pythonName = 'python3'
    return pythonName

  def getAcmKeysDir(self):
    # This is the staging ground where tests will put key files produced during test operations.
    # This is NOT where the keys will be sourced from.
    if platform.system() == 'Windows':
      acmKeysDir = os.path.expanduser("~")+'/acm/testkeys/'
    elif platform.system() == 'Linux':
      acmKeysDir = '/usr/acm/testkeys/'
    if not os.path.exists(acmKeysDir):
      os.makedirs(acmKeysDir, exist_ok=True) 
    return acmKeysDir
  
  def deleteAcmKeys(self):
    time.sleep(5)
    acmKeysDir = self.getAcmKeysDir()
    acmKeysDir = self.formatPathForOS(acmKeysDir)
    for root, dirs, files in os.walk(acmKeysDir):
      for name in files:
        print('++ ',os.path.join(root, name)) 
        os.remove(os.path.join(root, name))
      for name in dirs:
        print(os.path.join(root, name))
        shutil.rmtree(os.path.join(root, name))
    #Now 5 seconds to manually view folder to see that file was destroyed.
    time.sleep(5)
  
  #@public
  def getKeyDir(self, systemConfig, config_cliprocessor):
    propVal = systemConfig.get("keysDir")
    if propVal == '$Default':
      propVal = config_cliprocessor.inputVars.get('dirOfYamlKeys')
    elif '$Output' in propVal:
      propParts = propVal.split('\\')
      if len(propParts) == 2:
        if propParts[0] == '$Output':
          outputDir = config_cliprocessor.inputVars.get('dirOfOutput')
          propVal = outputDir + propParts[1] 
        else:
          print('The invalid input for keysDir is: ', propVal)
          print('ERROR: Invalid input for keysDir.')
          sys.exit(1)
      else:
        print('The invalid input for keysDir is: ', propVal)
        print('ERROR: Invalid input for keysDir.')
        sys.exit(1)
    propVal = self.formatPathForOS(propVal)
    return propVal


  def checkVarsReturnedAgainstExpected(self, cb, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponse):
    varsFragment = cb.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, tool, self, outputDict)
#from controller_cf                     .getVarsFragment(systemConfig, serviceType, instance, None, 'cloudformation', outputDict)
#from command_builder                      getVarsFragment(systemConfig, serviceType, instance, mappedVariables, tool, callingClass, outputDict={}):
    print('varsFragment is: ', varsFragment)
    fragParts = varsFragment.split(' ')
    varFilePart = 'empty'
    for part in fragParts:
      if tool == 'cloudformation':
        if part.startswith('file://'):
          varFilePart = part.replace('file://', '')
    print('varFilePart is: ', varFilePart)
    if varFilePart == 'empty':
      logString = "ERROR: varsFragment did not include a properly formed --varFile:// flag. "
      print(logString)
      sys.exit(1)
    if tool == 'cloudformation':
      acmKeysFile = varFilePart.replace('file://','').replace(' ', '')
    returnVal = False
    with open(acmKeysFile, "rb" ) as f:
      if (tool == 'cloudformation'):
        returnedData = json.load(f)
    if tool == 'cloudformation':
      varsObject = returnedData
    print('varsObject is: ', str(varsObject))
    numMatchesNeeded = len(correctExpectedResponse)
    numMatchesFound = 0
    matchedList = []
    if len(varsObject) != len(correctExpectedResponse):
      print('ERROR: vars file has the wrong number of lines.  ')
      sys.exit(1)
    for item in varsObject:
      if tool == 'cloudformation':
        for d in correctExpectedResponse:
          print('item is: ', str(item))
          # First, split the line into units that can be compared.
          leftItemParts = item['ParameterKey']
          rightItemParts = item['ParameterValue']
          leftDParts = d['ParameterKey']
          rightDParts = d['ParameterValue']
          print('xxx leftItemParts is: ', str(leftItemParts))
          print('xxx rightItemParts is: ', str(rightItemParts))
          print('xxx leftDParts is: ', str(leftDParts))
          print('xxx rightDParts is: ', str(rightDParts))
          # Next, compare the values for each matching key.
          if leftDParts == leftItemParts:
            numMatchesFound, matchedList = self.compareValuesForEachMatchingKey(numMatchesFound, matchedList, leftDParts, rightDParts, leftItemParts, rightItemParts, item)
    print("... numMatchesFound is: ", numMatchesFound)
    print("... numMatchesNeeded is: ", numMatchesNeeded)
    print("+++ matchedList is: ", matchedList)
    if numMatchesFound == numMatchesNeeded:
      returnVal = True
    return returnVal

  def compareValuesForEachMatchingKey(self, numMatchesFound, matchedList, leftDParts, rightDParts, leftItemParts, rightItemParts, item):
    rightDParts = rightDParts.replace('"','')
    rightItemParts = rightItemParts.replace('"','')
#    if (leftItemParts == "newImageName") or (leftDParts == "newImageName"):
#    if True == True:
    if (leftItemParts != "addOrgTest") and (leftItemParts != "currentDateTimeAlphaNumeric") and (leftItemParts != "makePath") and (leftItemParts != "secondVar") and (leftItemParts != "firstOutputVar") and (leftItemParts != "alternate") and (leftItemParts != "vpcCIDR") and (leftItemParts != "environ") and (leftItemParts != "networkName") and (leftItemParts != "feline") and (leftItemParts != "rabid") and (leftItemParts != "lab") and (leftItemParts != "canary") and (leftItemParts != "KeyNm") and (leftItemParts != "region") and (leftItemParts != "CidrBlock") and (leftItemParts != "AvailabilityZone") and (leftItemParts != "InstanceType") and (leftItemParts != "SSHLocation") and (leftItemParts != "KeyName") and (leftItemParts != "RouteTableId") and (leftDParts != "VpcId"):
      print(".... leftDParts is: ", leftDParts)
      print(".... leftItemParts is: ", leftItemParts)
      print(".... rightDParts is: ", rightDParts)
    #For path variables, we workaround formatting issues by simply checking to see if each is a valid path.
    if os.path.exists(rightDParts) and os.path.exists(rightItemParts):
      from pathlib import Path
      if Path(rightDParts) == Path(rightItemParts):
        numMatchesFound+=1
        matchedList.append(item)
    #For datetime variables, we are simply cheching that they are all numeric and they are the same length, because datetime stamps will vary minute by minute.
    elif (leftDParts == "now") or (leftDParts == "currentDateTimeAlphaNumeric"):
      if (len(rightDParts) == len(rightItemParts)) and (rightDParts.isdigit()) and (rightItemParts.isdigit()):
        numMatchesFound+=1
        matchedList.append(item)
    elif (leftDParts == "addDateTime") or (leftDParts == "new_image_name") or (leftDParts == "newImageName"):
      import re
      if (len(rightDParts) == len(rightItemParts)) and (len(re.sub('[^0-9]','', rightDParts)) == len(re.sub('[^0-9]','', rightItemParts))):
        numMatchesFound+=1
        matchedList.append(item)
    elif (leftDParts == "VpcId"):
      if (len(rightDParts) == len(rightItemParts)) and (rightDParts.startswith('vpc-')) and (rightItemParts.startswith('vpc-')): 
        numMatchesFound+=1
        matchedList.append(item)
    elif (leftDParts == "RouteTableId"):
      if (len(rightDParts) == len(rightItemParts)) and (rightDParts.startswith('rtb-')) and (rightItemParts.startswith('rtb-')): 
        numMatchesFound+=1
        matchedList.append(item)
    elif (leftDParts == "KeyNm"):
      if (len(rightDParts) == len(rightItemParts)): 
        numMatchesFound+=1
        matchedList.append(item)
    elif (leftDParts == "clientSecret") or (leftDParts == "client_secret"):
      if (len(rightDParts) == len(rightItemParts)): 
        numMatchesFound+=1
        matchedList.append(item)
    elif (leftDParts == "adminPwd") or (leftDParts == "ssh_pass"):
      if (len(rightDParts) == len(rightItemParts)): 
        numMatchesFound+=1
        matchedList.append(item)
    elif (leftDParts == "clientId") or (leftDParts == "client_id"):
      if (len(rightDParts) == len(rightItemParts)) and (rightItemParts.count('-')==4): 
        numMatchesFound+=1
        matchedList.append(item)
    elif (leftDParts == "tenantId") or (leftDParts == "tenant_id"):
      if (len(rightDParts) == len(rightItemParts)) and (rightItemParts.count('-')==4): 
        numMatchesFound+=1
        matchedList.append(item)
    elif (leftDParts == "subscriptionId") or (leftDParts == "subscription_id"):
      if (len(rightDParts) == len(rightItemParts)) and (rightItemParts.count('-')==4): 
        numMatchesFound+=1
        matchedList.append(item)
    elif (leftDParts == "ImageId"):
      if (len(rightDParts) == len(rightItemParts)) and (rightItemParts.startswith('ami-')): 
        numMatchesFound+=1
        matchedList.append(item)
    elif (leftDParts == "makePath"):
      userCallingDir = str(os.path.abspath("."))+'\\'
      userCallingDir = self.formatPathForOS(userCallingDir)
      dval = self.formatPathForOS(userCallingDir+rightDParts.replace('userCallingDir', ''))
      from pathlib import Path
      dPath = Path(dval)
      itemPath = Path(rightItemParts)
      if dPath == itemPath:
        numMatchesFound+=1
        matchedList.append(item)
    elif rightDParts == rightItemParts:
      numMatchesFound+=1
      matchedList.append(item)
    else:
      print('... Failed to match: ', leftDParts, ' ', leftItemParts)
      print(rightDParts, ' ', rightItemParts)
      print('os.path.exists(rightDParts) is: ', os.path.exists(rightDParts))
      print('os.path.exists(rightItemParts) is: ', os.path.exists(rightItemParts))
      sys.exit(1)
    return numMatchesFound, matchedList

  def formatPathForOS(self, input):
    if platform.system() == "Windows":
      #First strip down to one \ in each spot.
      input = input.replace('/','\\')
      input = input.replace('\\\\','\\')
      input = input.replace('\\\\\\','\\')
      #Now replace singles with doubles so you get C:\\path\\to\\a\\file with proper escale sequence.
      input = input.replace('\\','\\\\')
    elif platform.system() == "Linux":
      if '\\' in input:
        print('*** trap 1')
      if '\\\\' in input:
        print('*** trap 2')
      input = input.replace('\\','/')
      input = input.replace('//','/')
      input = input.replace('///','/')
    if input.endswith('/n'):
      input = input[:-2] + '\n'
    return input

#UNCOMMENT THE FOLLOWING FUNCTION BECAUSE IT IS CRITICAL.  WE ARE JUST COMMENTING IT DURING DEVELOPMENT OF OTHER THINGS FOR CLARITY.
  def getSystemConfig_CloudFormation(self):
    systemConfig = {
      'keysDir': '$Default', 
      'cloud': 'aws', 
      'organization': 'a1b2c', 
      'tags': {'networkName': 'name-of-vnet', 'systemName': 'name-of-system', 'environmentName': 'name-of-environment', 'ownerName': 'name-of-owner'}, 
      'foundation': {
        'instanceName': 'cf-test',
        'stackName': 'devenvironment',
        'templateName': 'aws-building-blocks/cf/foundation-unittest.json',
        'controller': 'cloudformation',
        'region': 'us-west-2',
        'canary': 'isabird',
        'labrador': 'isadog',
        'preprocessor': {'locationOn': 'aws-building-blocks/scripts/hello1.py', 'commandOn': self.getPython()+' $location', 'locationOff': 'aws-building-blocks/scripts/hello2.py', 'commandOff': self.getPython()+' $location'}, 
        'postprocessor': {'locationOn': 'aws-building-blocks/scripts/hello3.py', 'commandOn': self.getPython()+' $location', 'locationOff': 'aws-building-blocks/scripts/hello4.py', 'commandOff': self.getPython()+' $location'}, 
        'mappedVariables': {
          'vpcCIDR': '10.0.0.0/16',
          'secondString': 'bencher',
          'clientName': '$keys',
          'subName': '$keys.subscriptionName',
          'labrador': '$this.foundation',
          'tName': '$this.foundation.canary',
          'networkName': '$this.tags',
          'owner': '$this.tags.ownerName',
          'makePath': '$customFunction.addPath./azure-building-blocks/arm',
          'now': '$customFunction.currentDateTime',
          'addOrgTest': '$customFunction.addOrganization.somestring',
          'addDateTime': '$customFunction.addDateTime.somestring'
        }, 
        'images': [
          {
            'instanceName': 'cf-image-test',
            'stackName': 'cfimagetest',
            'templateName': 'aws-building-blocks/cf/image-unittest.json',
            'controller': 'cloudformation',
            'canine': 'describesadog',
            'feline': 'cat-like',
            'mappedVariables': { 
              'VpcId': '$customFunction.foundationOutput.VpcId',
              'RouteTableId': '$customFunction.foundationOutput.RouteTableId',
              'KeyName': '$keys',
              'SSHLocation': '0.0.0.0/0',
              'InstanceType': 't2.small',
              'AvailabilityZone': 'us-west-2a',
              'CidrBlock': '10.0.0.0/24',
              'newImageName': '$customFunction.addDateTime.EMPTY_IMAGE',
              'region': '$this.foundation',
              'KeyNm': '$keys.KeyName', 
              'canary': '$this.foundation',
              'lab': '$this.foundation.labrador',
              'rabid': '$this.instance.canine',
              'feline': '$this.instance',
              'networkName': '$this.tags',
              'environ': '$this.tags.environmentName',
              'vpcCIDR': '$this.foundationMapped',
              'alternate': '$this.foundationMapped.secondString',
              'firstOutputVar': '$customFunction.foundationOutput',
              'secondVar': '$customFunction.foundationOutput.secondOutputVar',
              'makePath': '$customFunction.addPath./azure-building-blocks/arm',
              'currentDateTimeAlphaNumeric': '$customFunction.currentDateTime',
              'addOrgTest': '$customFunction.addOrganization.somestring'
            }
          }
        ]
      }, 
      'serviceTypes': {
        'subnetsWithScaleSet': {
          'sharedVariables': {
            'mappedVariables': {
              'firstSharedVariable': 'justthis'
            }
          },
          'instances': [
            {
              'instanceName': 'ec2-with-custom-img',
              'stackName': 'ec2withcustomimg',
              'templateName': 'aws-building-blocks/cf/ec2withcustomimg.json',
              'controller': 'cloudformation',
              'imageName': 'cf-image-demo',
              'oneInstanceVar': 'one-value',
              'twoInstanceVar': 'two-value',
              'preprocessor': {'locationOn': 'aws-building-blocks/scripts/hello1.py', 'commandOn': self.getPython()+' $location', 'locationOff': 'aws-building-blocks/scripts/hello2.py', 'commandOff': self.getPython()+' $location'}, 
              'postprocessor': {'locationOn': 'aws-building-blocks/scripts/hello3.py', 'commandOn': self.getPython()+' $location', 'locationOff': 'aws-building-blocks/scripts/hello4.py', 'commandOff': self.getPython()+' $location'}, 
              'mappedVariables': {
                'VpcId': '$customFunction.foundationOutput.VpcId',
                'RouteTableId': '$customFunction.foundationOutput.RouteTableId',
                'KeyName': '$keys.KeyName',
                'InstanceType': 't2.small',
                'SSHLocation': '0.0.0.0/0',
                'ImageId': '$customFunction.mostRecentImage.cf-image-demo',
                'AvailabilityZone': 'us-west-2a',
                'CidrBlock': '10.0.0.0/24',
                'clientName': '$keys',
                'canary': '$this.foundation',
                'lab': '$this.foundation.labrador',
                'oneVar': '$this.instance.oneInstanceVar',
                'twoInstanceVar': '$this.instance',
                'networkName': '$this.tags',
                'environ': '$this.tags.environmentName',
                'vpcCIDR': '$this.foundationMapped',
                'alternate': '$this.foundationMapped.secondString',
                'firstOutputVar': '$customFunction.foundationOutput',
                'secondVar': '$customFunction.foundationOutput.secondOutputVar',
                'makePath': '$customFunction.addPath./azure-building-blocks/arm',
                'now': '$customFunction.currentDateTime',
                'addOrgTest': '$customFunction.addOrganization.somestring'
              }
            }
          ]
        }
      }
    }
    return systemConfig


  def destroyInfrastructureUsedInTest(self, config_cliprocessor, controller_cf):
    # Re-set the values that will be passed into the call to destroy the image and foundation.
    systemConfig = self.getSystemConfig_CloudFormation()
    keyDir = self.getKeyDir(systemConfig, config_cliprocessor)
    secretType = 'secret'
    self.setAcmVariables(config_cliprocessor, secretType)

    ccf = controller_cf()

    # Destroy the foundation stack
    instance = systemConfig.get('foundation')
    caller = 'networkFoundation'
    ccf.destroyStack(systemConfig, instance, keyDir, caller)

    #Delete the new key files that were created for these tests
    #THE FOLLOWING BLOCK DELETES THE KEY FILE, BUT YOU NEED THE KEYFILE DURING TEST DEVELOPMENT.
    self.deleteAcmKeys()


#UNCOMMENT THIS NEXT FUNCTION BECAUSE IT WORKS FINE.  JUST COMMENTING IT HERE SO WE CAN ISOLATE OTHER TESTS BELOW IT DURING DEVELOPMENT.
  def test_cf_foundation_VarsFragmentContents(self):
    self.addAcmDirToPath()
    from AgileCloudManager.app.command_builder import command_builder
    import AgileCloudManager.app.config_cliprocessor
    self.setAcmVariables(AgileCloudManager.app.config_cliprocessor)
    correctExpectedResponse = [
{'ParameterKey': 'vpcCIDR', 'ParameterValue': '10.0.0.0/16'}, 
{'ParameterKey': 'secondString', 'ParameterValue': 'bencher'}, 
{'ParameterKey': 'clientName', 'ParameterValue': 'example-clientName'}, 
{'ParameterKey': 'subName', 'ParameterValue': 'example-subscriptionName'}, 
{'ParameterKey': 'labrador', 'ParameterValue': 'isadog'}, 
{'ParameterKey': 'tName', 'ParameterValue': 'isabird'}, 
{'ParameterKey': 'networkName', 'ParameterValue': 'name-of-vnet'}, 
{'ParameterKey': 'owner', 'ParameterValue': 'name-of-owner'}, 
{'ParameterKey': 'makePath', 'ParameterValue': 'userCallingDir\\\\\\\\azure-building-blocks\\\\arm'}, 
{'ParameterKey': 'now', 'ParameterValue': '20220704111638627971'}, 
{'ParameterKey': 'addOrgTest', 'ParameterValue': 'somestringa1b2c'}, 
{'ParameterKey': 'addDateTime', 'ParameterValue': 'somestring20220704111638627971'}
    ]
    cb = command_builder()
    systemConfig = self.getSystemConfig_CloudFormation()
    serviceType = None
    instance = systemConfig.get("foundation")
    mappedVariables = systemConfig.get('foundation').get('mappedVariables')
    tool = 'cloudformation'
    outputDict = {}

    returnVal = self.checkVarsReturnedAgainstExpected(cb, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponse)

    #THE FOLLOWING BLOCK DELETES THE KEY FILE, BUT YOU NEED THE KEYFILE DURING TEST DEVELOPMENT.
    self.deleteAcmKeys()
    print('test returnVal is: ', returnVal)
    self.assertTrue(returnVal)

#UNCOMMENT THIS NEXT FUNCTION BECAUSE IT WORKS FINE.  JUST COMMENTING IT HERE SO WE CAN ISOLATE OTHER TESTS BELOW IT DURING DEVELOPMENT.
  def test_cf_image_VarsFragmentContents(self):
    self.addAcmDirToPath()
    from AgileCloudManager.app.command_builder import command_builder
    import AgileCloudManager.app.config_cliprocessor
    from AgileCloudManager.app.controller_image import controller_image
    from AgileCloudManager.app.controller_cf import controller_cf

    # First, set variables to pull the real secrets to we can create the foundation
    self.setAcmVariables(AgileCloudManager.app.config_cliprocessor, 'secret')

    # Second, set the values that will be passed into the call to  that will create the foundation.
    systemConfig = self.getSystemConfig_CloudFormation()
    keyDir = self.getKeyDir(systemConfig, AgileCloudManager.app.config_cliprocessor)
    caller = 'networkFoundation'
    serviceType = None
    instance = systemConfig.get("foundation")
    foundationInstanceName = instance.get('instanceName')

    # Third, create real foundation and real image to make sure that foundationOutput and mostRecentImage functions work properly
    cfc = controller_cf()
    cfc.createStack(systemConfig, instance, keyDir, caller, serviceType, foundationInstanceName)

    # Fifth, validate contents of the cf image vars fragment
    image = systemConfig.get('foundation').get('images')[0]
    tool = 'cloudformation'
    correctExpectedResponse_CfImage = [
{'ParameterKey': 'VpcId', 'ParameterValue': 'vpc-xxxxxxxxxxxxxxxxx'}, 
{'ParameterKey': 'RouteTableId', 'ParameterValue': 'rtb-xxxxxxxxxxxxxxxxx'},
{'ParameterKey': 'KeyName', 'ParameterValue': 'image=maker'}, 
{'ParameterKey': 'SSHLocation', 'ParameterValue': '0.0.0.0/0'}, 
{'ParameterKey': 'InstanceType', 'ParameterValue': 't2.small'}, 
{'ParameterKey': 'AvailabilityZone', 'ParameterValue': 'us-west-2a'}, 
{'ParameterKey': 'CidrBlock', 'ParameterValue': '10.0.0.0/24'}, 
{'ParameterKey': 'newImageName', 'ParameterValue': 'empty_image20220704140832135208'}, 
{'ParameterKey': 'region', 'ParameterValue': 'us-west-2'}, 
{'ParameterKey': 'KeyNm', 'ParameterValue': 'xxxxxxxxxxx'}, 
{'ParameterKey': 'canary', 'ParameterValue': 'isabird'}, 
{'ParameterKey': 'lab', 'ParameterValue': 'isadog'}, 
{'ParameterKey': 'rabid', 'ParameterValue': 'describesadog'}, 
{'ParameterKey': 'feline', 'ParameterValue': 'cat-like'}, 
{'ParameterKey': 'networkName', 'ParameterValue': 'name-of-vnet'}, 
{'ParameterKey': 'environ', 'ParameterValue': 'name-of-environment'}, 
{'ParameterKey': 'vpcCIDR', 'ParameterValue': '10.0.0.0/16'}, 
{'ParameterKey': 'alternate', 'ParameterValue': 'bencher'}, 
{'ParameterKey': 'firstOutputVar', 'ParameterValue': 'oneValue'}, 
{'ParameterKey': 'secondVar', 'ParameterValue': 'twoValue'}, 
{'ParameterKey': 'makePath', 'ParameterValue': 'userCallingDir\\\\\\\\azure-building-blocks\\\\arm'}, 
{'ParameterKey': 'currentDateTimeAlphaNumeric', 'ParameterValue': '20220704140834595445'}, 
{'ParameterKey': 'addOrgTest', 'ParameterValue': 'somestringa1b2c'}
]

    outputDict = {}
    cbld = command_builder()
    returnValImg = self.checkVarsReturnedAgainstExpected(cbld, systemConfig, None, image, image.get('mappedVariables'), tool, outputDict, correctExpectedResponse_CfImage)
    print('returnValImg is: ', returnValImg)
    # Fifth, create an empty image.  Later, remember to add more granular testing of each input variable
    ci = controller_image()
    ci.buildImages(systemConfig, keyDir)

    # Sixth, create the inputs for the service instance
    # Note: Keeping same values for setAcmVariables(..) because the keys must be sourced from same place.  
    serviceType = 'subnetsWithScaleSet'
    instance = systemConfig.get('serviceTypes').get(serviceType).get('instances')[0]
    mappedVariables = instance.get('mappedVariables')
    outputDict = {}
    cbdr = command_builder()
    instanceVarsFragment = cbdr.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, tool, self)
    print('xxx  instanceVarsFragment is: ', instanceVarsFragment)
    correctExpectedResponseInstance = [
{"ParameterKey": "firstSharedVariable", "ParameterValue": "justthis"}, 
{"ParameterKey": "VpcId", "ParameterValue": "vpc-xxxxxxxxxxxxxxxxx"}, 
{"ParameterKey": "RouteTableId", "ParameterValue": "rtb-xxxxxxxxxxxxxxxxx"}, 
{"ParameterKey": "KeyName", "ParameterValue": "image=maker"}, 
{"ParameterKey": "InstanceType", "ParameterValue": "t2.small"}, 
{"ParameterKey": "SSHLocation", "ParameterValue": "0.0.0.0/0"}, 
{"ParameterKey": "ImageId", "ParameterValue": "ami-xxxxxxxxxxxxxxxxx"}, 
{"ParameterKey": "AvailabilityZone", "ParameterValue": "us-west-2a"}, 
{"ParameterKey": "CidrBlock", "ParameterValue": "10.0.0.0/24"}, 
{"ParameterKey": "clientName", "ParameterValue": "Demo_Sandbox"}, 
{"ParameterKey": "canary", "ParameterValue": "isabird"}, 
{"ParameterKey": "lab", "ParameterValue": "isadog"}, 
{"ParameterKey": "oneVar", "ParameterValue": "one-value"}, 
{"ParameterKey": "twoInstanceVar", "ParameterValue": "two-value"}, 
{"ParameterKey": "networkName", "ParameterValue": "name-of-vnet"}, 
{"ParameterKey": "environ", "ParameterValue": "name-of-environment"}, 
{"ParameterKey": "vpcCIDR", "ParameterValue": "10.0.0.0/16"}, 
{"ParameterKey": "alternate", "ParameterValue": "bencher"}, 
{"ParameterKey": "firstOutputVar", "ParameterValue": "oneValue"}, 
{"ParameterKey": "secondVar", "ParameterValue": "twoValue"}, 
{"ParameterKey": "makePath", "ParameterValue": "userCallingDir\\\\\\\\azure-building-blocks\\\\arm"}, 
{"ParameterKey": "now", "ParameterValue": "20220705155052861754"}, 
{"ParameterKey": "addOrgTest", "ParameterValue": "somestringa1b2c"}
    ]

    instanceReturnVal = self.checkVarsReturnedAgainstExpected(cbdr, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponseInstance)
    print('instanceReturnVal is: ', instanceReturnVal)

    # Destroy the resources that were created during this test.
    self.destroyInfrastructureUsedInTest(AgileCloudManager.app.config_cliprocessor, controller_cf)

    # Only return true if both the image test and the instance test each returned True
    if (returnValImg == True) and (instanceReturnVal == True):
      returnVal = True
    else:
      returnVal = False
    print("returnValImg is: ", str(returnValImg))
    print("instanceReturnVal is: ", str(instanceReturnVal))
    print('test returnVal is: ', returnVal)
    self.assertTrue(returnVal)


if __name__ == '__main__':
    unittest.main()

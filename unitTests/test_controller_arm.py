
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
    ## First, navigating the terminal to the folder that is the PARENT of the folder that contains the agile-cloud-manager repository
    ## Second, make sure the directory structure is correct, including sibling directories for required repos, etc. 
    ## Third, running the following command in the terminal:
       #python -m unittest AgileCloudManager/unitTests/test_controller_arm.py
  
class TestControllerArm(unittest.TestCase):

  def addAcmDirToPath(self):
#    acmDir = str(pathlib.Path(__file__).parent.resolve().parent.resolve())+'/agile-cloud-manager'
    acmDir = str(pathlib.Path(__file__).parent.resolve().parent.resolve())+'/app'
    acmDir = self.formatPathForOS(acmDir)
    sys.path.insert(0, acmDir)

  def setAcmVariables(self, config_cliprocessor, inputType='sanitized'):
    # inputsDir is where the key files originate.  These will be sourced before you use ACM
    if inputType == 'sanitized':
      inputsDir = str(pathlib.Path(__file__).parent.resolve())+'/input-files'
    elif inputType == 'secret':
      if platform.system() == 'Windows':
        inputsDir = os.path.expanduser('~') + '/acm/keys/starter/'
      elif platform.system() == 'Linux':
        inputsDir = os.path.expanduser('~') + '/acmconfig/'
    print('platform.system() is: ', platform.system())
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
    config_cliprocessor.inputVars['dirOfYamlKeys'] = inputsDir
    if inputType == 'sanitized':
      config_cliprocessor.inputVars['dirOfOutput'] = inputsDir
    elif inputType == 'secret':
      config_cliprocessor.inputVars['dirOfOutput'] = self.formatPathForOS(str(pathlib.Path(inputsDir).parent.resolve())+'/')
    config_cliprocessor.inputVars["tfvarsFileAndPath"] = varsFileAndPath
    config_cliprocessor.inputVars["userCallingDir"] = userCallingDir
    config_cliprocessor.inputVars["verboseLogFilePath"] = verboseLogFilePath

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

  def checkVarsReturnedAgainstExpected(self, cb, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponse):
    print('instance is: ', instance)
    varsFragment = cb.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, tool, self, outputDict)
    print("varsFragment is: ", varsFragment)
    fragParts = varsFragment.split(' ')
    varFilePart = 'empty'
    for part in fragParts:
      if tool == 'customController':
        if part.startswith('--varsfile://'):
          varFilePart = part
      if tool == 'arm':
        if '--parameters' not in part:
          varFilePart = part
    print('varFilePart is: ', varFilePart)
#    quit('hhhhhhhhhhh@!')
    if varFilePart == 'empty':
      logString = "ERROR: varsFragment did not include a properly formed --varFile:// flag. "
      quit(logString)
    if tool == 'customController':
      acmKeysFile = varFilePart.replace('--varsfile://','').replace(' ', '')
    elif tool == 'arm':
      acmKeysFile = varFilePart.replace('--parameters','').replace(' ', '')
    returnVal = False
    f = open(acmKeysFile, "rb" )
    returnedJSON = json.load(f)
    f.close()
    if tool == 'customController':
      jsonObject = returnedJSON
    elif tool == 'arm':
      jsonObject = returnedJSON['parameters']
      correctExpectedResponse = correctExpectedResponse[0]['parameters']
    numMatchesNeeded = len(correctExpectedResponse)
    numMatchesFound = 0
    matchedList = []
    print("jsonObject is: ", jsonObject)
    print("correctExpectedResponse is: ", correctExpectedResponse)
    if len(jsonObject) != len(correctExpectedResponse):
      self.assertTrue(returnVal)
    for item in jsonObject:
      if tool == 'customController':
        if len(dict(item)) != 1:
          self.assertTrue(returnVal)
        for key in dict(item).keys():
          for d in correctExpectedResponse:
            if key in d.keys():
                if key == 'now':
                  if d[key] != dict(item)[key]:
                    if len(d[key]) == len(dict(item)[key]):
                      numMatchesFound +=1
                if d[key] == dict(item)[key]:
                  numMatchesFound +=1
      elif tool == 'arm':
          for d in correctExpectedResponse:
#            dkey = 'null'
#            dval = 'null'
            dkey = d
            dval = correctExpectedResponse[d]['value']
##            if len(dict(d))==1:
##              for k in dict(d).keys():
#            if len(d)==1:
#              for k in d.keys():
#                dkey = k
##                dval = dict(d)[k]
#                dval = d[k]
            if item == dkey:
              if item == 'now':
                if len(dval) == len(jsonObject[item]['value']):
                  numMatchesFound +=1
                  matchedList.append(item)
              elif item == 'makePath':
                userCallingDir = str(os.path.abspath("."))+'\\'
                userCallingDir = self.formatPathForOS(userCallingDir)
                dval = self.formatPathForOS(userCallingDir+dval.replace('userCallingDir', ''))
                from pathlib import Path
                dPath = Path(dval)
                itemPath = Path(jsonObject[item]['value'])
                if dPath == itemPath:
                  numMatchesFound+=1
                  matchedList.append(item)
              else:
                if dval == jsonObject[item]['value']:
                  numMatchesFound+=1
                  matchedList.append(item)

    print("numMatchesFound is: ", numMatchesFound)
    print("numMatchesNeeded is: ", numMatchesNeeded)
    print('matchedList is: ', str(matchedList))
#    quit('fffqqqrrr')

    if numMatchesFound == numMatchesNeeded:
      returnVal = True
    return returnVal

  def formatPathForOS(self, input):
    if platform.system() == "Windows":
      input = input.replace('/','\\')
      input = input.replace('\\\\','\\')
      input = input.replace('\\\\\\','\\')
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
  def getSystemConfigFoundation_ARM(self):
    systemConfig = {
      'keysDir': '$Default', 
      'cloud': 'azure', 
      'organization': 'a1b2c', 
      'tags': {'networkName': 'name-of-vnet', 'systemName': 'name-of-system', 'environmentName': 'name-of-environment', 'ownerName': 'name-of-owner'}, 
      'foundation': {
        'instanceName': 'arm-test', 
        'deploymentName': 'foundation-test',
        'templateName': 'azure-building-blocks/arm/empty.foundation.json',
        'emptyTemplateName': 'azure-building-blocks/arm/empty.template.json',
        'controller': 'arm',
        'resourceGroupName': 'myEmptyTestRG',
        'resourceGroupRegion': 'eastus',
        'canary': 'isabird',
        'labrador': 'isadog',
        'preprocessor': {'locationOn': 'aws-building-blocks/scripts/hello1.py', 'commandOn': self.getPython()+' $location', 'locationOff': 'aws-building-blocks/scripts/hello2.py', 'commandOff': self.getPython()+' $location'}, 
        'postprocessor': {'locationOn': 'aws-building-blocks/scripts/hello3.py', 'commandOn': self.getPython()+' $location', 'locationOff': 'aws-building-blocks/scripts/hello4.py', 'commandOff': self.getPython()+' $location'}, 
        'mappedVariables': {
          'resourceGroupName': '$this.foundation',
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
          'addOrgTest': '$customFunction.addOrganization.somestring'
        }, 
        'images': [
          {
            'instanceName': 'arm-image',
            'deploymentName': 'imagetest',
            'templateName': 'azure-building-blocks/arm/empty.image.json',
            'emptyTemplateName': 'azure-building-blocks/arm/empty.template.json',
            'controller': 'arm', 
            'resourceGroupName': 'myEmptyTestRG',
            'resourceGroupRegion': 'eastus',
            'imageName': 'testimage',
            'runOutputName': 'testoutput',
            'canine': 'describesadog',
            'feline': 'cat-like',
            'mappedVariables': {
              'KeyName': '$keys.KeyName', 
              'InstanceType': 't2.small', 
              'clientName': '$keys',
              'subscriptionId': '$keys',
              'canary': '$this.foundation',
              'lab': '$this.foundation.labrador',
              'resourceGroupName': '$this.foundation',
              'resourceGroupRegion': '$this.foundation',
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
              'imgBuilderId': '$customFunction.imageBuilderId',
              'imageTemplateName': '$customFunction.imageTemplateName',
              'imageName': '$this.instance',
              'runOutputName': '$this.instance',
              'addOrgTest': '$customFunction.addOrganization.somestring'
            }
          }
        ]
      }, 
      'serviceTypes': {
        'subnetsWithScaleSet': {
          'sharedVariables': {
            'mappedVariables': {
              'firstSharedVariable': 'justthis',
              'KeyName': '$keys.KeyName', 
              'clientName': '$keys',
              'canary': '$this.foundation',
              'lab': '$this.foundation.labrador',
              'networkName': '$this.tags',
              'environ': '$this.tags.environmentName',
              'vpcCIDR': '$this.foundationMapped',
              'alternate': '$this.foundationMapped.secondString',
              'firstOutputVar': '$customFunction.foundationOutput',
              'secondVar': '$customFunction.foundationOutput.secondOutputVar',
              'makePath': '$customFunction.addPath./azure-building-blocks/arm',
              'now': '$customFunction.currentDateTime',
              'imageId': '$customFunction.mostRecentImage.arm-image',
              'addOrgTest': '$customFunction.addOrganization.somestring'
            }
          },
          'instances': [
            {
              'instanceName': 'arm-service',
              'deploymentName': 'servicetest',
              'templateName': 'azure-building-blocks/arm/empty.instance.json',
              'emptyTemplateName': 'azure-building-blocks/arm/empty.template.json',
              'controller': 'arm',
              'resourceGroupName': 'myEmptyInstanceRG',
              'resourceGroupRegion': 'eastus',
              'imageName': 'arm-image', 
              'oneInstanceVar': 'one-value',
              'twoInstanceVar': 'two-value',
              'preprocessor': {'locationOn': 'aws-building-blocks/scripts/hello1.py', 'commandOn': self.getPython()+' $location', 'locationOff': 'aws-building-blocks/scripts/hello2.py', 'commandOff': self.getPython()+' $location'}, 
              'postprocessor': {'locationOn': 'aws-building-blocks/scripts/hello3.py', 'commandOn': self.getPython()+' $location', 'locationOff': 'aws-building-blocks/scripts/hello4.py', 'commandOff': self.getPython()+' $location'}, 
              'mappedVariables': {
                'KeyName': '$keys.KeyName', 
                'InstanceType': 't2.small', 
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
                'imageId': '$customFunction.mostRecentImage.testimage',
                'now': '$customFunction.currentDateTime',
                'addOrgTest': '$customFunction.addOrganization.somestring'
              }
            }
          ]
        }
      }
    }
    return systemConfig



#UNCOMMENT THIS 
#UNCOMMENT THIS NEXT FUNCTION BECAUSE IT WORKS FINE.  JUST COMMENTING IT HERE SO WE CAN ISOLATE OTHER TESTS BELOW IT DURING DEVELOPMENT.


#checked july 15
#UNCOMMENT THIS NEXT FUNCTION BECAUSE IT WORKS FINE.  JUST COMMENTING IT HERE SO WE CAN ISOLATE OTHER TESTS BELOW IT DURING DEVELOPMENT.
  def test_ARM_foundation_VarsFragmentContents(self):
    self.addAcmDirToPath()
    from AgileCloudManager.app.command_builder import command_builder
    import AgileCloudManager.app.config_cliprocessor
    self.setAcmVariables(AgileCloudManager.app.config_cliprocessor)
    correctExpectedResponse = [
    {
      "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#", 
      "contentVersion": "1.0.0.0", 
      "parameters": {
          "resourceGroupName": {"value": "myEmptyTestRG"}, 
          "vpcCIDR": {"value": "10.0.0.0/16"}, 
          "secondString": {"value": "bencher"}, 
          "clientName": {"value": "example-clientName"}, 
          "subName": {"value": "example-subscriptionName"}, 
          "labrador": {"value": "isadog"}, 
          "tName": {"value": "isabird"}, 
          "networkName": {"value": "name-of-vnet"}, 
          "owner": {"value": "name-of-owner"}, 
          "makePath": {"value": "userCallingDir\\azure-building-blocks\\arm"}, 
          "now": {"value": "20220621123906081117"}, 
          "addOrgTest": {"value": "somestringa1b2c"}
      }
    }
    ]
    cb = command_builder()
    systemConfig = self.getSystemConfigFoundation_ARM()
    serviceType = None
    instance = systemConfig.get("foundation")
    mappedVariables = systemConfig.get('foundation').get('mappedVariables')
    tool = 'arm'
    outputDict = {}
    returnVal = self.checkVarsReturnedAgainstExpected(cb, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponse)
    print('returnVal is: ', returnVal)
    #THE FOLLOWING BLOCK DELETES THE KEY FILE, BUT YOU NEED THE KEYFILE DURING TEST DEVELOPMENT.
    self.deleteAcmKeys()
    self.assertTrue(returnVal)

#UNCOMMENT THIS NEXT FUNCTION BECAUSE IT WORKS FINE.  JUST COMMENTING IT HERE SO WE CAN ISOLATE OTHER TESTS BELOW IT DURING DEVELOPMENT.
  def test_ARM_image_VarsFragmentContents(self):
    self.addAcmDirToPath()
    from AgileCloudManager.app.command_builder import command_builder
    import AgileCloudManager.app.config_cliprocessor
    from AgileCloudManager.app.controller_arm import controller_arm

    # First, set variables to pull the real secrets to we can create the empty foundation
    self.setAcmVariables(AgileCloudManager.app.config_cliprocessor, 'secret')
    systemConfig = self.getSystemConfigFoundation_ARM()

    # Next, create real foundation and real image to make sure that foundationOutput and mostRecentImage functions work properly
    ca = controller_arm()
    ca.createDeployment(systemConfig, systemConfig.get("foundation"), 'networkFoundation', 'networkFoundation', False)
 
    # Now, run the service instance test while the real foundation and real image still exist.  
    print('ca.foundationOutput is: ', ca.foundationOutput)    
    correctExpectedResponse = [
{
  "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#", 
  "contentVersion": "1.0.0.0", 
  "parameters": {
    "firstSharedVariable": {"value": "justthis"}, 
    "KeyName": {"value": "image=maker"}, 
    "clientName": {"value": "Demo_Sandbox"}, 
    "canary": {"value": "isabird"}, 
    "lab": {"value": "isadog"}, 
    "networkName": {"value": "name-of-vnet"}, 
    "environ": {"value": "name-of-environment"}, 
    "vpcCIDR": {"value": "10.0.0.0/16"}, 
    "alternate": {"value": "bencher"}, 
    "firstOutputVar": {"value": "one-value"}, 
    "secondVar": {"value": "two-value"}, 
    "makePath": {"value": "userCallingDir\\azure-building-blocks\\arm"}, 
    "now": {"value": "20220623103255682461"}, 
    "imageId": {"value": "testimage"}, 
    "addOrgTest": {"value": "somestringa1b2c"}, 
    "InstanceType": {"value": "t2.small"}, 
    "oneVar": {"value": "one-value"}, 
    "twoInstanceVar": {"value": "two-value"}
  }
}
    ]
    cb = command_builder()
    systemConfig = self.getSystemConfigFoundation_ARM()
    serviceType = 'subnetsWithScaleSet'
    instance = systemConfig.get('serviceTypes').get('subnetsWithScaleSet').get('instances')[0]
    mappedVariables = systemConfig.get('serviceTypes').get('subnetsWithScaleSet').get('instances')[0].get('mappedVariables')
    tool = 'arm'
    outputDict = {}
    outputDict['typeParent'] = 'systems'
    foundationResourceGroupName = systemConfig.get("foundation").get("resourceGroupName")
    foundationDeploymentName = systemConfig.get("foundation").get("deploymentName")
    outputDict['resourceGroupName'] = foundationResourceGroupName
    outputDict['deploymentName'] = foundationDeploymentName
    returnVal = self.checkVarsReturnedAgainstExpected(cb, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponse)
    print('returnVal is: ', returnVal)
    ca.destroyDeployment(systemConfig, systemConfig.get("foundation"), 'networkFoundation')
    #THE FOLLOWING BLOCK DELETES THE KEY FILE, BUT YOU NEED THE KEYFILE DURING TEST DEVELOPMENT.
    self.deleteAcmKeys()
    self.assertTrue(returnVal)

if __name__ == '__main__':
    unittest.main()

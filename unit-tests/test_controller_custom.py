
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
       #python -m unittest agile-cloud-manager/unit-tests/test_controller_custom.py

class TestControllerCustom(unittest.TestCase):

  def addAcmDirToPath(self):
    acmDir = str(pathlib.Path(__file__).parent.resolve().parent.resolve())+'/app'
    acmDir = self.formatPathForOS(acmDir)
    sys.path.insert(0, acmDir)

  def setAcmVariables(self, config_cliprocessor, inputType='sanitized'):
    # inputsDir is where the key files originate.  These will be sourced before you use ACM
    if inputType == 'sanitized':
      inputsDir = str(pathlib.Path(__file__).parent.resolve())+'/input-files'
    elif inputType == 'secret':
      inputsDir = os.path.expanduser('~') + '/acm/keys/starter/'
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
    print('varFilePart is: ', varFilePart)
#    quit('hhhhhhhhhhh@!')
    if varFilePart == 'empty':
      logString = "ERROR: varsFragment did not include a properly formed --varFile:// flag. "
      quit(logString)
    if tool == 'customController':
      acmKeysFile = varFilePart.replace('--varsfile://','').replace(' ', '')
    returnVal = False
    f = open(acmKeysFile, "rb" )
    returnedJSON = json.load(f)
    f.close()
    if tool == 'customController':
      jsonObject = returnedJSON
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
                      matchedList.append(item)
                elif key == 'makePath':
                  userCallingDir = str(os.path.abspath("."))+'\\'
                  userCallingDir = self.formatPathForOS(userCallingDir)
                  dval = self.formatPathForOS(userCallingDir+d[key].replace('userCallingDir', ''))
                  from pathlib import Path
                  dPath = Path(dval)
                  itemPath = Path(dict(item)[key])
                  if dPath == itemPath:
                    numMatchesFound+=1
                    matchedList.append(item)
                elif d[key] == dict(item)[key]:
                  numMatchesFound +=1
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


  def getSystemConfigFoundation_Custom(self):
    systemConfig = {
      'keysDir': '$Default', 
      'cloud': 'aws', 
      'organization': 'a1b2c', 
      'tags': {'networkName': 'name-of-vnet', 'systemName': 'name-of-system', 'environmentName': 'name-of-environment', 'ownerName': 'name-of-owner'}, 
      'foundation': {
        'instanceName': 'custom', 
        'templateName': 'aws-building-blocks/customTemplates/sample.template.json', 
        'controller': '$customController.aws-building-blocks/controllers/customController.py', 
        'controllerCommand': 'python $location', 
        'canary': 'isabird',
        'labrador': 'isadog',
        'preprocessor': {'locationOn': 'aws-building-blocks/scripts/hello1.py', 'commandOn': 'python $location', 'locationOff': 'aws-building-blocks/scripts/hello2.py', 'commandOff': 'python $location'}, 
        'postprocessor': {'locationOn': 'aws-building-blocks/scripts/hello3.py', 'commandOn': 'python $location', 'locationOff': 'aws-building-blocks/scripts/hello4.py', 'commandOff': 'python $location'}, 
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
          'addOrgTest': '$customFunction.addOrganization.somestring'
        }, 
        'images': [
          {
            'instanceName': 'custom-image', 
            'templateName': 'aws-building-blocks/customTemplates/sample.template.json', 
            'controller': '$customController.aws-building-blocks/controllers/customController.py', 
            'controllerCommand': 'python $location', 
            'canine': 'describesadog',
            'feline': 'cat-like',
            'mappedVariables': {
              'KeyName': '$keys.KeyName', 
              'InstanceType': 't2.small', 
              'clientName': '$keys',
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
              'now': '$customFunction.currentDateTime',
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
#              'imageId': '$customFunction.mostRecentImage.image-demo',
              'addOrgTest': '$customFunction.addOrganization.somestring'
            }
          },
          'instances': [
            {
              'instanceName': 'custom-scaleset', 
              'templateName': 'aws-building-blocks/customTemplates/sample.template.json', 
              'controller': '$customController.aws-building-blocks/controllers/customController.py', 
              'controllerCommand': 'python $location', 
              'imageName': 'image-demo', 
              'oneInstanceVar': 'one-value',
              'twoInstanceVar': 'two-value',
              'preprocessor': {'locationOn': 'aws-building-blocks/scripts/hello1.py', 'commandOn': 'python $location', 'locationOff': 'aws-building-blocks/scripts/hello2.py', 'commandOff': 'python $location'}, 
              'postprocessor': {'locationOn': 'aws-building-blocks/scripts/hello3.py', 'commandOn': 'python $location', 'locationOff': 'aws-building-blocks/scripts/hello4.py', 'commandOff': 'python $location'}, 
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
#                'imageId': '$customFunction.mostRecentImage.image-demo',
                'now': '$customFunction.currentDateTime',
                'addOrgTest': '$customFunction.addOrganization.somestring'
              }
            }
          ]
        }
      }
    }
    return systemConfig


  def test_foundation_VarsFragmentStructure(self):
    self.addAcmDirToPath()
    from command_builder import command_builder
    import config_cliprocessor
    self.setAcmVariables(config_cliprocessor)
    structureIsCorrect = False
    systemConfig = self.getSystemConfigFoundation_Custom()
    serviceType = None
    instance = systemConfig.get("foundation")
    mappedVariables = systemConfig.get('foundation').get('mappedVariables')
    tool = 'customController'
    outputDict = {}
    cb = command_builder()
    varsFragment = cb.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, tool, outputDict)
    print("varsFragment is: ", varsFragment)
    if ('--varsfile://' in varsFragment) and ('--templateFile://' in varsFragment):
      structureIsCorrect = True
    print("structureIsCorrect is: ", structureIsCorrect)
    self.deleteAcmKeys()
    self.assertTrue(structureIsCorrect)


  def test_customcontroller_foundation_VarsFragmentContents(self):
    self.addAcmDirToPath()
    from command_builder import command_builder
    import config_cliprocessor
    self.setAcmVariables(config_cliprocessor)
    correctExpectedResponse = [
      {"vpcCIDR": "10.0.0.0/16"}, 
      {"secondString": "bencher"}, 
      {"clientName": "example-clientName"}, 
      {"subName": "example-subscriptionName"}, 
      {"labrador": "isadog"}, 
      {"tName": "isabird"}, 
      {"networkName": "name-of-vnet"}, 
      {"owner": "name-of-owner"}, 
      {"makePath": "userCallingDir\\azure-building-blocks\\arm"}, 
      {"now": "20220616153103296962"}, 
      {"addOrgTest": "somestringa1b2c"}
    ]
    cb = command_builder()
    systemConfig = self.getSystemConfigFoundation_Custom()
    serviceType = None
    instance = systemConfig.get("foundation")
    mappedVariables = systemConfig.get('foundation').get('mappedVariables')
    tool = 'customController'
    outputDict = {}
    returnVal = self.checkVarsReturnedAgainstExpected(cb, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponse)
    print('returnVal is: ', returnVal)
    #THE FOLLOWING BLOCK DELETES THE KEY FILE, BUT YOU NEED THE KEYFILE DURING TEST DEVELOPMENT.
    self.deleteAcmKeys()
    self.assertTrue(returnVal)


  def test_customcontroller_image_VarsFragmentContents(self):
    self.addAcmDirToPath()
    from command_builder import command_builder
    import config_cliprocessor
    self.setAcmVariables(config_cliprocessor)
    correctExpectedResponse = [
      {"KeyName": "example-KeyName"}, 
      {"InstanceType": "t2.small"}, 
      {"clientName": "example-clientName"}, 
      {"canary": "isabird"}, 
      {"lab": "isadog"}, 
      {"rabid": "describesadog"}, 
      {"feline": "cat-like"}, 
      {"networkName": "name-of-vnet"}, 
      {"environ": "name-of-environment"}, 
      {"vpcCIDR": "10.0.0.0/16"}, 
      {"alternate": "bencher"}, 
      {"firstOutputVar": "value-for-first-output-variable"}, 
      {"secondVar": "value-for-second-output-variable"}, 
      {"makePath": "userCallingDir\\azure-building-blocks\\arm"}, 
      {"now": "20220617181604103059"}, 
      {"addOrgTest": "somestringa1b2c"}
    ]
    cb = command_builder()
    systemConfig = self.getSystemConfigFoundation_Custom()
    serviceType = None
    if 'images' in systemConfig.get('foundation').keys():
      image = systemConfig.get('foundation').get('images')[0]
    else:
      print('No images were found in your foundation.')
      self.assertTrue(False)
    tool = 'customController'
    outputDict = {}
    returnVal = self.checkVarsReturnedAgainstExpected(cb, systemConfig, serviceType, image, image.get('mappedVariables'), tool, outputDict, correctExpectedResponse)
    print('returnVal is: ', returnVal)
    #THE FOLLOWING BLOCK DELETES THE KEY FILE, BUT YOU NEED THE KEYFILE DURING TEST DEVELOPMENT.
    self.deleteAcmKeys()
    self.assertTrue(returnVal)


  def test_customcontroller_serviceinstance_VarsFragment_Contents(self):
    self.addAcmDirToPath()
    from command_builder import command_builder
    import config_cliprocessor
    self.setAcmVariables(config_cliprocessor)
    correctExpectedResponse = [
      {"firstSharedVariable": "justthis"}, 
      {"KeyName": "example-KeyName"}, 
      {"clientName": "example-clientName"}, 
      {"canary": "isabird"}, 
      {"lab": "isadog"}, 
      {"networkName": "name-of-vnet"}, 
      {"environ": "name-of-environment"}, 
      {"vpcCIDR": "10.0.0.0/16"}, 
      {"alternate": "bencher"}, 
      {"firstOutputVar": "value-for-first-output-variable"}, 
      {"secondVar": "value-for-second-output-variable"}, 
      {"makePath": "userCallingDir\\azure-building-blocks\\arm"}, 
      {"now": "20220620095531060121"}, 
      {"addOrgTest": "somestringa1b2c"}, 
      {"InstanceType": "t2.small"}, 
      {"oneVar": "one-value"}, 
      {"twoInstanceVar": "two-value"}
    ]
    cb = command_builder()
    systemConfig = self.getSystemConfigFoundation_Custom()
    serviceType = "subnetsWithScaleSet"
    if 'serviceTypes' in systemConfig.keys():
      for thisType in systemConfig.get('serviceTypes'):
        if thisType == serviceType:
          for thisInstance in systemConfig.get('serviceTypes').get(serviceType).get('instances'):
            if thisInstance.get('instanceName') == 'custom-scaleset':
              instance = thisInstance
        print('thisType is: ', thisType)
    if instance == None:
      print('No instance was found with proper instanceName in ', serviceType, ' serviceType. ')
      self.assertTrue(False)
    tool = 'customController'
    outputDict = {}
    returnVal = self.checkVarsReturnedAgainstExpected(cb, systemConfig, serviceType, instance, instance.get('mappedVariables'), tool, outputDict, correctExpectedResponse)
    print('returnVal is: ', returnVal)
    #THE FOLLOWING BLOCK DELETES THE KEY FILE, BUT YOU NEED THE KEYFILE DURING TEST DEVELOPMENT.
    self.deleteAcmKeys()
    self.assertTrue(returnVal)

if __name__ == '__main__':
    unittest.main()

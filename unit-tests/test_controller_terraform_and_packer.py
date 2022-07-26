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
       #python -m unittest agile-cloud-manager/unit-tests/test_controller_terraform_and_packer.py
  
class TestControllerPacker(unittest.TestCase):
  
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
      inputsDir = os.path.expanduser('~') + '/acm/keys/starter/'
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
          quit('ERROR: Invalid input for keysDir.')
      else:
        print('The invalid input for keysDir is: ', propVal)
        quit('ERROR: Invalid input for keysDir.')
    propVal = self.formatPathForOS(propVal)
    return propVal


  def checkVarsReturnedAgainstExpected(self, cb, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponse):
    varsFragment = cb.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, tool, self, outputDict)
    print('varsFragment is: ', varsFragment)
    fragParts = varsFragment.split(' ')
    varFilePart = 'empty'
    for part in fragParts:
#      if tool == 'customController':
#        if part.startswith('--varsfile://'):
#          varFilePart = part
      if tool == 'arm':
        if '--parameters' not in part:
          varFilePart = part
      if tool == "terraform":
        if part.startswith('-var-file='):
          varFilePart = part
      if tool == 'packer':
#        print('len(fragParts) is: ', len(fragParts))
#        print('fragParts is: ', str(fragParts))
#        print('packer part is: ', part)
        if part.startswith('-var-file='):
          varFilePart = part
    print('varFilePart is: ', varFilePart)
    #quit('[---c---]')
    if varFilePart == 'empty':
      logString = "ERROR: varsFragment did not include a properly formed --varFile:// flag. "
      quit(logString)
#    if tool == 'customController':
#      acmKeysFile = varFilePart.replace('--varsfile://','').replace(' ', '')
    if tool == 'arm':
      acmKeysFile = varFilePart.replace('--parameters','').replace(' ', '')
    elif tool == 'terraform':
      acmKeysFile = varFilePart.replace('-var-file=','').replace(' ', '').replace('"','')
    elif tool == 'packer':
      acmKeysFile = varFilePart.replace('-var-file=','').replace(' ', '').replace('"','')
    returnVal = False
    with open(acmKeysFile, "rb" ) as f:
#      if (tool == 'customController') or (tool == 'arm'):
#        returnedData = json.load(f)
      if tool == 'terraform':
        returnedData = f.read().decode().splitlines()
      elif tool == 'packer':
        returnedData = json.load(f)
#    if tool == 'customController':
#      varsObject = returnedData
    if tool == 'arm':
      varsObject = returnedData['parameters']
      correctExpectedResponse = correctExpectedResponse[0]['parameters']
    elif tool == 'terraform':
      varsObject = returnedData
    elif tool == 'packer':
      varsObject = returnedData
    print('varsObject is: ', str(varsObject))
    numMatchesNeeded = len(correctExpectedResponse)
    numMatchesFound = 0
    matchedList = []
    if len(varsObject) != len(correctExpectedResponse):
      quit('ERROR: vars file has the wrong number of lines.  ')
    for item in varsObject:
#      if tool == 'customController':
#        if len(dict(item)) != 1:
#          quit('ERROR: len(dict(item)) != 1')
#        for key in dict(item).keys():
#          for d in correctExpectedResponse:
#            if key in d.keys():
#                if key == 'now':
#                  if d[key] != dict(item)[key]:
#                    if len(d[key]) == len(dict(item)[key]):
#                      numMatchesFound +=1
#                if d[key] == dict(item)[key]:
#                  numMatchesFound +=1
      if tool == 'arm':
          for d in correctExpectedResponse:
            if item == d:
              if item == 'now':
                if len(correctExpectedResponse[d]['value']) == len(varsObject[item]['value']):
                  numMatchesFound +=1
              if (item == 'makePath') or (leftDParts == "cloudInit") or (leftDParts == "init_script"):
                userCallingDir = str(os.path.abspath("."))+'\\'
                userCallingDir = self.formatPathForOS(userCallingDir)
                dval = self.formatPathForOS(userCallingDir+dval.replace('userCallingDir', ''))
                from pathlib import Path
                dPath = Path(dval)
                itemPath = Path(varsObject[item]['value'])
                if dPath == itemPath:
                  numMatchesFound+=1
                  matchedList.append(item)
              if correctExpectedResponse[d]['value'] == varsObject[item]['value']:
                numMatchesFound+=1
      elif tool == 'terraform':
          for d in correctExpectedResponse:
            # First, split the line into units that can be compared.
            itemParts = item.split("=")
            dParts = d.split("=")
            if len(itemParts)==2:
              leftItemParts = itemParts[0].replace(' ','')
              rightItemParts = itemParts[1].replace(' ','')
            elif (len(itemParts)==3):
              leftItemParts = itemParts[0].replace(' ','')
              rightItemParts = itemParts[1].replace(' ','')+'='+itemParts[2].replace(' ','')
            else:
              logString = "ERROR: Wrong number of = signs in one of the variable lines. Only one or two = sign per line allowed. "
              quit(logString)
            if (len(dParts)==2):
              leftDParts = dParts[0].replace(' ','')
              rightDParts = dParts[1].replace(' ','')
            elif (len(dParts)==3):
              leftDParts = dParts[0].replace(' ','')
              rightDParts = dParts[1].replace(' ','')+'='+dParts[2].replace(' ','')
            else:
              logString = "ERROR: Wrong number of = signs in one of the variable lines. Only one or two = sign per line allowed. "
              quit(logString)
            # Next, compare the values for each matching key.
            if leftDParts == leftItemParts:
              rightDParts = rightDParts.replace('"','')
              rightItemParts = rightItemParts.replace('"','')
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
              elif (leftDParts == "makePath") or (leftDParts == "cloudInit") or (leftDParts == "init_script"):
                userCallingDir = str(os.path.abspath("."))+'\\'
                userCallingDir = self.formatPathForOS(userCallingDir)
                dval = self.formatPathForOS(userCallingDir+rightDParts.replace('userCallingDir', ''))
                from pathlib import Path
                dPath = Path(dval)
                itemPath = Path(rightItemParts)
                if dPath == itemPath:
                  numMatchesFound+=1
                  matchedList.append(item)
              elif leftDParts == "clientSecret":
                if (len(rightDParts) == len(rightItemParts)): 
                  numMatchesFound+=1
                  matchedList.append(item)
              elif leftDParts == "adminPwd":
                if (len(rightDParts) == len(rightItemParts)): 
                  numMatchesFound+=1
                  matchedList.append(item)
              elif leftDParts == "clientId":
                if (len(rightDParts) == len(rightItemParts)) and (rightItemParts.count('-')==4): 
                  numMatchesFound+=1
                  matchedList.append(item)
              elif leftDParts == "tenantId":
                if (len(rightDParts) == len(rightItemParts)) and (rightItemParts.count('-')==4): 
                  numMatchesFound+=1
                  matchedList.append(item)
              elif leftDParts == "subscriptionId":
                if (len(rightDParts) == len(rightItemParts)) and (rightItemParts.count('-')==4): 
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
                quit('---eee---')
      elif tool == 'packer':
        print('type(item) is: ', type(item))
        print('str(item) is: ', str(item))
        leftItemParts = item
        rightItemParts = varsObject.get(item)
        print('leftItemParts is: ', str(leftItemParts))
        print('rightItemParts is: ', str(rightItemParts))
        for d in correctExpectedResponse:
            print('d is: ', str(d))
            rightDParts = correctExpectedResponse.get(d)
            leftDParts = d
            if item == d:
              #For path variables, we workaround formatting issues by simply checking to see if each is a valid path.
              if os.path.exists(rightDParts) and os.path.exists(rightItemParts):
                from pathlib import Path
                if Path(rightDParts) == Path(rightItemParts):
                  numMatchesFound+=1
                else:
                  print('NO MATCH! str(Path(rightDParts)) is: ', str(Path(rightDParts)))
                  print('NO MATCH! str(Path(rightItemParts)) is: ', str(Path(rightItemParts)))
                  quit('ggg---hhh---iii')
              #For datetime variables, we are simply cheching that they are all numeric and they are the same length, because datetime stamps will vary minute by minute.
              elif (leftDParts == "now") or (leftDParts == "currentDateTimeAlphaNumeric"):
                if (len(rightDParts) == len(rightItemParts)) and (rightDParts.isdigit()) and (rightItemParts.isdigit()):
                  numMatchesFound+=1
              elif (leftDParts == "makePath") or (leftDParts == "cloudInit") or (leftDParts == "init_script"):
                userCallingDir = str(os.path.abspath("."))+'\\'
                userCallingDir = self.formatPathForOS(userCallingDir)
                dval = self.formatPathForOS(userCallingDir+rightDParts.replace('userCallingDir', ''))
                from pathlib import Path
                dPath = Path(dval)
                itemPath = Path(rightItemParts)
                if dPath == itemPath:
                  numMatchesFound+=1
                  matchedList.append(item)
              elif leftDParts == "az_server":
                if rightDParts.startswith("https://dev.azure.com/") and rightItemParts.startswith("https://dev.azure.com/"):
                  numMatchesFound+=1
              elif leftDParts == "ssh_pass":
                if (len(rightDParts) == len(rightItemParts)): 
                  numMatchesFound+=1
              elif leftDParts == "az_pat":
                if (len(rightDParts) == len(rightItemParts)): 
                  numMatchesFound+=1
              elif leftDParts == "client_secret":
                if (len(rightDParts) == len(rightItemParts)): 
                  numMatchesFound+=1
              elif leftDParts == "client_id":
                if (len(rightDParts) == len(rightItemParts)) and (rightItemParts.count('-')==4): 
                  numMatchesFound+=1
              elif leftDParts == "tenant_id":
                if (len(rightDParts) == len(rightItemParts)) and (rightItemParts.count('-')==4): 
                  numMatchesFound+=1
              elif leftDParts == "subscription_id":
                if (len(rightDParts) == len(rightItemParts)) and (rightItemParts.count('-')==4): 
                  numMatchesFound+=1
              elif leftDParts == "new_image_name":
                # strip the prefix, then make sure the remainder is numeric and of the same length, because the datatimes will vary in value while retaining the same format.
                if (rightDParts.startswith('empty_image')) and (rightItemParts.startswith('empty_image')):
                  if len(rightDParts.replace('empty_image', '').replace(' ','')) == len(rightItemParts.replace('empty_image', '').replace(' ','')):
                    if (rightDParts.replace('empty_image', '').replace(' ','')).isdigit() and (rightItemParts.replace('empty_image', '').replace(' ','')).isdigit():
                      numMatchesFound+=1
              elif rightDParts == rightItemParts:
                numMatchesFound+=1
              else:
                print('... Failed to match: ', leftDParts, ' ', leftItemParts)
                print(rightDParts, ' ', rightItemParts)
                print('os.path.exists(rightDParts) is: ', os.path.exists(rightDParts))
                print('os.path.exists(rightItemParts) is: ', os.path.exists(rightItemParts))
                quit('---eee---')

    print("... numMatchesFound is: ", numMatchesFound)
    print("... numMatchesNeeded is: ", numMatchesNeeded)
#    print("matchedList is: ", matchedList)
#    quit('www---ooo---kkk!')
    if numMatchesFound == numMatchesNeeded:
      returnVal = True
    return returnVal

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
  def getSystemConfig_TerraformPacker(self):
    systemConfig = {
      'keysDir': '$Default', 
      'cloud': 'azure', 
      'organization': 'a1b2c', 
      'tags': {'networkName': 'name-of-vnet', 'systemName': 'name-of-system', 'environmentName': 'name-of-environment', 'ownerName': 'name-of-owner'}, 
      'foundation': {
        'instanceName': 'tf-test', 
        'templateName': 'azure-building-blocks/terraform/emptyfoundation',
        'controller': 'terraform',
        'resourceGroupName': 'myEmptyTestRG',
        'resourceGroupRegion': 'westus',
        'canary': 'isabird',
        'labrador': 'isadog',
        'preprocessor': {'locationOn': 'aws-building-blocks/scripts/hello1.py', 'commandOn': 'python $location', 'locationOff': 'aws-building-blocks/scripts/hello2.py', 'commandOff': 'python $location'}, 
        'postprocessor': {'locationOn': 'aws-building-blocks/scripts/hello3.py', 'commandOn': 'python $location', 'locationOff': 'aws-building-blocks/scripts/hello4.py', 'commandOff': 'python $location'}, 
        'mappedVariables': {
          'subscriptionId': '$keys',
          'tenantId': '$keys',
          'clientId': '$keys',
          'clientSecret': '$keys',
          'resourceGroupRegion': '$this.foundation',
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
        'backendVariables': {
          'storage_account_name': '$keys.storageAccountName',
          'container_name': '$keys',
          'key': 'adminaccounts.networkfoundation.tfstate',
          'access_key': '$keys.tfBackendStorageAccessKey'
        },
        'images': [
          {
            'instanceName': 'EMPTY_IMAGE',
            'templateName': 'azure-building-blocks/packer/empty-image',
            'controller': 'packer',
            'keySourceFile': '$env.ACM_SOURCE_KEYS',
            'canine': 'describesadog',
            'feline': 'cat-like',
            'mappedVariables': {
              'ssh_user': 'packer',
              'ssh_pass': 'just-me-123',
              'file_secret_name': 'acmSecretsFile',
              'vault_name': 'agentsFoundationVault',
              'init_script': '$customFunction.addPath.\\azure-building-blocks\scripts\empty-cloudinit-packer.sh',
              'new_image_name': '$customFunction.addDateTime.EMPTY_IMAGE',
              'region': '$this.foundation.resourceGroupRegion',
              'resource_group': '$this.foundation.resourceGroupName',
              'az_server': '$keys.azdoOrgServiceURL',
              'az_pat': '$keys.azdoOrgPAT',
              'tenant_id': '$keys.tenantId',
              'subscription_id': '$keys.subscriptionId',
              'client_secret': '$keys.clientSecret',
              'client_id': '$keys.clientId',
              'KeyName': '$keys.KeyName', 
              'clientName': '$keys',
              'canary': '$this.foundation',
              'lab': '$this.foundation.labrador',
              'rabid': '$this.instance.canine',
              'feline': '$this.instance',
              'networkName': '$this.tags',
              'environ': '$this.tags.environmentName',
              'vpcCIDR': '$this.foundationMapped',
              'alternate': '$this.foundationMapped.secondString',
              'first_output_var': '$customFunction.foundationOutput',
              'secondVar': '$customFunction.foundationOutput.second_output_var',
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
              'firstSharedVariable': 'justthis',
              'KeyName': '$keys.KeyName', 
              'clientName': '$keys',
              'canary': '$this.foundation',
              'lab': '$this.foundation.labrador',
              'networkName': '$this.tags',
              'environ': '$this.tags.environmentName',
              'vpcCIDR': '$this.foundationMapped',
              'alternate': '$this.foundationMapped.secondString',
              'first_output_var': '$customFunction.foundationOutput',
              'secondVar': '$customFunction.foundationOutput.second_output_var',
              'makePath': '$customFunction.addPath./azure-building-blocks/arm',
              'now': '$customFunction.currentDateTime',
              'imageId': 'empty_image',
              'addOrgTest': '$customFunction.addOrganization.somestring',
              'resourceGroupName': '$this.foundation',
              'clientSecret': '$keys',
              'clientId': '$keys',
              'tenantId': '$keys',
              'subscriptionId': '$keys'
            }
          },
          'instances': [
            {
              'instanceName': 'tf-service',
              'templateName': 'azure-building-blocks/terraform/snet-agents',
              'controller': 'terraform',
              'resourceGroupName': 'myEmptyInstanceRG',
              'resourceGroupRegion': 'westus',
              'imageName': 'arm-image', 
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
                'first_output_var': '$customFunction.foundationOutput',
                'secondVar': '$customFunction.foundationOutput.second_output_var',
                'makePath': '$customFunction.addPath./azure-building-blocks/arm',
                'now': '$customFunction.currentDateTime',
                'addOrgTest': '$customFunction.addOrganization.somestring',
                'imageName': 'empty_image',
                'cidrSubnet': '10.0.6.0/24',
                'adminUser': 'azureuser',
                'adminPwd': 'abc-some-pwd-123',
                'cloudInit': '$customFunction.addPath.\\azure-building-blocks\scripts\startup-script-demo.sh'
              },
              'backendVariables': {
                'storage_account_name': '$keys.storageAccountName',
                'container_name': '$keys',
                'key': 'agents.empty-subnet.tfstate',
                'access_key': '$keys.tfBackendStorageAccessKey'
              }
            }
          ]
        }
      }
    }
    return systemConfig

#UNCOMMENT THE FOLLOWING FUNCTION BECAUSE IT IS CRITICAL.  WE ARE JUST COMMENTING IT DURING DEVELOPMENT OF OTHER THINGS FOR CLARITY.
  def getSystemConfig_TfBackendAzrm(self):
    systemConfig = {
      'keysDir': '$Output\\adminAccounts', 
      'forceDelete': 'True',
      'cloud': 'azure', 
      'organization': 'a1b2c', 
      'tags': {'networkName': 'name-of-vnet', 'systemName': 'name-of-system', 'environmentName': 'name-of-environment', 'ownerName': 'name-of-owner'}, 
      'serviceTypes': {
        'tfBackend': {
          'instances': [
            {
              'instanceName': 'adminAccounts',
              'deploymentName': 'adminAccountsTfBackend',
              'templateName': 'azure-building-blocks/arm/tfbackend.json',
              'emptyTemplateName': 'azure-building-blocks/arm/empty.template.json',
              'controller': 'arm',
              'type': 'azurerm2',
              'preprocessor': {
                'locationOn': 'azure-building-blocks/scripts/hello1.py',
                'commandOn': 'python $location',
                'locationOff': 'azure-building-blocks/scripts/hello2.py',
                'commandOff': 'python $location'
              },
              'postprocessor': {
                'locationOn': 'azure-building-blocks/scripts/hello3.py',
                'commandOn': 'python $location',
                'locationOff': 'azure-building-blocks/scripts/hello4.py',
                'commandOff': 'python $location'
              },
              'keyVaultName': 'adminAccountsBackend',
              'keyName': 'adminAccountsBackendKey',
              'environment': 'Dev',
              'resourceGroupName': 'adminAccountsTfBackendDev',
              'resourceGroupRegion': 'westus',
              'mappedVariables': {
                'storageAccountName': '$customFunction.addOrganization.adminaccounts',
                'environmentName': '$this.tags.environmentName',
                'resourceGroupRegion': '$this.instance.resourceGroupRegion'
              }
            }
          ]
        }
      }
    }
    return systemConfig

  def destroyInfrastructureUsedInTest(self, config_cliprocessor, controller_terraform, controller_arm):
    # Seventh, re-set the values that will be passed into the call to terraformCrudOperation that will destroy the foundation.
    # Keys for the foundation must be sourced relative to the tfbackend
    systemConfig = self.getSystemConfig_TfBackendAzrm()
    serviceType = 'tfBackend'
    keyDir = self.getKeyDir(systemConfig, config_cliprocessor)
    instanceName = systemConfig.get('serviceTypes').get(serviceType).get('instances')[0].get('instanceName')
    secretType = 'secret_'+instanceName
    self.setAcmVariables(config_cliprocessor, secretType)
    # The rest of the foundation's values come from the foundation's config as follows
    systemConfig = self.getSystemConfig_TerraformPacker()
    operation = 'off'
    instance = None
    typeParent = 'none'
    typeName = 'networkFoundation'
    parentInstanceName = None
    typeGrandChild = None
    typeInstanceName = None

    # Eigth, destroy real foundation and real image that were used in this test
    ct = controller_terraform()
    ct.terraformCrudOperation(operation, keyDir, systemConfig, instance, typeParent, typeName, typeGrandChild, typeInstanceName)

    # Ninth, set variables to pull the real secrets to we can destroy the tfbackend
    self.setAcmVariables(config_cliprocessor, 'secret')

    # Tenth, Destroy the terraform backend
    systemConfig = self.getSystemConfig_TfBackendAzrm()
    serviceType = 'tfBackend'
    instance = systemConfig.get('serviceTypes').get(serviceType).get('instances')[0]
    print('instance is: ', str(instance))
    #The following will have to call arm destroyDeployment(systemConfig, instance, caller)
    caller = 'serviceInstance'
    carm = controller_arm()
    carm.destroyDeployment(systemConfig, instance, caller)

    #Eleventh, delete the new key files that were created for these tests
    #THE FOLLOWING BLOCK DELETES THE KEY FILE, BUT YOU NEED THE KEYFILE DURING TEST DEVELOPMENT.
    self.deleteAcmKeys()

#UNCOMMENT THIS NEXT FUNCTION BECAUSE IT WORKS FINE.  JUST COMMENTING IT HERE SO WE CAN ISOLATE OTHER TESTS BELOW IT DURING DEVELOPMENT.
  def test_terraform_foundation_VarsFragmentContents(self):
    self.addAcmDirToPath()
    from command_builder import command_builder
    import config_cliprocessor
    self.setAcmVariables(config_cliprocessor)
    correctExpectedResponse = [
'subscriptionId="example-subscriptionId"',
'tenantId="example-tenantId"',
'clientId="example-clientId"',
'clientSecret="example-clientSecret"',
'resourceGroupRegion="westus"',
'resourceGroupName="myEmptyTestRG"',
'vpcCIDR="10.0.0.0/16"',
'secondString="bencher"',
'clientName="example-clientName"',
'subName="example-subscriptionName"',
'labrador="isadog"',
'tName="isabird"',
'networkName="name-of-vnet"',
'owner="name-of-owner"',
'makePath="userCallingDir\\azure-building-blocks\\arm"',
'now="20220624125048860330"',
'addOrgTest="somestringa1b2c"'
    ]
    cb = command_builder()
    systemConfig = self.getSystemConfig_TerraformPacker()
    serviceType = None
    instance = systemConfig.get("foundation")
    mappedVariables = systemConfig.get('foundation').get('mappedVariables')
    tool = 'terraform'
    outputDict = {}
    returnVal = self.checkVarsReturnedAgainstExpected(cb, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponse)
    print('returnVal is: ', returnVal)
    #THE FOLLOWING BLOCK DELETES THE KEY FILE, BUT YOU NEED THE KEYFILE DURING TEST DEVELOPMENT.
    self.deleteAcmKeys()
    self.assertTrue(returnVal)

#UNCOMMENT THIS NEXT FUNCTION BECAUSE IT WORKS FINE.  JUST COMMENTING IT HERE SO WE CAN ISOLATE OTHER TESTS BELOW IT DURING DEVELOPMENT.
  def test_packer_image_VarsFragmentContents(self):
    self.addAcmDirToPath()
    from command_builder import command_builder
    import config_cliprocessor
    from controller_arm import controller_arm
    from controller_terraform import controller_terraform
    from controller_image import controller_image
    from controller_tfbackendazrm import controller_tfbackendazrm
    from controller_packer import controller_packer

    # First, set variables to pull the real secrets to we can create the tfbackend
    self.setAcmVariables(config_cliprocessor, 'secret')

    # Second, Create the terraform backend
    systemConfig = self.getSystemConfig_TfBackendAzrm()
    serviceType = 'tfBackend'
    instance = systemConfig.get('serviceTypes').get(serviceType).get('instances')[0]
    armParamsDict = {"caller":'serviceInstance', "serviceType":serviceType}
    print('instance is: ', str(instance))
    tfbknd = controller_tfbackendazrm()
    tfbknd.createTfBackend(systemConfig, instance, armParamsDict)

    # Third, set the values that will be passed into the call to terraformCrudOperation that will create the foundation.
    instanceName = systemConfig.get('serviceTypes').get(serviceType).get('instances')[0].get('instanceName')
    secretType = 'secret_'+instanceName
    self.setAcmVariables(config_cliprocessor, secretType)
    systemConfig = self.getSystemConfig_TerraformPacker()
    operation = 'on'
    keyDir = self.getKeyDir(systemConfig, config_cliprocessor)
    instance = None
    typeParent = 'none'
    typeName = 'networkFoundation'
    parentInstanceName = None
    typeGrandChild = None
    typeInstanceName = None

    # Fourth, create real foundation and real image to make sure that foundationOutput and mostRecentImage functions work properly
    ct = controller_terraform()
    ct.terraformCrudOperation(operation, keyDir, systemConfig, instance, typeParent, typeName, typeGrandChild, typeInstanceName)

    # Fifth, validate contents of the packer vars fragment
    cb = command_builder()
    image = systemConfig.get('foundation').get('images')[0]
    cp = controller_packer()
    tool = 'packer'
    correctExpectedResponse_Packer = {
"ssh_user": "packer", 
"ssh_pass": "just-me-123", 
"ssh_pass": "xxxxxxxxxxx", 
"file_secret_name": "acmSecretsFile", 
"vault_name": "agentsFoundationVault", 
"init_script": "userCallingDir\\\\\\\\azure-building-blocks\\\\scripts\\\\empty-cloudinit-packer.sh", 
"new_image_name": "empty_image20220630135850568567", 
"region": "westus", 
"resource_group": "myEmptyTestRG", 
"az_server": "https://dev.azure.com/someOrg",  
"az_pat": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", 
"tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",  
"subscription_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", 
"client_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", 
"client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", 
"KeyName": "image=maker", 
"clientName": "Demo_Sandbox", 
"canary": "isabird", 
"lab": "isadog", 
"rabid": "describesadog", 
"feline": "cat-like", 
"networkName": "name-of-vnet", 
"environ": "name-of-environment", 
"vpcCIDR": "10.0.0.0/16", 
"alternate": "bencher", 
"first_output_var": "one-value", 
"secondVar": "two-value", 
"makePath": "userCallingDir\\\\\\\\azure-building-blocks\\\\arm", 
"currentDateTimeAlphaNumeric": "20220630135850574988", 
"addOrgTest": "somestringa1b2c"
    }

    outputDict = {}
    cbld = command_builder()
    returnValPkr = self.checkVarsReturnedAgainstExpected(cbld, systemConfig, None, image, image.get('mappedVariables'), tool, outputDict, correctExpectedResponse_Packer)
    print('returnValPkr is: ', returnValPkr)

    # Fifth, create an empty image.  Later, remember to add more granular testing of each input variable
    ci = controller_image()
    ci.buildImages(systemConfig, keyDir)

    # Sixth, create the inputs for the service instance
    # Note: Keeping same values for setAcmVariables(..) because the keys must be sourced from the tfbackend instance.  
    systemConfig = self.getSystemConfig_TerraformPacker()
    serviceType = 'subnetsWithScaleSet'
    instance = systemConfig.get('serviceTypes').get(serviceType).get('instances')[0]
    instanceName = instance.get('instanceName')
    mappedVariables = instance.get('mappedVariables')
    tool = 'terraform'
    outputDict = {}
    cbdr = command_builder()
    instanceVarsFragment = cbdr.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, tool, self)
    print('xxx  instanceVarsFragment is: ', instanceVarsFragment)
    correctExpectedResponse = [
'firstSharedVariable="justthis"',
'KeyName="image=maker"',
'clientName="Demo_Sandbox"',
'canary="isabird"',
'lab="isadog"',
'networkName="name-of-vnet"',
'environ="name-of-environment"',
'vpcCIDR="10.0.0.0/16"',
'alternate="bencher"',
'first_output_var="one-value"',
'secondVar="two-value"',
'makePath="userCallingDir\\\\azure-building-blocks\\arm"',
'now="20220629152616440812"',
'imageId="empty_image"',
'addOrgTest="somestringa1b2c"',
'resourceGroupName="myEmptyTestRG"',
'clientSecret="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"',
'clientId="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"',
'tenantId="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"',
'subscriptionId="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"',
'InstanceType="t2.small"',
'oneVar="one-value"',
'twoInstanceVar="two-value"',
'imageName="empty_image"',
'cidrSubnet="10.0.6.0/24"',
'adminUser="azureuser"',
'adminPwd="xxxxxxxxxxxxxxxx"',
'cloudInit="userCallingDir\\\\azure-building-blocks\\scripts\\startup-script-demo.sh"'
    ]

    instanceReturnVal = self.checkVarsReturnedAgainstExpected(cbdr, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponse)
    print('instanceReturnVal is: ', instanceReturnVal)
    self.destroyInfrastructureUsedInTest(config_cliprocessor, controller_terraform, controller_arm)

    if (returnValPkr == True) and (instanceReturnVal == True):
      returnVal = True
    else:
      returnVal = False
    #Finally, complete the test
    self.assertTrue(returnVal)


if __name__ == '__main__':
    unittest.main()

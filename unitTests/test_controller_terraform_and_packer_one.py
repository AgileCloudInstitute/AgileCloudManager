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
       #python -m unittest AgileCloudManager.unitTests.test_controller_terraform_and_packer_one
  
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
      if platform.system() == 'Windows':
        inputsDir = os.path.expanduser('~') + '/acm/keys/starter/'
      elif platform.system() == 'Linux':
        inputsDir = os.path.expanduser('~') + '/acmconfig/'
    else:
      if platform.system() == 'Windows':
        inputsDir = os.path.expanduser('~') + '/acm/keys/starter/'
#        inputsDir = os.path.expanduser('~') + '/acm/keys/'+inputType+'/'
      elif platform.system() == 'Linux':
#        inputsDir = os.path.expanduser('~') + '/acmconfig/'
        inputsDir = os.path.expanduser('~') + '/acmconfig2/adminAccounts/'
 
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
    dirOfOutput = self.getAcmUserHome() + '\\keys\\' 
    dirOfOutput = self.formatPathForOS(dirOfOutput)
    if inputType == 'sanitized':
      config_cliprocessor.inputVars['dirOfOutput'] = inputsDir
#    elif inputType == 'secret':
#      config_cliprocessor.inputVars['dirOfOutput'] = self.formatPathForOS(str(pathlib.Path(inputsDir).parent.resolve())+'/')
    else:
      config_cliprocessor.inputVars['dirOfOutput'] = dirOfOutput #self.formatPathForOS(str(pathlib.Path(inputsDir).parent.resolve())+'/')
    #--Start test removing 2 character indent
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
    #--End test removing 2 character indent
#Test comment out next line and replace with line after it.
#    config_cliprocessor.inputVars["tfvarsFileAndPath"] = varsFileAndPath
    config_cliprocessor.inputVars["tfvarsFileAndPath"] = tfvarsFileAndPath
    config_cliprocessor.inputVars["userCallingDir"] = userCallingDir
    config_cliprocessor.inputVars["verboseLogFilePath"] = verboseLogFilePath

  def getAcmUserHome(self):
    if platform.system() == 'Windows':
      acmUserHome = os.path.expanduser("~")+'/acm/'
    elif platform.system() == 'Linux':
      acmUserHome = '/usr/acm/'
    if not os.path.exists(acmUserHome):
      os.makedirs(acmUserHome, exist_ok=True) 
    return acmUserHome


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
    print('+++ propVal from systemConfig is: ', propVal)
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
    print('xxx ...  propVal is: ', propVal)
    return propVal


  def checkVarsReturnedAgainstExpected(self, cb, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponse):
    varsFragment = cb.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, tool, self, outputDict)
    print('varsFragment is: ', varsFragment)
    fragParts = varsFragment.split(' ')
    varFilePart = 'empty'
    for part in fragParts:
      if tool == 'arm':
        if '--parameters' not in part:
          varFilePart = part
      if tool == "terraform":
        if part.startswith('-var-file='):
          varFilePart = part
      if tool == 'packer':
        if part.startswith('-var-file='):
          varFilePart = part
    print('varFilePart is: ', varFilePart)
    if varFilePart == 'empty':
      logString = "ERROR: varsFragment did not include a properly formed --varFile:// flag. "
      print(logString)
      sys.exit(1)
    if tool == 'arm':
      acmKeysFile = varFilePart.replace('--parameters','').replace(' ', '')
    elif tool == 'terraform':
      acmKeysFile = varFilePart.replace('-var-file=','').replace(' ', '').replace('"','')
    elif tool == 'packer':
      acmKeysFile = varFilePart.replace('-var-file=','').replace(' ', '').replace('"','')
    returnVal = False
    with open(acmKeysFile, "rb" ) as f:
      if tool == 'terraform':
        returnedData = f.read().decode().splitlines()
      elif tool == 'packer':
        returnedData = json.load(f)
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
      print('ERROR: vars file has the wrong number of lines.  ')
      sys.exit(1)
    for item in varsObject:
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
              print(logString)
              sys.exit(1)
            if (len(dParts)==2):
              leftDParts = dParts[0].replace(' ','')
              rightDParts = dParts[1].replace(' ','')
            elif (len(dParts)==3):
              leftDParts = dParts[0].replace(' ','')
              rightDParts = dParts[1].replace(' ','')+'='+dParts[2].replace(' ','')
            else:
              logString = "ERROR: Wrong number of = signs in one of the variable lines. Only one or two = sign per line allowed. "
              print(logString)
              sys.exit(1)
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
                sys.exit(1)
      elif tool == 'packer':
        print('type(item) is: ', type(item))
        print('str(item) is: ', str(item))
        leftItemParts = item
        rightItemParts = varsObject.get(item)
        print('leftItemParts is: ', str(leftItemParts))
        print('rightItemParts is: ', str(rightItemParts))
        for d in correctExpectedResponse:
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
                  sys.exit(1)
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
                sys.exit(1)
    print("... numMatchesFound is: ", numMatchesFound)
    print("... numMatchesNeeded is: ", numMatchesNeeded)
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

#      'keysDir': '$Default', 
#UNCOMMENT THE FOLLOWING FUNCTION BECAUSE IT IS CRITICAL.  WE ARE JUST COMMENTING IT DURING DEVELOPMENT OF OTHER THINGS FOR CLARITY.
  def getSystemConfig_TerraformPacker(self):
    systemConfig = {
      'keysDir': '$Output\\adminAccounts', 
      'cloud': 'azure', 
      'organization': 'tstaxy', 
      'tags': {'networkName': 'name-of-vnet', 'systemName': 'name-of-system', 'environmentName': 'name-of-environment', 'ownerName': 'name-of-owner'}, 
      'foundation': {
        'instanceName': 'tf-test', 
        'templateName': 'azure-building-blocks/terraform/emptyfoundation',
        'controller': 'terraform',
        'resourceGroupName': 'myEmptyTestRG',
        'resourceGroupRegion': 'eastus',
        'canary': 'isabird', 
        'labrador': 'isadog',
        'preprocessor': {'locationOn': 'aws-building-blocks/scripts/hello1.py', 'commandOn': self.getPython()+' $location', 'locationOff': 'aws-building-blocks/scripts/hello2.py', 'commandOff': self.getPython()+' $location'}, 
        'postprocessor': {'locationOn': 'aws-building-blocks/scripts/hello3.py', 'commandOn': self.getPython()+' $location', 'locationOff': 'aws-building-blocks/scripts/hello4.py', 'commandOff': self.getPython()+' $location'}, 
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
#this is not the original.  This should be wrong and is thus commented out.      'keysDir': '$Default', 
      'forceDelete': 'True',
      'cloud': 'azure', 
      'organization': 'tstaxy', 
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
              'type': 'azurerm',
              'preprocessor': {
                'locationOn': 'azure-building-blocks/scripts/hello1.py',
                'commandOn': self.getPython()+' $location',
                'locationOff': 'azure-building-blocks/scripts/hello2.py',
                'commandOff': self.getPython()+' $location'
              },
              'postprocessor': {
                'locationOn': 'azure-building-blocks/scripts/hello3.py',
                'commandOn': self.getPython()+' $location',
                'locationOff': 'azure-building-blocks/scripts/hello4.py',
                'commandOff': self.getPython()+' $location'
              },
              'keyVaultName': 'adminAccountsBackend',
              'keyName': 'adminAccountsBackendKey',
              'environment': 'Dev',
              'resourceGroupName': 'adminAccountsTfBackendDevTest',
              'resourceGroupRegion': 'eastus',
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
    from AgileCloudManager.app.command_builder import command_builder
    import AgileCloudManager.app.config_cliprocessor
    self.setAcmVariables(AgileCloudManager.app.config_cliprocessor)
    correctExpectedResponse = [
'subscriptionId="example-subscriptionId"',
'tenantId="example-tenantId"',
'clientId="example-clientId"',
'clientSecret="example-clientSecret"',
'resourceGroupRegion="eastus"',
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
'now="20240624125048860330"',
'addOrgTest="somestringtstaxy"'
    ]
    cb = command_builder()
    systemConfig = self.getSystemConfig_TerraformPacker()
    serviceType = None
    instance = systemConfig.get("foundation")
    mappedVariables = systemConfig.get('foundation').get('mappedVariables')
    tool = 'terraform'
    outputDict = {}
    print("xxxzzzvvv config_cliprocessor.inputVars.get('dirOfOutput') is: ", AgileCloudManager.app.config_cliprocessor.inputVars.get('dirOfOutput'))
    returnVal = self.checkVarsReturnedAgainstExpected(cb, systemConfig, serviceType, instance, mappedVariables, tool, outputDict, correctExpectedResponse)
    #THE FOLLOWING BLOCK DELETES THE KEY FILE, BUT YOU NEED THE KEYFILE DURING TEST DEVELOPMENT.
    self.deleteAcmKeys()
    print('test_terraform_foundation_VarsFragmentContents() returnVal is: ', returnVal)
    self.assertTrue(returnVal)


if __name__ == '__main__':
    unittest.main()

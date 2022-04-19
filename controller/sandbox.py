import os
import platform
import shutil
from pathlib import Path


def writeKeyFiles(keysDir):
  with open(keysDir+'keys.yaml', 'w') as file:
    file.write('secretsType: master\n')
    file.write('name: <put-actual-secret-value-here>\n')
    file.write('clientName: <put-actual-secret-value-here>\n')
    file.write('clientId: <put-actual-secret-value-here>\n')
    file.write('clientSecret: <put-actual-secret-value-here>\n')
    file.write('subscriptionId: <put-actual-secret-value-here>\n')
    file.write('subscriptionName: <put-actual-secret-value-here>\n')
    file.write('tenantId: <put-actual-secret-value-here>\n')
    file.write('azdoOrgPAT: <put-actual-secret-value-here>\n')
    file.write('azdoOrgServiceURL: <put-actual-secret-value-here>\n')
    file.write('gitUsername: <put-actual-secret-value-here>\n')
    file.write('gitPass: <put-actual-secret-value-here>\n')
  with open(keysDir+'gitCred.yaml', 'w') as file:
    file.write('gitUsername: <store-username-here>\n')
    file.write('gitPassword: <store-password-here>\n')
  with open(keysDir+'IamUserKeys.yaml', 'w') as file:
    file.write('keyPairs:\n')
    file.write('  - name: iamUserKeyPair\n')
    file.write('    _public_access_key: <put-actual-secret-value-here>\n')
    file.write('    _secret_access_key: <put-actual-secret-value-here>\n')

def createDirectoryStructure():
  userCallingDir = os.path.abspath(".")
  print('userCallingDir is: ', userCallingDir)
  path = Path(userCallingDir)
  parentPath = path.parent
  print('parentPath is: ', parentPath)
  print('Contents of parent directory are: ')
  for item in os.listdir(path.parent):
    print('... ', item)
  acmAdmin = str(parentPath) + '\\acmAdmin'
  adminPath = Path(acmAdmin)
  if not os.path.exists(adminPath):
    os.mkdir(adminPath)

  keys = acmAdmin + '\\keys'
  keysPath = Path(keys)
  if not os.path.exists(keysPath):
    os.mkdir(keysPath)

  keys = acmAdmin + '\\keys\\shared\\'
  keysPath = Path(keys)
  if not os.path.exists(keysPath):
    os.mkdir(keysPath)
    writeKeyFiles(str(keysPath)+'\\')

  binaries = acmAdmin + '\\binaries'
  path = Path(binaries)
  if not os.path.exists(path):
    os.mkdir(path)

  dynamicVars = acmAdmin + '\\dynamicVars'
  path = Path(dynamicVars)
  if not os.path.exists(path):
    os.mkdir(path)

  logs = acmAdmin + '\\logs'
  path = Path(logs)
  if not os.path.exists(path):
    os.mkdir(path)

  print('Contents of acmAdmin directory are: ')
  for item in os.listdir(adminPath):
    print('... ', item)

  print('Contents of keys directory are: ')
  for item in os.listdir(keysPath):
    print('... ', item)

def removeDirectoryStructure():
  userCallingDir = os.path.abspath(".")
  print('userCallingDir is: ', userCallingDir)
  path = Path(userCallingDir)
  parentPath = path.parent
  print('parentPath is: ', parentPath)
  print('Contents of parent directory BEFORE DELETION are: ')
  for item in os.listdir(parentPath):
    print('... ', item)
  acmAdmin = str(parentPath) + '\\acmAdmin'
  adminPath = Path(acmAdmin)
  shutil.rmtree(adminPath)
  print('Contents of parent directory AFTER DELETION are: ')
  for item in os.listdir(parentPath):
    print('... ', item)



createDirectoryStructure()
removeDirectoryStructure()

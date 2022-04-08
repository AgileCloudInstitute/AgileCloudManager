## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import subprocess
import re
import requests
import base64
import logWriter
import json
import sys 
import os

import config_cliprocessor
import command_builder
import controller_terraform

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

terraformResult = ''  
success_packer = ''

def getShellJsonResponse(cmd,counter=0):
  process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
  data = process.stdout
  err = process.stderr
  logString = "data string is: " + data
  logWriter.writeLogVerbose("acm", logString)
  logString = "err is: " + str(err)
  logWriter.writeLogVerbose("acm", logString)
  logString = "process.returncode is: " + str(process.returncode)
  logWriter.writeLogVerbose("acm", logString)
  logString = "cmd is: " + cmd
  logWriter.writeLogVerbose("acm", logString)
  if process.returncode == 0:
    logString = str(data)
    logWriter.writeLogVerbose("shell", logString)
    decodedData = data #.decode('utf-8')
    return decodedData
  else:
    if counter == 0:
      counter +=1 
      logString = "Sleeping 30 seconds before running the command a second time in case a latency problem caused the first attempt to fail. "
      logWriter.writeLogVerbose('acm', logString)
      import time
      time.sleep(30)
      data = getShellJsonResponse(cmd,counter)
      return data
    else:  
      if "(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found." in str(err):
        logString = "WARNING: "+"(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found."
        logWriter.writeLogVerbose('shell')
        logString = "Continuing because this error message is often benign.  If you encounter downstream problems resulting from this, please report your use case so that we can examine the cause. "
        logWriter.writeLogVerbose('acm', logString)
        return decodedData
      else:
        logString = "Error: " + str(err)
        logWriter.writeLogVerbose("shell", logString)
        logString = "Error: Return Code is: " + str(process.returncode)
        logWriter.writeLogVerbose("shell", logString)
        logString = "ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem."
        logWriter.writeLogVerbose("acm", logString)
        sys.exit(1)

def runShellCommand(commandToRun):
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        logString = decodedline
        logWriter.writeLogVerbose("shell", logString)
      else:
        break

def runPreOrPostProcessor(processorSpecs, operation):
  if operation == 'on':
    location = processorSpecs['locationOn']
    command = processorSpecs['commandOn']
  elif operation == 'off':
    location = processorSpecs['locationOff']
    command = processorSpecs['commandOff']
  fullyQualifiedPathToScript = config_cliprocessor.inputVars.get('app_parent_path')+location
  fullyQualifiedPathToScript = command_builder.formatPathForOS(fullyQualifiedPathToScript)
  commandToRun = command.replace('location',fullyQualifiedPathToScript)
  runShellCommand(commandToRun)

def getAccountKey(commandToRun):
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        logWriter.writeLogVerbose("shell", decodedline)
        return decodedline
      else:
        break

################################################################################################################################
### Start of dependency checks

def checkIfAzInstalled(commandToRun, vers):
    resp = json.loads(getShellJsonResponse(commandToRun))
    cliV = resp['azure-cli']
#...start new
    versParts = vers.split('.')
    cliVParts = cliV.split('.')
    print('versParts is: ', versParts)
    print('cliVParts is: ', cliVParts)
    if (int(cliVParts[0]) >= int(versParts[0])) and (int(cliVParts[1]) >= int(versParts[1])):
      logString = 'Dependency is installed.'
      logWriter.writeLogVerbose("acm", logString)
      return logString
#...end new, start commented out old
#    if cliV.startswith(str(vers)):
#      logString = 'Dependency is installed.'
#      logWriter.writeLogVerbose("acm", logString)
#      return logString
    else:
      logString = "Wrong version of dependency is installed for azure-cli."
      logWriter.writeLogVerbose("acm", logString)
      return logString

def checkIfAzdoInstalled(commandToRun, vers):
    resp = json.loads(getShellJsonResponse(commandToRun))
    logString = 'azdo response is: ' + str(resp)
    logWriter.writeLogVerbose("acm", logString)
    azdoV = resp['extensions']['azure-devops']
    versParts = vers.split('.')
    azdoVParts = azdoV.split('.')
    print('versParts is: ', versParts)
    print('azdoVParts is: ', azdoVParts)
    if (int(azdoVParts[0]) >= int(versParts[0])) and (int(azdoVParts[1]) >= int(versParts[1])):
      logString = 'Dependency is installed.'
      logWriter.writeLogVerbose("acm", logString)
      return logString
    else:
      logString = "Wrong version of dependency is installed for azure-devops extension of azure-cli."
      logWriter.writeLogVerbose("acm", logString)
      return logString

def checkIfInstalled(commandToRun, vers):
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    match = False
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        if vers in decodedline:
          match = True
          logString = "Dependency is installed."
          logWriter.writeLogVerbose("acm", logString)
          return logString
      else:
        break
    logString = 'Dependency is NOT installed.  Please make sure your machine is properly provisioned.'
    logWriter.writeLogVerbose("acm", logString)
    return logString

### End of dependency checks
##################################################################################################################################

def runShellCommandInWorkingDir(commandToRun, workingDir):
    proc = subprocess.Popen( commandToRun,cwd=workingDir, stdout=subprocess.PIPE, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        logString = decodedline
        logWriter.writeLogVerbose("shell", logString)
      else:
        break

def getShellJsonData(cmd, workingDir):
  if "TF_LOG" in os.environ:
    oldTfLog = os.environ["TF_LOG"]
    os.environ["TF_LOG"] = "ERROR"
  process = subprocess.Popen(
      cmd,cwd=workingDir,
      shell=True,
      stdout=subprocess.PIPE)
  data, err = process.communicate()
  filename = workingDir + 'my-directory-list.txt'
  try:
    os.remove(filename)
  except OSError:
    pass
  if process.returncode == 0:
    decodedData = data.decode('utf-8')
    if "TF_LOG" in os.environ:
      os.environ["TF_LOG"] = oldTfLog
    return decodedData
  else:
    print("Error: " + str(err))
    print("Error: Return Code is: " + str(process.returncode))
    print("ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem.")
    if "TF_LOG" in os.environ:
      os.environ["TF_LOG"] = oldTfLog
    sys.exit(1)

def processDecodedLine(decodedline, lineNum, errIdx, commFragment):
  if "Too many command line arguments." in decodedline:
    logString = "Error: The variables you passed into the terraform command were corrupted. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  if "Failed to instantiate provider" in decodedline:
    logString = "Error: Failed to instantiate provider.  Halting program so you can check your configuration and identify the root of the problem. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  if ("giving up after " in decodedline) and (" attempt(s)" in decodedline):
    logString = "Error: Halting program so you can examine upstream logs to discover what the cause is. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  if ("Error: No Images were found for Resource Group" in decodedline) and (commFragment == "apply"):
    logString = "Error: No Images were found for Resource Group.  Halting program so you can check your configuration and identify the root of the problem. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)

  if "Destroy complete!" in decodedline:
    logString = "Found Destroy complete!!"
    logWriter.writeLogVerbose("acm", logString)
    global terraformResult
    terraformResult="Destroyed"
  if "Apply complete!" in decodedline:
    logString = "Found Apply complete!!"
    logWriter.writeLogVerbose("acm", logString)
    terraformResult="Applied"
  return errIdx

def runTerraformCommand(commandToRun, workingDir):
  reachedOutputs = False
  if " apply" in commandToRun:
    commFragment = "apply"
  elif " destroy" in commandToRun:
    commFragment = "destroy"
  elif " output" in commandToRun:
    commFragment = "output"
  else:
    commFragment = "other"
  lineNum = 0
  errIdx = 0
  isError = "no"
  #Make a work item to re-write this function to throw an error and stop the program whenever an error is encountered.
  proc = subprocess.Popen( commandToRun,cwd=workingDir,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
  while True:
    line = proc.stdout.readline()
    if line:
      lineNum += 1
      thetext=line.decode('utf-8').rstrip('\r|\n')
      decodedline=ansi_escape.sub('', thetext)
      logWriter.writeLogVerbose("terraform", decodedline)
#      print('commFragment is: ', commFragment)
      if 'Outputs' in decodedline:
        reachedOutputs = True
      if (commFragment == 'output'):
        print('decodedLine is: ', decodedline)
        if (decodedline.count('=') == 1):
          lineParts = decodedline.split('=')
          key = lineParts[0].replace(' ','').replace('"','').replace("'","")
          value = lineParts[1].replace(' ','').replace('"','').replace("'","")
          controller_terraform.tfOutputDict[key] = value
  #          print('controller_terraform.tfOutputDict is: ', str(controller_terraform.tfOutputDict))
      if (commFragment != 'output') and (controller_terraform.foundationApply == True):
        print('decodedLine is: ', decodedline)
        if (decodedline.count('=') == 1) and (reachedOutputs == True):
          lineParts = decodedline.split('=')
          key = lineParts[0].replace(' ','').replace('"','').replace("'","")
          value = lineParts[1].replace(' ','').replace('"','').replace("'","")
          controller_terraform.tfOutputDict[key] = value
#          print('controller_terraform.tfOutputDict is: ', str(controller_terraform.tfOutputDict))
      errIdx = processDecodedLine(decodedline, lineNum, errIdx, commFragment)
    else:
      break
#  if commFragment == 'output':
#    quit('OUTPUT!!!')

def runPackerCommand(commandToRun, workingDir):
    proc = subprocess.Popen( commandToRun,cwd=workingDir,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        logWriter.writeLogVerbose("packer", decodedline)
        if "Builds finished. The artifacts of successful builds are" in decodedline:
          global success_packer
          success_packer="true"
        elif "machine readable:" in decodedline:
          if "error-count" in decodedline:
            logString = "error-count is in decodedline.  "
            logWriter.writeLogVerbose("acm", logString)
            success_packer="false"
      else:
        break

def getPoolQueueIdApiRequest(orgName, projId, qName, azPat):  
    orgName = orgName.replace('"','')
    orgName = orgName.replace("'","")
    azPat = azPat.replace('"','')
    azPat = azPat.replace("'","")
    #Assemble headers  
    personal_access_token = ":"+azPat
    headers = {}  
    headers['Content-type'] = "application/json"  
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))  
    #Assemble the endpoint URL
    #Get the Agent Pool Queues whose name matches the search criteria.  This should only be one queue because name should be a unique key.  
    api_version_p = "5.1-preview.1"
    #GET https://dev.azure.com/{organization}/{project}/_apis/distributedtask/queues?queueName={queueName}&actionFilter={actionFilter}&api-version=5.1-preview.1
    queues_url = ("https://dev.azure.com/%s/%s/_apis/distributedtask/queues?queueName=%s&api-version=%s" % (orgName, projId, qName, api_version_p))
    logString = "-------------------------------------------------------------"
    logWriter.writeLogVerbose("acm", logString)
    logString = "queues_url is: " + queues_url
    logWriter.writeLogVerbose("acm", logString)
    #Make the request    
    r = requests.get(queues_url, headers=headers)
    logString = "r.status_code is: " + str(r.status_code)
    logWriter.writeLogVerbose("acm", logString)
    #Add some better error handling here to handle various response codes.  We are assuming that a 200 response is received in order to continue here.  
    if r.status_code != 200:
      print(r.content)
      logString = "ERROR: getPoolQueueIdApiRequest() returned a non-200 response code.  Halting program so you can debug."
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
    myQueuesData = r.json()
    logString = "myQueuesData is: " + str(myQueuesData)
    logWriter.writeLogVerbose("acm", logString)
    #Using index 0 here because queue_name should be a unique key that brings only one result in this response
    poolQueueId = myQueuesData['value'][0]['id']
    logString = "poolQueueId is: " + str(poolQueueId)
    logWriter.writeLogVerbose("acm", logString)
    return poolQueueId

def createAzdoServiceEndpointApiRequest(data, azdo_organization_name, azPAT):
    print("data is: ", data)
    print("azdo_organization_name is: ", azdo_organization_name)
    azPAT = azPAT.replace("'","")
    azPAT = azPAT.replace('"','')
    print("azPAT is: ", azPAT)
    logString = "0 test  "
    logWriter.writeLogVerbose("acm", logString)
    try:
      personal_access_token = ":"+azPAT
      headers = {}
      headers['Content-type'] = "application/json"
      headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
      api_version = "6.0-preview.4"
      url = ("https://dev.azure.com/%s/_apis/serviceendpoint/endpoints?api-version=%s" % (azdo_organization_name, api_version))
      print("url is: ", url)
      logString = "1 test  "
      logWriter.writeLogVerbose("acm", logString)
    except Exception as e:
      logString = "1 ERROR: Attempting to create the azure devops service endpoint triggered the following exception:  "
      logWriter.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      logWriter.writeLogVerbose("acm", logString)
      exit(1)
    try:
      r = requests.post(url, data=json.dumps(data), headers=headers)
      logString = "2 test  "
      logWriter.writeLogVerbose("acm", logString)
    except Exception as e:
      logString = "2 ERROR: Attempting to create the azure devops service endpoint triggered the following exception:  "
      logWriter.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      logWriter.writeLogVerbose("acm", logString)
      exit(1)
    try:
      respCode = str(r.status_code)
      logString = "r.status_code is: " + respCode
      logWriter.writeLogVerbose("acm", logString)
      logString = "r.json() is: " + str(r.json())
      logWriter.writeLogVerbose("acm", logString)
    except Exception as e:
      logString = "3 ERROR: Attempting to create the azure devops service endpoint triggered the following exception:  "
      logWriter.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      logWriter.writeLogVerbose("acm", logString)
      logString = str(r.content).format(str(e.args[0])).encode("utf-8")
      logWriter.writeLogVerbose("acm", logString)
      exit(1)

    return respCode, r.json()

def runShellCommandForTests(commandToRun):
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        print(decodedline)
      else:
        proc.kill()
        break
    proc.kill()

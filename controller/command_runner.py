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

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

#NOTE: Add functionality to accept variable names that are themselves variables.  
#      The output variable names from terraform module files can be auto imported with 
#      slice indices to be processed by the runTerraformCommand() function so that downstream 
#      modules can use those output variables as their own input without need to hardwire the 
#      variable names in code as we are doing here for now.  
#AWS output vars
vpc_id = ''  
vpc_cidr = ''  
subnet_id = ''  
sg_id = ''  
sg_name = ''  
instance_profile_name = ''  
iam_role_name = ''  
vm_ip_pub = ''  
#Azure output vars
appId = ''
subscription_id = ''  
tenant_id = ''  
pipes_resource_group_name = ''  
pipes_resource_group_region = ''  
nicName = ''  
storageAccountDiagName = ''  
azuredevops_project_id = ''
azuredevops_service_connection_id = ''

azuredevops_build_definition_id = ''
azuredevops_git_repository_name = ''

vnetName = ''  

azuredevops_build_definition_id = ''
azuredevops_git_repository_name = ''

vaultName = ''

terraformResult = ''  
success_packer = ''

def getShellJsonResponse(cmd):
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE)
    process.wait()
    data, err = process.communicate()
    logString = "data bytes is:" + str(data.decode("utf-8"))
    logWriter.writeLogVerbose("acm", logString)
    logString = "data string is: " + str(data.decode("utf-8"))
    logWriter.writeLogVerbose("acm", logString)
    logString = "err is: " + str(err)
    logWriter.writeLogVerbose("acm", logString)
    logString = "process.returncode is: " + str(process.returncode)
    logWriter.writeLogVerbose("acm", logString)
    logString = "cmd is: " + cmd
    logWriter.writeLogVerbose("acm", logString)
    if process.returncode == 0:
      logString = str(data.decode('utf-8'))
      logWriter.writeLogVerbose("shell", logString)
      decodedData = data.decode('utf-8')
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
    if cliV.startswith(str(vers)):
      logString = 'Dependency is installed.'
      logWriter.writeLogVerbose("acm", logString)
      return logString
    else:
      logString = "Wrong version of dependency is installed for azure-cli."
      logWriter.writeLogVerbose("acm", logString)
      return logString

def checkIfAzdoInstalled(commandToRun, vers):
    resp = json.loads(getShellJsonResponse(commandToRun))
    logString = 'azdo response is: ' + str(resp)
    logWriter.writeLogVerbose("acm", logString)
    azdoV = resp['extensions']['azure-devops']
    if azdoV.startswith(str(vers)):
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
    print('=== commandToRun is: ', commandToRun)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        print('--- decodedline is: ', decodedline)
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
    os.environ["TF_LOG"] = oldTfLog
    return decodedData
  else:
    print("Error: " + str(err))
    print("Error: Return Code is: " + str(process.returncode))
    print("ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem.")
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

  if ("{" not in decodedline) and ("(" not in decodedline) and (")" not in decodedline) and ("*" not in decodedline) and ("." not in decodedline):
    if "vpc_id" in decodedline:
      global vpc_id
      vpc_id=decodedline[9:]
    if "vpc_cidr" in decodedline:
      global vpc_cidr
      vpc_cidr=decodedline[11:]
    if "subnet_id" in decodedline:
      global subnet_id
      subnet_id=decodedline[12:]
    if "sg_id" in decodedline:
      global sg_id
      sg_id=decodedline[8:]
    if "sg_name" in decodedline:
      global sg_name
      sg_name=decodedline[10:]
    if "instance_profile_name" in decodedline:
      global instance_profile_name
      instance_profile_name=decodedline[24:]
    if "iam_role_name" in decodedline:
      global iam_role_name
      iam_role_name=decodedline[16:]
    if "public_ip_of_ec2_instance" in decodedline:
      global vm_ip_pub
      vm_ip_pub=decodedline[28:].replace('"', '')
    if "appId = " in decodedline:
      global appId
      appId=decodedline[8:]
    if "subscription_id" in decodedline:
      global subscription_id
      subscription_id=decodedline[18:]
    if "tenant_id" in decodedline:
      global tenant_id
      tenant_id=decodedline[12:]
    if "pipes_resource_group_name" in decodedline:
      global pipes_resource_group_name
      pipes_resource_group_name=decodedline[28:]
    if "pipes_resource_group_region" in decodedline:
      global pipes_resource_group_region
      pipes_resource_group_region=decodedline[30:]
    if "nicName" in decodedline:
      global nicName
      nicName=decodedline[10:]
    if "storageAccountDiagName" in decodedline:
      global storageAccountDiagName
      storageAccountDiagName=decodedline[25:]
    if "azuredevops_build_definition_id" in decodedline:
      global azuredevops_build_definition_id
      azuredevops_build_definition_id=decodedline[34:]
    if "azuredevops_git_repository_name" in decodedline:
      global azuredevops_git_repository_name
      azuredevops_git_repository_name=decodedline[34:]
    if "vnetName" in decodedline:
      global vnetName
      vnetName=decodedline[11:]
    if "azuredevops_project_id" in decodedline:
      global azuredevops_project_id
      azuredevops_project_id=decodedline[25:]
    if "azuredevops_service_connection_id" in decodedline:
      global azuredevops_service_connection_id
      azuredevops_service_connection_id=decodedline[36:]
    if "azuredevops_service_connection_id_gh" in decodedline:
      global azuredevops_service_connection_id_gh
      azuredevops_service_connection_id_gh=decodedline[39:]
    if "vaultName" in decodedline:
      global vaultName
      vaultName=decodedline[12:]
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
  if " apply " in commandToRun:
    commFragment = "apply"
  elif " destroy " in commandToRun:
    commFragment = "destroy"
  elif " output " in commandToRun:
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
      errIdx = processDecodedLine(decodedline, lineNum, errIdx, commFragment)
    else:
      break

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

## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import subprocess
import re
import requests
import base64
import logWriter
import json

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
#publicIPName = ''  

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
#    print("data bytes is:", data)
#    print("data string is: ", data.decode("utf-8"))
#    print("err is: ", err)
#    print("process.returncode is: ", process.returncode)
    if process.returncode == 0:
        return data.decode('utf-8')
    else:
        print("Error:", err)
        quit("ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem.")
    #return ""
  
def runShellCommand(commandToRun):
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        print(decodedline)
      else:
        break

def getAccountKey(commandToRun):
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        return decodedline
      else:
        break

################################################################################################################################
### Start of dependency checks

def checkIfAzInstalled(commandToRun, vers):
    resp = json.loads(getShellJsonResponse(commandToRun))
    cliV = resp['azure-cli']
    if cliV.startswith(str(vers)):
      return 'Dependency is installed.'
    else:
      return "Wrong version of dependency is installed for azure-cli."

def checkIfAzdoInstalled(commandToRun, vers):
    resp = json.loads(getShellJsonResponse(commandToRun))
    azdoV = resp['extensions']['azure-devops']
    if azdoV.startswith(str(vers)):
      return 'Dependency is installed.'
    else:
      return "Wrong version of dependency is installed for azure-devops extension of azure-cli."

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
          return "Dependency is installed."
      else:
        break
    return 'Dependency is NOT installed.  Please make sure your machine is properly provisioned.'

### End of dependency checks
##################################################################################################################################

def runShellCommandInWorkingDir(commandToRun, workingDir):
    proc = subprocess.Popen( commandToRun,cwd=workingDir, stdout=subprocess.PIPE, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        print(decodedline)
      else:
        break

def processDecodedLine(decodedline):
  if "Error" in decodedline:
    print("\n---------------------------------------------------------\n")
    quit("ERROR found.  Halting program so you can debug.")
  if "Too many command line arguments." in decodedline:
    quit("Error: The variables you passed into the terraform command were corrupted. ")
  if "Failed to instantiate provider" in decodedline:
    quit("Error: Failed to instantiate provider.  Halting program so you can check your configuration and identify the root of the pr0blem. ")
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
  if "appId" in decodedline:
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
    print("Found Destroy complete!!")
    global terraformResult
    terraformResult="Destroyed"
  if "Apply complete!" in decodedline:
    print("Found Apply complete!!")
    terraformResult="Applied"

def runTerraformCommand(commandToRun, workingDir ):
    isError = "no"
    print("about to proc")
    #Make a work item to re-write this function to throw an error and stop the program whenever an error is encountered.
    proc = subprocess.Popen( commandToRun,cwd=workingDir,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
#    print("procc-ing")
    while True:
      line = proc.stdout.readline()
#      print("about to if line")
      if line:
#        print("there is a line")
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        print(decodedline)
        processDecodedLine(decodedline)
      else:
        break

def runPackerCommand(commandToRun, workingDir, **inputVars):
    proc = subprocess.Popen( commandToRun,cwd=workingDir,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        print(decodedline)
        logWriter.writeLogVerbose(decodedline, **inputVars)
        if "Builds finished. The artifacts of successful builds are" in decodedline:
          global success_packer
          success_packer="true"
        elif "machine readable:" in decodedline:
          if "error-count" in decodedline:
            print("error-count is in decodedline.  ")
            success_packer="false"
      else:
        break

def getPoolQueueIdApiRequest(orgName, projId, qName, azPat):  
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
    print("-------------------------------------------------------------")
    print("queues_url is: ", queues_url)
    #Make the request    
    r = requests.get(queues_url, headers=headers)
    print("r.status_code is: ", r.status_code)
    #Add some better error handling here to handle various response codes.  We are assuming that a 200 response is received in order to continue here.  
    if r.status_code != 200:
      quit("ERROR: getPoolQueueIdApiRequest() returned a non-200 response code.  Halting program so you can debug.")
    myQueuesData = r.json()
    print("myQueuesData is: ", myQueuesData)
    #Using index 0 here because queue_name should be a unique key that brings only one result in this response
    poolQueueId = myQueuesData['value'][0]['id']
    return poolQueueId

def createAzdoServiceEndpointApiRequest(data, azdo_organization_name, azPAT):
    personal_access_token = ":"+azPAT
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
    api_version = "6.0-preview.4"
    url = ("https://dev.azure.com/%s/_apis/serviceendpoint/endpoints?api-version=%s" % (azdo_organization_name, api_version)) 

    r = requests.post(url, data=json.dumps(data), headers=headers)
    respCode = r.status_code
    print("r.status_code is: ", respCode)
    print("r.json() is: ", r.json())
    return respCode, r.json()


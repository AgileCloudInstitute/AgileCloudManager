## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import json
import platform 
import sys

import config_fileprocessor
import controller_terraform
import command_runner
import command_builder
import logWriter
import config_cliprocessor

def onProject(command, systemInstanceName, projName, yamlInfraConfigFileAndPath, keyDir):
  projectResult = 'Failed'
  operation = 'on'
  typeParent = 'systems'
  cloud = config_fileprocessor.getCloudName(yamlInfraConfigFileAndPath)
  if len(cloud) < 2:
    logString = "ERROR: cloud name not valid.  Add better validation checking to the code. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  if cloud == 'azure':
    mycloud = 'ok'
  else:
    logString = "Project management tools other than Azure Devops are planned for future releases.  Until then, cloud must be set to azure for projectManagement block items.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  app_parent_path = config_cliprocessor.inputVars.get('app_parent_path')
  codeResult = 'Failed'
  controller_terraform.terraformCrudOperation(operation, systemInstanceName, keyDir, yamlInfraConfigFileAndPath, typeParent, 'projects', None, None, projName)
  if command_runner.terraformResult == "Applied": 
    logString = "Project creation operation succeeded.  Now inside Python conditional block to do only after the on operation has succeeded. "
    logWriter.writeLogVerbose("acm", logString)
    logString = "-----------------------------------------------------------------------------"
    logWriter.writeLogVerbose("acm", logString)
    projectResult = "Success"
    logString = "done with " + projName + " project.  But now going to add any code repos and builds specified for this project. ----------------------------------------"
    logWriter.writeLogVerbose("acm", logString)
    yaml_keys_file_and_path = command_builder.getKeyFileAndPath(keyDir, typeParent, cloud)
    organization = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgServiceURL')
    subscriptionId = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'subscriptionId')
    clientId = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
    clientSecret = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret') 
    tenantId = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
    #### #The following command gets the client logged in and able to operate on azure repositories.
    loginCmd = "az login --service-principal -u " + clientId + " --tenant " + tenantId + " -p \"" + clientSecret + "\""
    command_runner.runShellCommand(loginCmd)
    pid = command_runner.azuredevops_project_id
    pid = pid.replace('"', '')
    if len(pid) > 2:
      azPat = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgPAT')
      azdoLoginCmd= "ECHO " + azPat + " | " + "az devops login --organization "+organization + " --debug "
      command_runner.runShellCommand(azdoLoginCmd)
      gitUsername = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'gitUsername')
      gitPass = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'gitPass')
    else: 
      logString = "Unable to read a valid project id.  Halting program so you can identify the source of the problem before proceeding. "
      logWriter.writeLogVerbose("acm", logString)
    codeInstanceNames = config_fileprocessor.getCodeInstanceNames(yamlInfraConfigFileAndPath, projName)
    for codeInstance in codeInstanceNames:
      serviceEndPointName = '_' + codeInstance
      gitSourceUrl = config_fileprocessor.getThirdLevelProperty(yamlInfraConfigFileAndPath, typeParent, 'projects', projName, 'code', codeInstance, "sourceRepo")
      endpointTemplate = app_parent_path + config_fileprocessor.getThirdLevelProperty(yamlInfraConfigFileAndPath, typeParent, 'projects', projName, 'code', codeInstance, 'endpointTemplate')
      if platform.system() == "Windows":
        endpointTemplate = endpointTemplate.replace('/','\\')
      else:
        endpointTemplate.replace('\\','/')
      with open(endpointTemplate, 'r') as f:
        template = json.load(f)
      template['name'] = serviceEndPointName
      template['url'] = gitSourceUrl
      template['authorization']['parameters']['username'] = gitUsername
      template['authorization']['parameters']['password'] = gitPass
      template['serviceEndpointProjectReferences'][0]['projectReference']['id'] = pid
      template['serviceEndpointProjectReferences'][0]['projectReference']['name'] = projName
      template['serviceEndpointProjectReferences'][0]['name'] = serviceEndPointName
      orgName = organization.rsplit('/')[3]
      rcode, rJson = command_runner.createAzdoServiceEndpointApiRequest(template, orgName, azPat)
      ##Add handling for the next line based on the value of rcode
      endPtId = rJson['id']
      codeResult = 'Success'
  else:
    projectResult = 'Failed'
    logString = "Terraform project operation failed.  Quitting program here so you can debug the source of the problem.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)

def offProject(systemInstanceName, projName, infraConfigFileAndPath, keyDir):
  result = 'Failed'
  operation = 'off'
  typeParent = 'systems'
  cloud = config_fileprocessor.getCloudName(infraConfigFileAndPath)
  if len(cloud) < 2:
    logString = "ERROR: cloud name not valid.  Add better validation checking to the code. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  if cloud == 'azure':
    mycloud = 'ok'
  else:
    logString = "Project management tools other than Azure Devops are planned for future releases.  Until then, cloud must be set to azure for projectManagement block items.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
#  for projName in projectInstanceNames:
  controller_terraform.terraformCrudOperation(operation, systemInstanceName, keyDir, infraConfigFileAndPath, typeParent, 'projects', None, None, projName)
#  quit("ho hos!")
  if command_runner.terraformResult == "Destroyed": 
    result = "Success"
  else:
    result = 'Failed'
    logString = "Terraform operation failed.  Quitting program here so you can debug the source of the problem.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  logString = "Done with " + projName + " project. ----------------------------------------"
  logWriter.writeLogVerbose("acm", logString)
  if result == 'Success':
    logString = "off operation succeeded.  Now inside Python conditional block to do only after the off operation has succeeded. "
    logWriter.writeLogVerbose("acm", logString)
  else:
    logString = "Error: off operation failed.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)

def importCodeIntoRepo(keyDir, typeName, instanceName, yaml_infra_config_file_and_path, cloud):
  logString = "Inside the function that imports code into repo.  "
  logWriter.writeLogVerbose("acm", logString)
  try:
    codeResult = "Success"
    yaml_keys_file_and_path = command_builder.getKeyFileAndPath(keyDir, typeName, cloud)
    azPat = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgPAT')
    azPat = azPat.replace('"','')
    azPat = azPat.replace("'","")
    gitUsername = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'gitUsername')
    gitUsername = gitUsername.replace('"','')
    gitUsername = gitUsername.replace("'","")
    gitPass = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'gitPass')
    gitPass = gitPass.replace('"','')
    gitPass = gitPass.replace("'","")
    pid = command_runner.azuredevops_project_id
    pid = pid.replace('"', '')
    repoName = config_fileprocessor.getSecondLevelProperty(yaml_infra_config_file_and_path, 'systems', 'projects', instanceName, 'repoName')
    gitSourceUrl = config_fileprocessor.getSecondLevelProperty(yaml_infra_config_file_and_path, 'systems', 'projects', instanceName, 'sourceRepo')
    organization = config_fileprocessor.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgServiceURL')
    organization = organization.replace('"','')
    organization = organization.replace("'","")
    serviceEndPointName = '_' + instanceName
    app_parent_path = config_cliprocessor.inputVars.get('app_parent_path')
    endpointTemplate = app_parent_path + config_fileprocessor.getSecondLevelProperty(yaml_infra_config_file_and_path, 'systems', 'projects', instanceName, 'endpointTemplate')
    if platform.system() == "Windows":
      endpointTemplate = endpointTemplate.replace('/','\\')
    else:
      endpointTemplate.replace('\\','/')
  except Exception as e:
    logString = "ERROR: The following exception was thrown while trying to assemble the variables that go into the endpoint template:  "
    logWriter.writeLogVerbose("acm", logString)
    logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
    logWriter.writeLogVerbose("acm", logString)
    exit(1)
  print("yaml_keys_file_and_path is: ", yaml_keys_file_and_path)
  print("azPat is: ", azPat)
  print("gitUsername is: ", gitUsername)
  print("gitPass is: ", gitPass)
  print("pid is: ", pid)
  print("repoName is: ", repoName)
  print("gitSourceUrl is: ", gitSourceUrl)
  print("organization is: ", organization)
  print("serviceEndPointName is: ", serviceEndPointName)
  print("app_parent_path is: ", app_parent_path)
  print("endpointTemplate is: ", endpointTemplate)
  logString = "About to load the endpoint template from:  " + endpointTemplate
  logWriter.writeLogVerbose("acm", logString)
  with open(endpointTemplate, 'r') as f:
    template = json.load(f)
  template['name'] = serviceEndPointName
  template['url'] = gitSourceUrl
  template['authorization']['parameters']['username'] = gitUsername
  template['authorization']['parameters']['password'] = gitPass
  template['serviceEndpointProjectReferences'][0]['projectReference']['id'] = pid
  template['serviceEndpointProjectReferences'][0]['projectReference']['name'] = instanceName
  template['serviceEndpointProjectReferences'][0]['name'] = serviceEndPointName
  print("organization is: ", organization)
#  quit("BREAKPOINT to debug project management. ")
  orgName = organization.rsplit('/')[3]
  orgName = orgName.replace('"','')
  orgName = orgName.replace("'","")
  logString = "About to create service endpoint API request.  "
  logWriter.writeLogVerbose("acm", logString)
  try:
    rcode, rJson = command_runner.createAzdoServiceEndpointApiRequest(template, orgName, azPat)
  except Exception as e:
    logString = "ERROR: The following exception was thrown while running command_runner.createAzdoServiceEndpointApiRequest():  "
    logWriter.writeLogVerbose("acm", logString)
    logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
    logWriter.writeLogVerbose("acm", logString)
    exit(1)
  logString = "rcode is: "
  logWriter.writeLogVerbose("acm", logString)
  logString = str(rcode)
  logWriter.writeLogVerbose("acm", logString)
  rcode = int(rcode)
  if rcode != 200:
    logString = "rJson is: " + str(rJson)
    logWriter.writeLogVerbose("acm", logString)
    logString = "ERROR: UNABLE TO CREATE SERVICE ENDPOINT.  THIS IS PROBABLY BECAUSE YOU ARE RUNNING THIS ON OPERATION TWICE WITHOUT RUNNING OFF TO DELETE FIRST.  The error codes received back from the API are as follows:  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  else:
    ##Add handling for the next line based on the value of rcode
    endPtId = rJson['id']
    logString = "Just created service principal. "
    logWriter.writeLogVerbose("acm", logString)
    try:
      azdoLoginCmd= "ECHO " + azPat + " | " + "az devops login --organization "+organization + " --debug "
      command_runner.runShellCommand(azdoLoginCmd)
    except Exception as e:
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      logWriter.writeLogVerbose("acm", logString)
      exit(1)
    logString = "-------------------------------------------------------------------"
    logWriter.writeLogVerbose("acm", logString)
    logWriter.writeLogVerbose("acm", logString)
    logString = "Just logged in to azdo. "
    logWriter.writeLogVerbose("acm", logString)
    logString = "-------------------------------------------------------------------"
    logWriter.writeLogVerbose("acm", logString)
    logWriter.writeLogVerbose("acm", logString)
    if len(endPtId) > 2:  
      myCmd = "az repos import create --git-source-url " + gitSourceUrl + " --repository " + repoName + " --git-service-endpoint-id  " + endPtId + " --organization " + organization + " --project " + instanceName + " --requires-authorization "
    else:
      myCmd = "az repos import create --git-source-url " + gitSourceUrl + " --repository " + repoName + " --organization " + organization + " --project " + instanceName
    try:
      myResponse = command_runner.getShellJsonResponse(myCmd)
      jsonOutput = json.loads(myResponse)
      allSteps = jsonOutput['detailedStatus']['allSteps']
      currentStep = jsonOutput['detailedStatus']['currentStep']
      if len(allSteps) == currentStep:
        status = jsonOutput['status']
        if status == 'completed':
          azdoLogoutCmd= "ECHO " + azPat + " | " + "az devops logout --organization "+organization 
          command_runner.runShellCommand(azdoLogoutCmd)
        else:
          logString = "Halting program because repository was not imported successfully.  Please review your logs to identify what happened so that this can be re-run successfully.  "
          logWriter.writeLogVerbose("acm", logString)
          sys.exit(1)
    except Exception as e:
      logString = "WARNING: Failed to import repository.  Continuing gracefully in case you already imported this repository and are simply re-running this module.  But please check to confirm that the repository has been imported previously.  "
      logWriter.writeLogVerbose("acm", logString)
      logString = "-----  ERROR message is: -----"
      logWriter.writeLogVerbose("acm", logString)
      logString = str(e)
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)

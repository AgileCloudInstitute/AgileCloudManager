## Copyright 2024 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

import json
import platform 
import sys
  
from config_fileprocessor import config_fileprocessor  
from command_runner import command_runner  
from command_formatter import command_formatter  
from log_writer import log_writer  
  
class controller_azdoproject:  
  
  def __init__(self):    
    pass  
 
  #@public  
  def onProject(self, serviceType, systemConfig, instance):  
    import config_cliprocessor  
    fproc = config_fileprocessor()  
    cmd_fmrtr = command_formatter()  
    lw = log_writer()  
    crnr = command_runner()
    from controller_terraform import controller_terraform
    ctf = controller_terraform()
    keyDir = fproc.getKeyDir(systemConfig)
    operation = 'on'
    typeParent = 'systems'
    cloud = systemConfig.get("cloud")
    if len(cloud) < 2:
      logString = "ERROR: cloud name not valid.  Add better validation checking to the code. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    if cloud != 'azure':
      logString = "Project management tools other than Azure Devops are planned for future releases.  Until then, cloud must be set to azure for projectManagement block items.  "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    projName = instance.get("instanceName")
    repoName = instance.get("repoName")
    ctf.terraformCrudOperation(operation, keyDir, systemConfig, instance, typeParent, serviceType, None, projName)
    if ctf.terraformResult == "Applied": 
      logString = "Project creation operation succeeded.  Now inside Python conditional block to do only after the on operation has succeeded. "
      lw.writeLogVerbose("acm", logString)
      logString = "-----------------------------------------------------------------------------"
      lw.writeLogVerbose("acm", logString)
      logString = "done with " + projName + " project.  But now going to add any code repos and builds specified for this project. ----------------------------------------"
      lw.writeLogVerbose("acm", logString)
      yaml_keys_file_and_path = cmd_fmrtr.getKeyFileAndPath(keyDir)
      organization = fproc.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgServiceURL')
      clientId = fproc.getFirstLevelValue(yaml_keys_file_and_path, 'clientId')
      clientSecret = fproc.getFirstLevelValue(yaml_keys_file_and_path, 'clientSecret') 
      tenantId = fproc.getFirstLevelValue(yaml_keys_file_and_path, 'tenantId')
      #### #The following command gets the client logged in and able to operate on azure repositories.
      loginCmd = "az login --service-principal -u " + clientId + " --tenant " + tenantId + " -p \"" + clientSecret + "\""
      crnr.runShellCommand(loginCmd)
      if 'azuredevops_project_id' in ctf.tfOutputDict.keys():
        pid = ctf.tfOutputDict['azuredevops_project_id']
        pid = pid.replace('"', '')
      else:
        logString = "ERROR: The terraform module that creates the Azure Devops Project must have an output variable named azuredevops_project_id which contains a valid id for the project that the module defines.  Since the module you are using does not have a azuredevops_project_id output variable, the program is halting so you can fix the problem and rerun the command that got you here.  "
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
      if len(pid) > 2:
        azPat = fproc.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgPAT')
        azdoLoginCmd= "ECHO " + azPat + " | " + "az devops login --organization "+organization + " --debug "
        crnr.runShellCommand(azdoLoginCmd)
        gitUsername = fproc.getFirstLevelValue(yaml_keys_file_and_path, 'gitUsername')
        gitPass = fproc.getFirstLevelValue(yaml_keys_file_and_path, 'gitPass')
      else: 
        logString = "Unable to read a valid project id.  Halting program so you can identify the source of the problem before proceeding. "
        lw.writeLogVerbose("acm", logString)
      serviceEndPointName = '_' + repoName
      gitSourceUrl = instance.get("sourceRepo")
      endpointTemplate = userCallingDir + cmd_fmrtr.getSlashForOS() +instance.get('endpointTemplate')
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
      rcode, rJson = crnr.createAzdoServiceEndpointApiRequest(template, orgName, azPat)
      ##Add handling for the next line based on the value of rcode
      endPtId = rJson['id']
    else:
      logString = "Terraform project operation failed.  Quitting program here so you can debug the source of the problem.  "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)

  #@public
  def offProject(self, serviceType, systemConfig, instance):
    cfproc = config_fileprocessor()
    lw = log_writer()
    from controller_terraform import controller_terraform
    ctrlr_tf = controller_terraform()
    keyDir = cfproc.getKeyDir(systemConfig)
    projName = instance.get("instanceName")
    result = 'Failed'
    operation = 'off'
    typeParent = 'systems'
    cloud = systemConfig.get("cloud")
    if len(cloud) < 2:
      logString = "ERROR: cloud name not valid.  Add better validation checking to the code. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    if cloud != 'azure':
      logString = "Project management tools other than Azure Devops are planned for future releases.  Until then, cloud must be set to azure for projectManagement block items.  "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    ctrlr_tf.terraformCrudOperation(operation, keyDir, systemConfig, instance, typeParent, serviceType, None, projName)
    if ctrlr_tf.terraformResult == "Destroyed": 
      result = "Success"
    else:
      result = 'Failed'
      logString = "Terraform operation failed.  Quitting program here so you can debug the source of the problem.  "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    logString = "Done with " + projName + " project. ----------------------------------------"
    lw.writeLogVerbose("acm", logString)
    if result == 'Success':
      logString = "off operation succeeded.  Now inside Python conditional block to do only after the off operation has succeeded. "
      lw.writeLogVerbose("acm", logString)
    else:
      logString = "Error: off operation failed.  "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)

  #@public
  def importCodeIntoRepo(self, keyDir, instance, tf_ctrlr):
    import config_cliprocessor
    cfgfproc = config_fileprocessor()
    cmd_fmrtr = command_formatter()
    cmd_rnr = command_runner()
    lw = log_writer()
    logString = "Inside the function that imports code into repo.  "
    lw.writeLogVerbose("acm", logString)
    instanceName = instance.get("instanceName")
    try:
      yaml_keys_file_and_path = cmd_fmrtr.getKeyFileAndPath(keyDir)
      azPat = cfgfproc.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgPAT')
      azPat = azPat.replace('"','')
      azPat = azPat.replace("'","")
      gitUsername = cfgfproc.getFirstLevelValue(yaml_keys_file_and_path, 'gitUsername')
      gitUsername = gitUsername.replace('"','')
      gitUsername = gitUsername.replace("'","")
      gitPass = cfgfproc.getFirstLevelValue(yaml_keys_file_and_path, 'gitPass')
      gitPass = gitPass.replace('"','')
      gitPass = gitPass.replace("'","")
      if 'azuredevops_project_id' in tf_ctrlr.tfOutputDict.keys():
        pid = tf_ctrlr.tfOutputDict['azuredevops_project_id']
        pid = pid.replace('"', '')
      else:
        logString = "ERROR: The terraform module that creates the Azure Devops Project must have an output variable named azuredevops_project_id which contains a valid id for the project that the module defines.  Since the module you are using does not have a azuredevops_project_id output variable, the program is halting so you can fix the problem and rerun the command that got you here.  "
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
      repoName = instance.get("repoName")
      gitSourceUrl = instance.get('sourceRepo')
      organization = cfgfproc.getFirstLevelValue(yaml_keys_file_and_path, 'azdoOrgServiceURL')
      organization = organization.replace('"','')
      organization = organization.replace("'","")
      serviceEndPointName = '_' + instanceName
      userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
      endpointTemplate = userCallingDir + cmd_fmrtr.getSlashForOS() + instance.get('endpointTemplate')
      if platform.system() == "Windows":
        endpointTemplate = endpointTemplate.replace('/','\\')
      else:
        endpointTemplate.replace('\\','/')
    except Exception as e:
      logString = "ERROR: The following exception was thrown while trying to assemble the variables that go into the endpoint template:  "
      lw.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      lw.writeLogVerbose("acm", logString)
      exit(1)
    if (len(serviceEndPointName) < 2) or (not serviceEndPointName):
      logString = "ERROR: Invalid value for serviceEndPointName is as follows: "+serviceEndPointName
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    if (len(gitSourceUrl) < 2) or (not gitSourceUrl):
      logString = "ERROR: Invalid value for gitSourceUrl is as follows: "+gitSourceUrl
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    if (len(gitUsername) < 2) or (not gitUsername):
      logString = "ERROR: Invalid value for gitUsername is as follows: "+gitUsername
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    if (len(gitPass) < 2) or (not gitPass):
      logString = "ERROR: Invalid value for git password or PAT stored in gitPass variable. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    if (len(str(pid)) < 2) or (not str(pid)):
      logString = "ERROR: Invalid value for pid is as follows: "+str(pid)
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    if (len(instanceName) < 2) or (not instanceName):
      logString = "ERROR: Invalid value for instanceName is as follows: "+instanceName
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    if (len(organization) < 2) or (not organization):
      logString = "ERROR: Invalid value for organization is as follows: "+organization
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    logString = "About to load the endpoint template from:  " + endpointTemplate
    lw.writeLogVerbose("acm", logString)
    with open(endpointTemplate, 'r') as f:
      template = json.load(f)
    template['name'] = serviceEndPointName
    template['url'] = gitSourceUrl
    template['authorization']['parameters']['username'] = gitUsername
    template['authorization']['parameters']['password'] = gitPass
    template['serviceEndpointProjectReferences'][0]['projectReference']['id'] = pid
    template['serviceEndpointProjectReferences'][0]['projectReference']['name'] = instanceName
    template['serviceEndpointProjectReferences'][0]['name'] = serviceEndPointName
    orgName = organization.rsplit('/')[3]
    orgName = orgName.replace('"','')
    orgName = orgName.replace("'","")
    logString = "About to create service endpoint API request.  "
    lw.writeLogVerbose("acm", logString)
    try:
      rcode, rJson = cmd_rnr.createAzdoServiceEndpointApiRequest(template, orgName, azPat)
    except Exception as e:
      logString = "ERROR: The following exception was thrown while running command_runner.createAzdoServiceEndpointApiRequest():  "
      lw.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      lw.writeLogVerbose("acm", logString)
      exit(1)
    logString = "rcode is: "
    lw.writeLogVerbose("acm", logString)
    logString = str(rcode)
    lw.writeLogVerbose("acm", logString)
    rcode = int(rcode)
    if rcode != 200:
      logString = "rJson is: " + str(rJson)
      lw.writeLogVerbose("acm", logString)
      logString = "ERROR: UNABLE TO CREATE SERVICE ENDPOINT.  THIS IS PROBABLY BECAUSE YOU ARE RUNNING THIS ON OPERATION TWICE WITHOUT RUNNING OFF TO DELETE FIRST.  The error codes received back from the API are as follows:  "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    else:
      ##Add handling for the next line based on the value of rcode
      endPtId = rJson['id']
      logString = "Just created service principal with id: "+str(endPtId)
      lw.writeLogVerbose("acm", logString)
      try:
        azdoLoginCmd= "ECHO " + azPat + " | " + "az devops login --organization "+organization + " --debug "
        cmd_rnr.runShellCommand(azdoLoginCmd)
      except Exception as e:
        logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
        lw.writeLogVerbose("acm", logString)
        exit(1)
      logString = "-------------------------------------------------------------------"
      lw.writeLogVerbose("acm", logString)
      lw.writeLogVerbose("acm", logString)
      logString = "Just logged in to azdo. "
      lw.writeLogVerbose("acm", logString)
      logString = "-------------------------------------------------------------------"
      lw.writeLogVerbose("acm", logString)
      lw.writeLogVerbose("acm", logString)
      if len(endPtId) > 2:  
        myCmd = "az repos import create --git-source-url " + gitSourceUrl + " --repository " + repoName + " --git-service-endpoint-id  " + endPtId + " --organization " + organization + " --project " + instanceName + " --requires-authorization "
        logString = "myCmd is: az repos import create --git-source-url " + gitSourceUrl + " --repository " + repoName + " --git-service-endpoint-id  *** --organization *** --project *** --requires-authorization "
        lw.writeLogVerbose("shell", logString)
      else:
        myCmd = "az repos import create --git-source-url " + gitSourceUrl + " --repository " + repoName + " --organization " + organization + " --project " + instanceName
        logString = "myCmd is: az repos import create --git-source-url " + gitSourceUrl + " --repository " + repoName + " --organization *** --project ***"
        lw.writeLogVerbose("shell", logString)
      try:
        myResponse = cmd_rnr.getShellJsonResponse(myCmd)
        jsonOutput = json.loads(myResponse)
        allSteps = jsonOutput['detailedStatus']['allSteps']
        currentStep = jsonOutput['detailedStatus']['currentStep']
        if len(allSteps) == currentStep:
          status = jsonOutput['status']
          if status == 'completed':
            azdoLogoutCmd= "ECHO " + azPat + " | " + "az devops logout --organization "+organization 
            cmd_rnr.runShellCommand(azdoLogoutCmd)
          else:
            logString = "Halting program because repository was not imported successfully.  Please review your logs to identify what happened so that this can be re-run successfully.  "
            lw.writeLogVerbose("acm", logString)
            sys.exit(1)
      except Exception as e:
        logString = "WARNING: Failed to import repository.  Continuing gracefully in case you already imported this repository and are simply re-running this module.  But please check to confirm that the repository has been imported previously.  "
        lw.writeLogVerbose("acm", logString)
        logString = "-----  ERROR message is: -----"
        lw.writeLogVerbose("acm", logString)
        logString = str(e)
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)

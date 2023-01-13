## Copyright 2023 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

from command_formatter import command_formatter
from command_runner import command_runner
from config_keysassembler import config_keysassembler
from log_writer import log_writer

import platform
import pathlib
import shutil
import json

class controller_azureadmin:
  
  def __init__(self):  
    pass
 
  #@public
  def cleanUp(self, operation, systemConfig, instance, typeName, instanceName, destinationCallInstance, myTfCtrlr):
    import config_cliprocessor
    crun = command_runner()
    myKeysAssmblr = config_keysassembler()
    myCmdFrmtr = command_formatter()
    myLogWriter = log_writer()
    if operation == "on":
      if myTfCtrlr.terraformResult == "Applied":
        dest_keys_file_and_path = myCmdFrmtr.getKeyFileLocation(instanceName)
        ### Save the newly-generated keys
        secKey = 'empty'
        sp_id = 'empty'
        sp_objid = 'empty'
        sp_appid = 'empty'
        app_id = 'empty'
        #Make work item to set localBackend programmatically.  Here we are developing the remote backend feature, so we are setting this here for now.
        localBackend = False
        if localBackend:
          tfStateFile = destinationCallInstance + 'terraform.tfstate'
          data = json.load(open(tfStateFile, 'r'))
          data_resources = data["resources"]
          for i in data_resources:
            if i["type"] == 'azuread_service_principal_password': 
              secKey = i['instances'][0]['attributes']['value']
              #Check to ensure that the following line populates sp_id correctly for local backend.  Here we are adding the following line while developing the remote backend.
              sp_id = i['instances'][0]['attributes']['service_principal_id']
            if i["type"] == 'azuread_service_principal':
              #Check to make sure the following 2 lines populate correctly for local backend.  Here these are being added while developing remote backend.
              sp_appid = i['instances'][0]['attributes']['application_id']
              sp_objid = i['instances'][0]['attributes']['object_id']
        else:
          binariesPath = config_cliprocessor.inputVars.get('dependenciesBinariesPath') 
          myCommand = binariesPath + "terraform show --json"
          returnedData = crun.getShellJsonData(myCommand, destinationCallInstance)
          returnedData = json.loads(returnedData)
          data_resources = returnedData["values"]["root_module"]["child_modules"][0]["resources"]
          passCount = 0
          for i in data_resources:
            if i["type"] == 'azuread_service_principal_password':
              secKey = i['values']['value']
              sp_id = i['values']['service_principal_id']
              passCount += 1
            if i["type"] == 'azuread_service_principal':
              sp_appid = i['values']['application_id']
              sp_objid = i['values']['object_id']
          if passCount > 1:
            logString = "Error: too many instances of azuread_service_principal_password.  We currently support one instance per module.  If you need support for more, submit a feature request. "
            myLogWriter.writeLogVerbose("acm", logString)
            exit(1)
        if (sp_id == sp_objid) and (sp_id != "empty"):
          app_id = sp_appid
        myKeysAssmblr.writeTheVarsFile(systemConfig, instance, typeName, app_id, secKey)
    elif operation == "off":
      if myTfCtrlr.terraformResult == "Destroyed":
        dest_keys_file_and_path = myCmdFrmtr.getKeyFileLocation(instanceName)
        if platform.system() == "Windows":
          splitString = '\\'
        elif platform.system() == "Linux":
          splitString = '/'
        else:
          logString = "ERROR: Operating system must be either Windows or Linux"
          myLogWriter.writeLogVerbose("acm", logString)
          exit(1)
        filePathParts = dest_keys_file_and_path.split(splitString)
        keyFileName = filePathParts[-1]
        pathOnly = dest_keys_file_and_path.replace(keyFileName, '')
        path = pathlib.Path(pathOnly)
        shutil.rmtree(path)

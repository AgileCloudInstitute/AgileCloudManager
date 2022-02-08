import subprocess
import re
import json
import os

import command_runner


myCommand = "C:\\projects\\acm\\Nov2021\\config-outside-acm-path\\dependencies\\binaries\\terraform show --json"
myDir = "C:\\projects\\acm\\Nov2021\\azure-building-blocks\\terraform\\calls-to-modules\\instances\\ad-admin\\admin-pipelineAgents-ad-admin\\"


returnedData = command_runner.getShellJsonData(myCommand, myDir)
returnedData = json.loads(returnedData)

data_resources = returnedData["values"]["root_module"]["child_modules"][0]["resources"]
for i in data_resources:
  if i["type"] == 'azuread_service_principal_password':
    secKey = i['values']['value']
    print("secKey is: ", secKey)

#C:\projects\acm\Nov2021\agile-cloud-manager\controller>python readTfvars.py


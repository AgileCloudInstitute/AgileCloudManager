print("Inside installReleaseDefinition.py script.")  
  
import sys  
import requests
import os
import base64
import json
import deploymentFunctions as depfunc  

initCommand='terraform init'
pathToProjectRepoBuildCalls = "/home/aci-user/cloned-repos/agile-cloud-manager/calls-to-modules/azure-pipelines-project-repo-build-resources/"
outputProjectRepoBuildCommand='terraform output '

##############################################################################################
### Step One: Get The Output Variables From the azure-pipelines-project-repo-build module
##############################################################################################

depfunc.runTerraformCommand(initCommand, pathToProjectRepoBuildCalls)
depfunc.runTerraformCommand(outputProjectRepoBuildCommand, pathToProjectRepoBuildCalls)

print("Back in installReleaseDefMinimal.py .")
print("depfunc.azuredevops_project_id is: ", depfunc.azuredevops_project_id )
print("depfunc.azuredevops_organization_name is: ", depfunc.azuredevops_organization_name)

#########################################################################################################
### Step Two: Get The poolQueueId from the agent pool Queue that will be used by the release definition.
################################################################################templateFile, azdo_organization_name, azdo_project_id, releaseDefName, releaseDefDescription#########################
def createReleaseDefinitionApiRequest(templateFile, azdo_organization_name, azdo_project_id, releaseDefName, releaseDefDescription):
    personal_access_token = ":"+os.environ["AZ_PAT"]
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
    api_version = "5.1"
    url = ("https://vsrm.dev.azure.com/%s/%s/_apis/release/definitions?api-version=%s" % (azdo_organization_name, azdo_project_id, api_version))
    with open(templateFile, 'r') as json_file:
      print("json_file is: ", json_file)
      data = json.load(json_file)
      print("---------------------------------------------------------")
      print("name is: ", data['name'])
      data['name'] = releaseDefName
      print("name is now: ", data['name'])
      print("description is: ", data['description'])
      data['description'] = releaseDefDescription
      print("description is now: ", data['description'])
      print("---------------------------------------------------------")
      print("url is: ", url)
      print("---------------------------------------------------------")
      print("revised data is: ", data)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    respCode = r.status_code
    print("r.status_code is: ", respCode)
    print("r.json() is: ", r.json())
    return respCode
 
##############################################################################################
### Step Three: Create Release Definition By Making API Call.
##############################################################################################
jsonTemplateFile = 'releaseDefTempMinimal.json'
releaseDefinitionName = 'Name of minimal release Definition'
releaseDefinitionDescription = 'Description of minimal release definition.'
rCode = createReleaseDefinitionApiRequest(jsonTemplateFile, depfunc.azuredevops_organization_name, depfunc.azuredevops_project_id , releaseDefinitionName, releaseDefinitionDescription)

print("response code from create release definition API call is: ", rCode)

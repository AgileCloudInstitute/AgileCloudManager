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

print("Back in installServiceConnection.py .")
print("depfunc.azuredevops_project_id is: ", depfunc.azuredevops_project_id )
print("depfunc.azuredevops_project_name is: ", depfunc.azuredevops_project_name)
print("depfunc.azuredevops_organization_service_url is: ", depfunc.azuredevops_organization_service_url)
print("azuredevops_organization_name is: ", depfunc.azuredevops_organization_name)

####Integrate all of the following variables into the preceding output processing from the terraform output.  
###//azuredevops_project_id = ""
###//azuredevops_project_name = ""
###//azuredevops_organization_service_url = ""
###//azuredevops_organization_name = azuredevops_organization_service_url.split("azure.com/",1)[1]
###//azuredevops_organization_name = azuredevops_organization_name.replace("/","")
###//..service_principal_id = ""
###//..service_principal_name = "" 
###//..service_connection_name = ""
###//..tenant_id = "" 
###//..subscription_id = ""
###//..subscription_name = ""

###print("azuredevops_project_id is: ", azuredevops_project_id)
###print("azuredevops_project_name is: ", azuredevops_project_name)
###print("azuredevops_organization_service_url is: ", azuredevops_organization_service_url)
###print("azuredevops_organization_name is: ", azuredevops_organization_name)
###print("service_principal_id is: ", service_principal_id)
###print("service_principal_name is: ", service_principal_name)
###print("service_connection_name is: ", service_connection_name)
###print("tenant_id is: ", tenant_id)
###print("subscription_id is: ", subscription_id)
###print("subscription_name is: ", subscription_name)

##############################################################################################
### Step Two: Create Service Connection By Making API Call.
##############################################################################################
def createServiceConnectionApiRequest(templateFile, azdo_organization_name, azdo_project_name):
    personal_access_token = ":"+os.environ["AZ_PAT"]
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
    api_version = "5.1-preview.2"
    url = ("https://dev.azure.com/%s/%s/_apis/serviceendpoint/endpoints?api-version=%s" % (azdo_organization_name, azdo_project_name, api_version))
    #https://dev.azure.com/{OrgName}/{ProjectName}/_apis/serviceendpoint/endpoints?api-version=5.1-preview.2
    with open(templateFile, 'r') as json_file:
      print("json_file is: ", json_file)
      data = json.load(json_file)
      print("---------------------------------------------------------")
      print("data[authorization][parameters][serviceprincipalid] is: ", data['authorization']['parameters']['serviceprincipalid'])
      print("data[authorization][parameters][serviceprincipalkey] is: ", data['authorization']['parameters']['serviceprincipalkey'])
      print("data[authorization][parameters][tenantid] is: ", data['authorization']['parameters']['tenantid'])
      print("data[description] is: ", data['description'])
      print("data[name] is: ", data['name'])
      print("data[serviceEndpointProjectReferences][0][description] is: ", data['serviceEndpointProjectReferences'][0]['description'])
      print("data[serviceEndpointProjectReferences][0][name] is: ", data['serviceEndpointProjectReferences'][0]['name'])
      print("data[serviceEndpointProjectReferences][0][projectReference][id] is: ", data['serviceEndpointProjectReferences'][0]['projectReference']['id'])
      print("data[serviceEndpointProjectReferences][0][projectReference][name] is: ", data['serviceEndpointProjectReferences'][0]['projectReference']['name'])
      print("---------------------------------------------------------")
      print("url is: ", url)
      print("---------------------------------------------------------")
      #print("revised data is: ", data)
    #r = requests.post(url, data=json.dumps(data), headers=headers)
    #print("r.status_code is: ", r.status_code)
    #print("r.json() is: ", r.json())
    
jsonTemplateFile = 'serviceConnectionTemplate.json'
createServiceConnectionApiRequest(jsonTemplateFile, depfunc.azuredevops_organization_name, depfunc.azuredevops_project_name)


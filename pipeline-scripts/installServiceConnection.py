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
print("depfunc.azuredevops_organization_name is: ", depfunc.azuredevops_organization_name)
print("depfunc.azuredevops_subscription_name is: ", depfunc.azuredevops_subscription_name)
print("depfunc.azuredevops_subscription_id is: ", depfunc.azuredevops_subscription_id)
print("depfunc.azuredevops_client_name is: ", depfunc.azuredevops_client_name)
print("depfunc.azuredevops_service_connection_name is: ", depfunc.azuredevops_service_connection_name)


####Integrate all of the following variables into the preceding output processing from the terraform output.  
service_principal_id = os.environ["AZ_CLIENT"]
service_principal_key = os.environ["AZ_PASS"]
tenant_id = os.environ["AZ_TENANT"]

print("service_principal_id is: ", service_principal_id)
print("service_principal_key is: ", service_principal_key)
print("tenant_id is: ", tenant_id)

   
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
      print("About to reset the variable values.")
      data['authorization']['parameters']['serviceprincipalid'] = service_principal_id
      data['authorization']['parameters']['serviceprincipalkey'] = service_principal_key
      data['authorization']['parameters']['tenantid'] = tenant_id
      data['description'] = "Service Connection Managed by Terraform"
      data['name'] = depfunc.azuredevops_service_connection_name
      data['serviceEndpointProjectReferences'][0]['description'] = "Project reference managed by Terraform."  
      data['serviceEndpointProjectReferences'][0]['name'] = depfunc.azuredevops_service_connection_name
      data['serviceEndpointProjectReferences'][0]['projectReference']['id'] = depfunc.azuredevops_project_id 
      data['serviceEndpointProjectReferences'][0]['projectReference']['name'] = depfunc.azuredevops_project_name

      print("---------------------------------------------------------")
      print("revised data[authorization][parameters][serviceprincipalid] is: ", data['authorization']['parameters']['serviceprincipalid'])
      print("revised data[authorization][parameters][serviceprincipalkey] is: ", data['authorization']['parameters']['serviceprincipalkey'])
      print("revised data[authorization][parameters][tenantid] is: ", data['authorization']['parameters']['tenantid'])
      print("revised data[description] is: ", data['description'])
      print("revised data[name] is: ", data['name'])
      print("revised data[serviceEndpointProjectReferences][0][description] is: ", data['serviceEndpointProjectReferences'][0]['description'])
      print("revised data[serviceEndpointProjectReferences][0][name] is: ", data['serviceEndpointProjectReferences'][0]['name'])
      print("revised data[serviceEndpointProjectReferences][0][projectReference][id] is: ", data['serviceEndpointProjectReferences'][0]['projectReference']['id'])
      print("revised data[serviceEndpointProjectReferences][0][projectReference][name] is: ", data['serviceEndpointProjectReferences'][0]['projectReference']['name'])
      print("---------------------------------------------------------")
      print("url is: ", url)
      print("---------------------------------------------------------")
      print("revised data is: ", data)
    #r = requests.post(url, data=json.dumps(data), headers=headers)
    #print("r.status_code is: ", r.status_code)
    #print("r.json() is: ", r.json())
    
jsonTemplateFile = 'serviceConnectionTemplate.json'
createServiceConnectionApiRequest(jsonTemplateFile, depfunc.azuredevops_organization_name, depfunc.azuredevops_project_name)


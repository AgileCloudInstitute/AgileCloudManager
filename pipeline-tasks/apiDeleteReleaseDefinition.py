import requests
import os
import base64
import json

#Input variables will be received from terraform output, but are defined here as constants during development:
azuredevops_project_id = ""
azuredevops_organization_service_url = ""

azuredevops_organization_name = azuredevops_organization_service_url.split("azure.com/",1)[1]
azuredevops_organization_name = azuredevops_organization_name.replace("/","")

azuredevops_release_definition_id = ""

delete_comment = "Comment goes here. "

print("azuredevops_project_id is: ", azuredevops_project_id)
print("azuredevops_organization_name is: ", azuredevops_organization_name)
print("azuredevops_release_definition_id is: ", azuredevops_release_definition_id)
print("delete_comment is: ", delete_comment)

personal_access_token = ":"+os.environ["AZ_PAT"]
headers = {}
headers['Content-type'] = "application/json"
headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
api_version = "5.1"
#DELETE https://vsrm.dev.azure.com/{organization}/{project}/_apis/release/definitions/{definitionId}?comment={comment}&forceDelete={forceDelete}&api-version=5.1
url = ("https://vsrm.dev.azure.com/%s/%s/_apis/release/definitions/%s?comment=%s&api-version=%s" % (azuredevops_organization_name, azuredevops_project_id, azuredevops_release_definition_id, delete_comment, api_version))

response = requests.delete(url, headers=headers)

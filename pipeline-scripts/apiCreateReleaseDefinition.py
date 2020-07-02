import requests
import os
import base64
import json

#Input variables will be received from terraform output, but are defined here as constants during development:
azuredevops_git_repository_id = ""
azuredevops_git_repository_name = ""
azuredevops_project_id = ""
azuredevops_project_name = ""
azuredevops_build_definition_id = ""
azuredevops_organization_service_url = ""

azuredevops_organization_name = azuredevops_organization_service_url.split("azure.com/",1)[1]
azuredevops_organization_name = azuredevops_organization_name.replace("/","")

print("azuredevops_git_repository_id is: ", azuredevops_git_repository_id)
print("azuredevops_git_repository_name is: ", azuredevops_git_repository_name)
print("azuredevops_project_id is: ", azuredevops_project_id)
print("azuredevops_project_name is: ", azuredevops_project_name)
print("azuredevops_build_definition_id is: ", azuredevops_build_definition_id)
print("azuredevops_organization_service_url is: ", azuredevops_organization_service_url)
print("azuredevops_organization_name is: ", azuredevops_organization_name)

creator_owner_id = ""

personal_access_token = ":"+os.environ["AZ_PAT"]
headers = {}
headers['Content-type'] = "application/json"
headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
api_version = "5.1"
url = ("https://vsrm.dev.azure.com/%s/%s/_apis/release/definitions?api-version=%s" % (azuredevops_organization_name, azuredevops_project_id, api_version))


with open('releaseDefinitionTemplate.json', 'r') as json_file:
  data = json.load(json_file)
  print("---------------------------------------------------------")
  print("name is: ", data['name'])
  data['name'] = 'Create AWS Simple Example'
  print("name is now: ", data['name'])
  print("---------------------------------------------------------")
  print("[\'artifacts\'][\'sourceId\'] is: ", data['artifacts'][0]['sourceId'])
  print("[\'artifacts\'][\'artifactSourceDefinitionUrl\'][\'id\'] is: ", data['artifacts'][0]['artifactSourceDefinitionUrl']['id'])
  print("[\'artifacts\'][\'alias\'] is: ", data['artifacts'][0]['alias'])
  print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['definition']['id'])
  print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['definition']['name'])
  print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['project']['id'])
  print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['project']['name'])
  print("---------------------------------------------------------")
  data['artifacts'][0]['sourceId'] = azuredevops_project_id + ":1"
  data['artifacts'][0]['artifactSourceDefinitionUrl']['id'] = azuredevops_organization_service_url + azuredevops_project_name + "/_build?definitionId=" + str(azuredevops_build_definition_id)
  data['artifacts'][0]['alias'] = "_" + azuredevops_git_repository_name
  data['artifacts'][0]['definitionReference']['definition']['id'] = azuredevops_build_definition_id
  data['artifacts'][0]['definitionReference']['definition']['name'] = azuredevops_git_repository_name
  data['artifacts'][0]['definitionReference']['project']['id'] = azuredevops_project_id
  data['artifacts'][0]['definitionReference']['project']['name'] = azuredevops_project_name
  print("---------------------------------------------------------")
  print("[\'artifacts\'][\'sourceId\'] is: ", data['artifacts'][0]['sourceId'])
  print("[\'artifacts\'][\'artifactSourceDefinitionUrl\'][\'id\'] is: ", data['artifacts'][0]['artifactSourceDefinitionUrl']['id'])
  print("[\'artifacts\'][\'alias\'] is: ", data['artifacts'][0]['alias'])
  print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['definition']['id'])
  print("[\'artifacts\'][\'definitionReference\'][\'definition\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['definition']['name'])
  print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'id\'] is: ", data['artifacts'][0]['definitionReference']['project']['id'])
  print("[\'artifacts\'][\'definitionReference\'][\'project\'][\'name\'] is: ", data['artifacts'][0]['definitionReference']['project']['name'])
  print("---------------------------------------------------------")
  print("url is: ", url)
  r = requests.post(url, data=json.dumps(data), headers=headers)

  print("r.status_code is: ", r.status_code)
  print("r.json() is: ", r.json())

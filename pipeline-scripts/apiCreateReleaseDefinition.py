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

data = {
  "source": "undefined",
  "revision": 1,
  "description": "null",
  "createdBy":{ "id": $creator_owner_id,},
  "createdOn": "0001-01-01T00:00:00",
  "modifiedBy": "null",
  "modifiedOn": "0001-01-01T00:00:00",
  "isDeleted": "false",
  "variables": {},
  "variableGroups": [],
  "environments": [
    {
      "id": 1,
      "name": "PROD",
	  "owner":{"id": $creator_owner_id,},
      "preDeployApprovals": {
        "approvals": [
          {
            "rank": 1,
            "isAutomated": "true",
            "isNotificationOn": "false",
            "id": 0
          }
        ]
      },
      "postDeployApprovals": {
        "approvals": [
          {
            "rank": 1,
            "isAutomated": "true",
            "isNotificationOn": "false",
            "id": 0
          }
        ]
      },
      "deployPhases": [
        {
          "deploymentInput": {
            "parallelExecution": {
              "parallelExecutionType": "none"
            },
            "skipArtifactsDownload": "false",
            "artifactsDownloadInput": {},
            "queueId": 1,
            "demands": [],
            "enableAccessToken": "false",
            "timeoutInMinutes": 0,
            "jobCancelTimeoutInMinutes": 1,
            "condition": "succeeded()",
            "overrideInputs": {}
          },
          "rank": 1,
          "phaseType": "agentBasedDeployment",
          "name": "Run on agent",
          "workflowTasks": []
        }
      ],
      "retentionPolicy": {
        "daysToKeep": 30,
        "releasesToKeep": 3,
        "retainBuild": "true"
      },
    }
  ],
  "artifacts": [],
  "triggers": [],
  "releaseNameFormat": "null",
  "tags": [],
  "properties": {},
  "id": 0,
  "name": "Fabrikam-web",
  "projectReference": "null",
  "_links": {}
}    
  
r = requests.post(url, data=json.dumps(data), headers=headers)

print("r.status_code is: ", r.status_code)
print("r.json() is: ", r.json())

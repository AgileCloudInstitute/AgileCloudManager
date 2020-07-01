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

  
def getApiRequest(url):  
    personal_access_token = ":"+os.environ["AZ_PAT"]
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
    r = requests.get(url, headers=headers)  
    print("r.status_code is: ", r.status_code)
    print("r.json() is: ", r.json())
  
  
#Set variables to be shared across API calls.  These will be imported from terraform output variables.  
api_version = "5.1"

#Get a list of agent pools.
agentpools_url = ("https://dev.azure.com/%s/_apis/distributedtask/pools?api-version=%s" % (azuredevops_organization_name, api_version))
print("-------------------------------------------------------------")
print("---- About to get list of Agent Pools ----")  
getApiRequest(agentpools_url)  
  
#Get a list of build definitions
#GET https://dev.azure.com/{organization}/{project}/_apis/build/definitions?name={name}&repositoryId={repositoryId}&repositoryType={repositoryType}&queryOrder={queryOrder}&$top={$top}&continuationToken={continuationToken}&minMetricsTime={minMetricsTime}&definitionIds={definitionIds}&path={path}&builtAfter={builtAfter}&notBuiltAfter={notBuiltAfter}&includeAllProperties={includeAllProperties}&includeLatestBuilds={includeLatestBuilds}&taskIdFilter={taskIdFilter}&processType={processType}&yamlFilename={yamlFilename}&api-version=5.1
builddefinitions_url = ("https://dev.azure.com/%s/%s/_apis/build/definitions?api-version=%s" % (azuredevops_organization_name, azuredevops_project_id, api_version))
print("-------------------------------------------------------------")
print("---- About to get list of Build Definitions ----")  
getApiRequest(builddefinitions_url)  


#Get a list of builds
#GET https://dev.azure.com/{organization}/{project}/_apis/build/builds?definitions={definitions}&queues={queues}&buildNumber={buildNumber}&minTime={minTime}&maxTime={maxTime}&requestedFor={requestedFor}&reasonFilter={reasonFilter}&statusFilter={statusFilter}&resultFilter={resultFilter}&tagFilters={tagFilters}&properties={properties}&$top={$top}&continuationToken={continuationToken}&maxBuildsPerDefinition={maxBuildsPerDefinition}&deletedFilter={deletedFilter}&queryOrder={queryOrder}&branchName={branchName}&buildIds={buildIds}&repositoryId={repositoryId}&repositoryType={repositoryType}&api-version=5.1
buildds_url = ("https://dev.azure.com/%s/%s/_apis/build/builds?api-version=%s" % (azuredevops_organization_name, azuredevops_project_id, api_version))
print("-------------------------------------------------------------")
print("---- About to get list of Builds ----")  
getApiRequest(builddefinitions_url)  


#Get a list of artifacts for a given build
#GET https://dev.azure.com/{organization}/{project}/_apis/build/builds/{buildId}/artifacts?api-version=5.1

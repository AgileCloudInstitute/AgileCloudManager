import yaml
import re 

myYamlInputFile = "\\path\\to\\agile-cloud-manager\\enter-user-input-here-only.yaml"

def getReleaseDefData(yamlInputFile):
  with open(yamlInputFile) as f:
    topLevel_dict = yaml.safe_load(f)
    for item in topLevel_dict:
      print("item is: ", item)
      if re.match("meta", item):
        metaItems = topLevel_dict.get(item)
        for metaItem in metaItems: 
          if re.match("subscriptionName", metaItem):
            print(metaItem, " is: ", metaItems.get(metaItem))
          if re.match("subscriptionId", metaItem):
            print(metaItem, " is: ", metaItems.get(metaItem))
          if re.match("tenantId", metaItem):
            print(metaItem, " is: ", metaItems.get(metaItem))
          if re.match("pipeAzureRegion", metaItem):
            print(metaItem, " is: ", metaItems.get(metaItem))
          if re.match("storageAccountNameTerraformBackend", metaItem):
            print(metaItem, " is: ", metaItems.get(metaItem))
          if re.match("storageContainerNameTerraformBackend", metaItem):
            print(metaItem, " is: ", metaItems.get(metaItem))
          if re.match("azdoOrgServiceURL", metaItem):
            print(metaItem, " is: ", metaItems.get(metaItem))
      if re.match("connection", item):  
        connectionItems = topLevel_dict.get(item)  
        for connectionItem in connectionItems:
          if re.match("clientName", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
          if re.match("clientId", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
          if re.match("clientSecret", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
          if re.match("serviceConnectionName", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
          if re.match("azdoOrgPAT", connectionItem):
            print(connectionItem, " is: ", connectionItems.get(connectionItem))
      if re.match("agents", item):
        agentsItems = topLevel_dict.get(item)
        for agentsItem in agentsItems:
          if re.match("adminUser", agentsItem):
            print(agentsItem, " is: ", agentsItems.get(agentsItem))
          if re.match("adminPwd", agentsItem):
            print(agentsItem, " is: ", agentsItems.get(agentsItem))
          if re.match("pathToCloudInitScript", agentsItem):
            print(agentsItem, " is: ", agentsItems.get(agentsItem))
      if re.match("importProjectRepoBuild", item):
        projectRepoBuildCollections = topLevel_dict.get(item)
        for projectRepoBuild in projectRepoBuildCollections:
          for projectRepoBuildItem in projectRepoBuild: 
            if re.match("name", projectRepoBuildItem):
              print(projectRepoBuildItem, " is: ", projectRepoBuild.get(projectRepoBuildItem))
            if re.match("awsPublicAccessKey", projectRepoBuildItem):
              print(projectRepoBuildItem, " is: ", projectRepoBuild.get(projectRepoBuildItem))
            if re.match("awsSecretAccessKey", projectRepoBuildItem):
              print(projectRepoBuildItem, " is: ", projectRepoBuild.get(projectRepoBuildItem))
            if re.match("sourceRepo", projectRepoBuildItem):
              print(projectRepoBuildItem, " is: ", projectRepoBuild.get(projectRepoBuildItem))
            if re.match("s3BucketNameTF", projectRepoBuildItem):
              print(projectRepoBuildItem, " is: ", projectRepoBuild.get(projectRepoBuildItem))
            if re.match("dynamoDbTableNameTF", projectRepoBuildItem):
              print(projectRepoBuildItem, " is: ", projectRepoBuild.get(projectRepoBuildItem))
            if re.match("moduleKeys", projectRepoBuildItem):
              print("-----------------------------------------------")
              print("-----------------------------------------------")
              moduleKeysCollection = projectRepoBuild.get(projectRepoBuildItem)
              for moduleKey in moduleKeysCollection:
                print(moduleKey.get("name"), " ::: has key ::: ", moduleKey.get("value"))

getReleaseDefData(myYamlInputFile)

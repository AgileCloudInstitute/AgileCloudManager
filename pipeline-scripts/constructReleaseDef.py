import json
import yaml
import re

with open('createTerraformSimpleAWS.yaml') as f:
    my_dict = yaml.safe_load(f)
    for keyname, valueStr in my_dict.items():
        if re.match("name", keyname):
            print('name of release definition is: ', valueStr)
        if re.match("description", keyname):
            print('description of release definition is: ', valueStr)
        if re.match("environments", keyname):
            print("Inside environments block. ")
            for keyn, valu in valueStr.items():
                print(keyn, " is: ", valu)

print("--------------------------------------------------------")

pythonTaskData = json.load(open('pythonTaskTemplate.json', 'r'))  
  
print("pythonTaskData is: ", pythonTaskData)
print("--------------------------------------------------------")

pythonTaskData['name'] = 'new name'
pythonTaskData['inputs']['scriptPath'] = 'new path'
pythonTaskData['inputs']['arguments'] = 'new arguments'
pythonTaskData['inputs']['workingDirectory'] = 'new working directory'
print("--------------------------------------------------------")

print("revised pythonTaskData is: ", pythonTaskData)
print("--------------------------------------------------------")
deployPhaseData = json.load(open('deployPhaseTemplate.json', 'r'))
print("deployPhaseData is: ", deployPhaseData)

deployPhaseData['name'] = 'new name for deployment phase'
deployPhaseData['workflowTasks'] = [pythonTaskData]
print("--------------------------------------------------------")

print("revised deployPhaseData is: ", deployPhaseData)
print("--------------------------------------------------------")

environmentData = json.load(open('environmentTemplate.json', 'r'))
print("environmentData is: ", environmentData)
environmentData['name'] = 'new name of environment'
environmentData['deployPhases'] = [deployPhaseData]  
print("--------------------------------------------------------")

print("revised environmentData is: ", environmentData)
print("--------------------------------------------------------")


releaseDefData = json.load(open('releaseDefConstructorTemplate.json', 'r'))
print("releaseDefData is: ", releaseDefData)
releaseDefData['name'] = 'new release def name'
releaseDefData['description'] = 'new release def description'
releaseDefData['environments'] = [environmentData]
print("--------------------------------------------------------")
print("revised releaseDefData is: ", releaseDefData)
print("--------------------------------------------------------")



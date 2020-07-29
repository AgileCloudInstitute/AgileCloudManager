import json
import yaml
import re

with open('createTerraformSimpleAWS.yaml') as f:
  my_dict = yaml.safe_load(f)
  new_dict = {}
  for item in my_dict:
    print("item is: ", item)
    if re.match("name", item):
      print("name is: ", my_dict.get(item))
    if re.match("description", item):
      print("description is: ", my_dict.get(item))
    if re.match("environments", item):
      print("Inside environments block. ")
      print("environments item is: ", item)
      print("environments get(item) is: ", my_dict.get(item))
      # Using for loop 
      for environment in my_dict.get(item): 
        print("--------- Gonna print a new environment item ----------------")
        print(environment) 
        print("--------- Gonna decompose the environment item ----------------")
        for env_item in environment:
          print("env_item is: ", env_item)
          if re.match("name", env_item):
            print("name is: ", environment.get(env_item))
          if re.match("deployPhases", env_item):
            for deployPhase in environment.get(env_item):  
              print("--------- Gonna print a new deployment phase ----------------")
              print(deployPhase)
              print("--------- Gonna decompose the deployment phase ----------------")
              for depPhase_item in deployPhase:
                print("depPhase_item is: ", depPhase_item)
                if re.match("name", depPhase_item):  
                  print("name is: ", deployPhase.get(depPhase_item))  
                if re.match("workflowTasks", depPhase_item):  
                  for task in deployPhase.get(depPhase_item):   
                    print("--------- Gonna print a new workflow task ----------------")  
                    print(task)  
                    print("--------- Gonna decompose the workflow task ----------------")  
                    for task_item in task:  
                      print("task_item is: ", task_item)  
                      if re.match("name", task_item):  
                        print("name is: ", task.get(task_item))  
                      if re.match("type", task_item):  
                        print("type is: ", task.get(task_item))  
                      if re.match("scriptPath", task_item):  
                        print("scriptPath is: ", task.get(task_item))  
                      if re.match("arguments", task_item):  
                        print("arguments is: ", task.get(task_item))  
                      if re.match("workingDirectory", task_item):  
                        print("workingDirectory is: ", task.get(task_item))  
      print("--------------------------------------------------------")




        name = item['name']
        new_dict[name] = item

    
    for i in my_dict.keys():
        if re.match("name", i):
            print("name is: ", my_dict.get(i))
        if re.match("description", i):
            print("description is: ", my_dict.get(i))
        if re.match("environments", i):
            print("Inside environments block. ")
#            environments = i['environments']
            new_dict = {item['name']:item for item in data}
new_dict[environments] = i
            for j in new_dict.keys():
                print("iterating keys inside environment")
                print(j, " is: ", new_dict.get(j))

//////////////////////////////////

new_dict = {}
for item in data:
   name = item['name']
   new_dict[name] = item

    for keyname, valueStr in my_dict.items():
        if re.match("name", keyname):
            print('name of release definition is: ', valueStr)
        if re.match("description", keyname):
            print('description of release definition is: ', valueStr)
        if re.match("environments", keyname):
            print("Inside environments block. ")
            for keyn in my_dict[keyname].keys():
                print("keyn is: ", keyn)


dict.get('Education', "Never")                

for i in d.keys():
    print i
    for j in d[i].keys():
        print j

for i in d:
    print i
    for j in d[i]:
        print j
//////////////////////////////////////////////////////////////////////
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



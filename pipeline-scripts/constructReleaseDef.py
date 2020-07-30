import json
import yaml
import re

yamlDir = '../releases/yaml-definitions/'
yamlFile = yamlDir + 'createTerraformSimpleAWS.yaml'
jsonFragmentDir = '../releases/json-fragments/' 
pythonTaskTemplateFile = jsonFragmentDir + 'pythonTaskTemplate.json'  
deployPhaseTemplateFile = jsonFragmentDir + 'deployPhaseTemplate.json'
environmentTemplateFile = jsonFragmentDir + 'environmentTemplate.json'
releaseDefConstructorTemplateFile = jsonFragmentDir + 'releaseDefConstructorTemplate.json'

with open(yamlFile) as f:
  releaseDef_dict = yaml.safe_load(f)
  for item in releaseDef_dict:
    print("item is: ", item)
    if re.match("name", item):
      print("name is: ", releaseDef_dict.get(item))
    if re.match("description", item):
      print("description is: ", releaseDef_dict.get(item))
    if re.match("environments", item):
      print("Inside environments block. ")
      print("environments item is: ", item)
      print("environments get(item) is: ", releaseDef_dict.get(item))
      environmentsList = releaseDef_dict.get(item)
      print("len environmentsList is: ", len(environmentsList))
      for env_idx, environment in enumerate(environmentsList):
      # Using for loop 
      #for environment in my_dict.get(item): 
        print("--------- Gonna print a new environment item ----------------")
        print(env_idx, ": ", environment) 
        print("--------- Gonna decompose the environment item ----------------")
        for env_item in environment:
          print(env_idx, ": ", "env_item is: ", env_item)
          if re.match("name", env_item):
            print(env_idx, ": ", "name is: ", environment.get(env_item))
          if re.match("deployPhases", env_item):
            deployPhaseList = environment.get(env_item)
            print("len deployPhaseList is: ", deployPhaseList)
            for phase_idx, deployPhase in enumerate(deployPhaseList):  
              print("--------- Gonna print a new deployment phase ----------------")
              print(phase_idx, ": ", deployPhase)
              print("--------- Gonna decompose the deployment phase ----------------")
              for depPhase_item in deployPhase:
                print(phase_idx, ": ", "depPhase_item is: ", depPhase_item)
                if re.match("name", depPhase_item):  
                  print(phase_idx, ": ", "name is: ", deployPhase.get(depPhase_item))  
                if re.match("workflowTasks", depPhase_item):  
                  workflowTasksList = deployPhase.get(depPhase_item)
                  print("len workflowTasksList is: ", workflowTasksList)
                  for task_idx, task in enumerate(workflowTasksList):
                    print("--------- Gonna print a new workflow task ----------------")  
                    print(task_idx, ": ", task)  
                    print("--------- Gonna decompose the workflow task ----------------")  
                    for task_item in task:  
                      print(task_idx, ": ", "task_item is: ", task_item)  
                      if re.match("name", task_item):  
                        print(task_idx, ": ", "name is: ", task.get(task_item))  
                      if re.match("type", task_item):  
                        print(task_idx, ": ", "type is: ", task.get(task_item))  
                      if re.match("scriptPath", task_item):  
                        print(task_idx, ": ", "scriptPath is: ", task.get(task_item))  
                      if re.match("arguments", task_item):  
                        print(task_idx, ": ", "arguments is: ", task.get(task_item))  
                      if re.match("workingDirectory", task_item):  
                        print(task_idx, ": ", "workingDirectory is: ", task.get(task_item))  
                    if task_idx == (len(workflowTasksList)-1):
                      print("////////////////// FINISHED PROCESSING THE LAST TASK \\\\\\\\\\\\\\\\\\\\\\")
              if phase_idx == (len(deployPhaseList)-1):
                print("////////////////// FINISHED PROCESSING THE LAST DEPLOYMENT PHASE \\\\\\\\\\\\\\\\\\\\\\")
        if env_idx == (len(environmentsList)-1):
          print("////////////////// FINISHED PROCESSING THE LAST ENVIRONMENT \\\\\\\\\\\\\\\\\\\\\\")
      print("--------------------------------------------------------")
print("--------------------------------------------------------")


pythonTaskData = json.load(open(pythonTaskTemplateFile, 'r'))  
print("pythonTaskData is: ", pythonTaskData)
print("--------------------------------------------------------")
pythonTaskData['name'] = 'new name'
pythonTaskData['inputs']['scriptPath'] = 'new path'
pythonTaskData['inputs']['arguments'] = 'new arguments'
pythonTaskData['inputs']['workingDirectory'] = 'new working directory'
print("--------------------------------------------------------")
print("revised pythonTaskData is: ", pythonTaskData)
print("--------------------------------------------------------")



deployPhaseData = json.load(open(deployPhaseTemplateFile, 'r'))
print("deployPhaseData is: ", deployPhaseData)
deployPhaseData['name'] = 'new name for deployment phase'
deployPhaseData['workflowTasks'] = [pythonTaskData]
print("--------------------------------------------------------")
print("revised deployPhaseData is: ", deployPhaseData)
print("--------------------------------------------------------")



environmentData = json.load(open(environmentTemplateFile, 'r'))
print("environmentData is: ", environmentData)
environmentData['name'] = 'new name of environment'
environmentData['deployPhases'] = [deployPhaseData]  
print("--------------------------------------------------------")
print("revised environmentData is: ", environmentData)
print("--------------------------------------------------------")


releaseDefData = json.load(open(releaseDefConstructorTemplateFile, 'r'))
print("releaseDefData is: ", releaseDefData)
releaseDefData['name'] = 'new release def name'
releaseDefData['description'] = 'new release def description'
releaseDefData['environments'] = [environmentData]
print("--------------------------------------------------------")
print("revised releaseDefData is: ", releaseDefData)
print("--------------------------------------------------------")

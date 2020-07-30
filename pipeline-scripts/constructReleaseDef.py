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
  ############################################################################
  ################# START TRANSLATION OF RELEASE DEFINITION ##################
  ############################################################################
  releaseDefData = json.load(open(releaseDefConstructorTemplateFile, 'r'))
  print("releaseDefData is: ", releaseDefData)
  for item in releaseDef_dict:
    print("item is: ", item)
    if re.match("name", item):
      #print("name is: ", releaseDef_dict.get(item))
      releaseDefData['name'] = releaseDef_dict.get(item)
    if re.match("description", item):
      #print("description is: ", releaseDef_dict.get(item))
      releaseDefData['description'] = releaseDef_dict.get(item)
    if re.match("environments", item):
      print("Inside environments block. ")
      print("environments item is: ", item)
      print("environments get(item) is: ", releaseDef_dict.get(item))
      environmentsList = releaseDef_dict.get(item)
      print("len environmentsList is: ", len(environmentsList))
      environmentsDataList = []
      for env_idx, environment in enumerate(environmentsList):
        ############################################################################
        ################## START TRANSLATION OF EACH ENVIRONMENT ###################
        ############################################################################
        environmentData = json.load(open(environmentTemplateFile, 'r'))
        print("environmentData is: ", environmentData)
        print("--------- Gonna print a new environment item ----------------")
        print(env_idx, ": ", environment) 
        print("--------- Gonna decompose the environment item ----------------")
        for env_item in environment:
          print(env_idx, ": ", "env_item is: ", env_item)
          if re.match("name", env_item):
            #print(env_idx, ": ", "name is: ", environment.get(env_item))
            environmentData['name'] = environment.get(env_item)
          if re.match("deployPhases", env_item):
            deployPhaseList = environment.get(env_item)
            print("len deployPhaseList is: ", deployPhaseList)
            deployPhaseDataList = []
            for phase_idx, deployPhase in enumerate(deployPhaseList):  
              ############################################################################
              ################ START TRANSLATION OF EACH DEPLOYMENT PHASE ################
              ############################################################################
              deployPhaseData = json.load(open(deployPhaseTemplateFile, 'r'))
              print("deployPhaseData is: ", deployPhaseData)
              print("--------- Gonna print a new deployment phase ----------------")
              print(phase_idx, ": ", deployPhase)
              print("--------- Gonna decompose the deployment phase ----------------")
              for depPhase_item in deployPhase:  
                print(phase_idx, ": ", "depPhase_item is: ", depPhase_item)
                if re.match("name", depPhase_item):  
                  #print(phase_idx, ": ", "name is: ", deployPhase.get(depPhase_item))  
                  deployPhaseData['name'] = deployPhase.get(depPhase_item)
                if re.match("workflowTasks", depPhase_item):  
                  workflowTasksList = deployPhase.get(depPhase_item)
                  print("len workflowTasksList is: ", len(workflowTasksList))
                  taskDataList = []
                  for task_idx, task in enumerate(workflowTasksList):
                    ############################################################################
                    ###################### START TRANSLATION OF EACH TASK ######################
                    ############################################################################
                    pythonTaskData = json.load(open(pythonTaskTemplateFile, 'r'))  
                    print("pythonTaskData is: ", pythonTaskData)
                    print("--------------------------------------------------------")
                    print("--------- Gonna print a new workflow task ----------------")  
                    print(task_idx, ": ", task)  
                    print("--------- Gonna decompose the workflow task ----------------")  
                    for task_item in task:  
                      print(task_idx, ": ", "task_item is: ", task_item)  
                      if re.match("name", task_item):  
                        #print(task_idx, ": ", "name is: ", task.get(task_item))  
                        pythonTaskData['name'] = task.get(task_item)
                      if re.match("type", task_item):  
                        print(task_idx, ": ", "type is: ", task.get(task_item))
                        if re.match("Python", task.get(task_item)): 
                          pythonTaskData['taskId'] = '6392f95f-7e76-4a18-b3c7-7f078d2f7700'
                      if re.match("scriptPath", task_item):  
                        #print(task_idx, ": ", "scriptPath is: ", task.get(task_item))
                        pythonTaskData['inputs']['scriptPath'] = task.get(task_item)
                      if re.match("arguments", task_item):  
                        #print(task_idx, ": ", "arguments is: ", task.get(task_item))  
                        pythonTaskData['inputs']['arguments'] = task.get(task_item)
                      if re.match("workingDirectory", task_item):  
                        #print(task_idx, ": ", "workingDirectory is: ", task.get(task_item))  
                        pythonTaskData['inputs']['workingDirectory'] = task.get(task_item)
                    print("--------------------------------------------------------")
                    print("revised pythonTaskData is: ", pythonTaskData)
                    taskDataList.append(pythonTaskData)
                    print("--------------------------------------------------------")
                    ############################################################################
                    ####################### END TRANSLATION OF EACH TASK #######################
                    ############################################################################
                    if task_idx == (len(workflowTasksList)-1):
                      print("////////////////// FINISHED PROCESSING THE LAST TASK \\\\\\\\\\\\\\\\\\\\\\")
                  print("--------------------------------------------------------")
                  print("taskDataList is: ", taskDataList)
                  print("--------------------------------------------------------")
                  deployPhaseData['workflowTasks'] = taskDataList
              if phase_idx == (len(deployPhaseList)-1):
                print("////////////////// FINISHED PROCESSING THE LAST DEPLOYMENT PHASE \\\\\\\\\\\\\\\\\\\\\\")
                ############################################################################
                ################# END TRANSLATION OF EACH DEPLOYMENT PHASE #################
                ############################################################################
                print("--------------------------------------------------------")
                print("revised deployPhaseData is: ", deployPhaseData)
                print("--------------------------------------------------------")
              deployPhaseDataList.append(deployPhaseData)
            print("--------------------------------------------------------")
            print("deployPhaseDataList is:", deployPhaseDataList)
            print("--------------------------------------------------------")
            environmentData['deployPhases'] = deployPhaseDataList 
        print("--------------------------------------------------------")
        print("revised environmentData is: ", environmentData)
        environmentsDataList.append(environmentData)
        print("--------------------------------------------------------")
        ############################################################################
        ################### END TRANSLATION OF EACH ENVIRONMENT ####################
        ############################################################################
        if env_idx == (len(environmentsList)-1):
          print("////////////////// FINISHED PROCESSING THE LAST ENVIRONMENT \\\\\\\\\\\\\\\\\\\\\\")
      print("--------------------------------------------------------")
      print("revised environmentsDataList is: ", environmentsDataList)
  releaseDefData['environments'] = environmentsDataList
  print("--------------------------------------------------------")
  print("revised releaseDefData is: ", releaseDefData)
  print("--------------------------------------------------------")
  

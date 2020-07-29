import json

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



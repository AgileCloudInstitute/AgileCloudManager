import json

data = json.load(open('pythonTaskTemplate.json', 'r'))

print("data is: ", data)

data['name'] = 'new name'
data['inputs']['scriptPath'] = 'new path'
data['inputs']['arguments'] = 'new arguments'
data['inputs']['workingDirectory'] = 'new working directory'

print("revised data is: ", data)



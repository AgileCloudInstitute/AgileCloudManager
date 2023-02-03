## Copyright 2023 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

import subprocess
import re
import sys
import json
import os
import requests
import time

from command_formatter import command_formatter
from log_writer import log_writer
import config_cliprocessor as cliproc

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
timeOutMins = 1
numIntervals = timeOutMins*6

class controller_custom:

  outputVariables = []

  def __init__(self):  
    pass

  #@public
  def runCustomController(self, operation, systemConfig, controllerPath, controllerCommand, mappedVariables, serviceType, instance):
    import config_cliprocessor 
    cf = command_formatter()
    cmdPrefix = ""
    print("controllerCommand is: ", controllerCommand)
    if ("$location" in controllerCommand) and (not controllerCommand.startswith("$location")):
      cmdPrefix = controllerCommand.split("$location")[0]
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    fullControllerPath = userCallingDir + controllerPath #+"\""
    fullControllerPath = cf.formatPathForOS(fullControllerPath)
    from command_builder import command_builder
    cbldr = command_builder()
    outputDict = {'calledFromCustomController':True}
    varsFragment = cbldr.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, 'customController', outputDict)
    controllerCommand = cmdPrefix+fullControllerPath+' '+operation+' '+varsFragment
    self.runShellCommand(controllerCommand)
 
  #@public
  def runCustomControllerAPI(self, operation, systemConfig, controllerPath, mappedVariables, serviceType, instance):
    import config_cliprocessor 
    cf = command_formatter()
    lw = log_writer()
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    fullControllerPath = userCallingDir + controllerPath #+"\""
    fullControllerPath = cf.formatPathForOS(fullControllerPath)
    from command_builder import command_builder
    cbldr = command_builder()
    outputDict = {'calledFromCustomController':True}
    varsFragment = cbldr.getVarsFragment(systemConfig, serviceType, instance, mappedVariables, 'customController', outputDict)
    print("custom varsFragment is: ", varsFragment)
    varsFragparts = varsFragment.split(' ')
    varsFile = 'nothing'
    templateFile = 'nothing'
    for file in varsFragparts:
      if file.startswith('--varsfile://'):
        varsFile = file.replace('--varsfile://', '')
      if file.startswith('--templateFile://'):
        templateFile = file.replace('--templateFile://', '')

    varsFileData = None
    templateFileData = None
    #Get data from varsFile
    if os.path.isfile(varsFile):
      with open(varsFile) as f:
        varsFileData = json.load(f)
        print("varsFileData is: ", varsFileData)
    else:
      logString = "ERROR: The value given for --varsFile is not a file located at: "+varsFile
      lw.writeLogVerbose("acm", logString)
      exit(1)

    #get data from templateFile
    if os.path.isfile(templateFile):
      with open(templateFile) as f:
        templateFileData = json.load(f)
        print("templateFileData is: ", templateFileData)
    else:
      logString = "ERROR: The value given for --templateFile is not a file located at: "+templateFile
      lw.writeLogVerbose("acm", logString)
      exit(1)
    print("operation is: ", operation)
    if not self.isListOfDictionaries(varsFileData):
      logString = "ERROR: The value given for varsFileData is not a list of dictionaries.  Halting program so you can debug the root cause of the problem. "
      lw.writeLogVerbose("acm", logString)
      exit(1)
    if not self.isListOfDictionaries(templateFileData):
      logString = "ERROR: The value given for templateFileData is not a list of dictionaries.  Halting program so you can debug the root cause of the problem. "
      lw.writeLogVerbose("acm", logString)
      exit(1)
    postJson = { 
      'command': operation,
      'varsFileData': varsFileData,
      'templateFileData': templateFileData
    }
    postJson = str(postJson)
    postJson = postJson.replace("'",'"')
    print('postJson is: ', postJson)
    if not self.is_json(postJson):
      logString = "ERROR: The value of postJson is not valid JSON.  Halting program so you can examine the root cause of the problem. "
      lw.writeLogVerbose("acm", logString)
      exit(1)
    print("mappedVariables is: ", mappedVariables)
    print("instance is: ", instance)
    myurl = instance.get("controller")
    myurl = myurl.replace("$customControllerAPI.", "")
    myurl = "http://localhost:"+myurl
    print("myurl is: ", myurl)
    import platform
    if platform.system() == 'Linux':
      curlCommand = "curl "+myurl
      print("curlCommand is: ", curlCommand)
      self.runShellCommand(curlCommand)
    if platform.system() == 'Windows':
      pshellCommand = 'powershell -command "$Response = Invoke-WebRequest -Uri "+myurl+";$StatusCode = $Response.StatusCode;$StatusCode;$Response"'
      self.runShellCommand(pshellCommand)
    print("BREAKPOINT X")
    sys.exit(1)
    if (operation == "on") or (operation == "off"):
      self.postCommand(myurl, postJson)
    elif operation == "output":
      self.getOutputs(myurl, "output")
    else:
      logString = "ERROR: Invalid value for operation.  You must specify either on, off, or output. The value given was: "+operation
      lw.writeLogVerbose("acm", logString)
      exit(1)
    #if operation == "output":
    #  quit("BREAKPOINT 0987654321")

  #@public
  def runShellCommand(self, commandToRun):
    lw = log_writer()
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    captureOutputs = False
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        if 'ERROR in customController.' in decodedline:
          lw.writeLogVerbose("shell", decodedline)
          sys.exit(1)
        if decodedline.startswith('Finished output variables.'):
          captureOutputs = False
        if captureOutputs:
          lineParts = decodedline.split(' = ')
          lineDict = {'varName':lineParts[0].replace(' ', ''), 'varValue':lineParts[1].replace(' ','')}
          self.outputVariables.append(lineDict)
        if decodedline.startswith('Output variables:'):
          captureOutputs = True
        lw.writeLogVerbose("shell", decodedline)
      else:
        break

  def isListOfDictionaries(self, myjson):
    if isinstance(myjson, list):
      for item in myjson:
        if not isinstance(item, dict):
          return False
    else:
      return False
    return True

  def is_json(self, myjson):
    try:
      json.loads(myjson)
    except ValueError as e:
      return False
    return True

  def postCommand(self, myurl, postJson, counter=0):
    import json
    lw = log_writer()
    logString = "About to do POST to custom controller."
    lw.writeLogVerbose("acm", logString)
    headers = {
      'content-type': 'application/json',
      'api-string': cliproc.inputVars.get('apiString')
    }
    res = requests.post(myurl, json.dumps(postJson), headers=headers)
    if res.json()['logEntries'] != None:
      for logEntry in res.json()['logEntries']:
        lw.writeLogVerbose(logEntry["controllerName"], logEntry["message"])
    if res.status_code == 200: #This indicates success.
      logString = "-------------------- POST res is 200. ------------------------"
      lw.writeLogVerbose("acm", logString)
      #Recursively calling getOutputs() in next line to confirm whether or not the controller successfully completes its job.
      self.getOutputs(myurl, "post")
    if res.status_code == 400: #This indicates that requested resource is not present.
      logString = "-------------------- POST res is 400. ------------------------"
      lw.writeLogVerbose("acm", logString)
      logString  = "POST res.json is: "+str(res.json())
      lw.writeLogVerbose("acm", logString)
    if res.status_code == 500: #This indicates an error from the server.
      logString = "-------------------- POST res is 500. ------------------------"
      lw.writeLogVerbose("acm", logString)
      logString = "POST res.json is: "+ str(res.json())
      lw.writeLogVerbose("acm", logString)
      #Iterate from 1 to numIntervals
      if counter < (numIntervals+1):
        logString = "Custom controller received a 500 response from the controller after "+ str(counter*10)+ " seconds. Continuing to retry.  "
        lw.writeLogVerbose("acm", logString)
        time.sleep(10)
        counter +=1
        self.postCommand(myurl, counter)
      else:
        logString = "ERROR: GET request to custom controller did not return a 200 response even after retrying for "+ str(timeOutMins)+ " minutes. Check your cloud provider portal to make sure there are no orphaned resources.  Also, consider re-running the command again and consider posting a request on our GitHub site for the time out interval to be increased.  "
        lw.writeLogVerbose("acm", logString)
        exit(1)

  def getOutputs(self, myurl, source, counter=0):
    headers = {
      'content-type': 'application/json',
      'api-string': cliproc.inputVars.get('apiString')
    }
    lw = log_writer()
    if source == "output":
      logString = "About to GET"
      lw.writeLogVerbose("acm", logString)
    res = requests.get(myurl, headers=headers)
    if res.json()['logEntries'] != None:
      for logEntry in res.json()['logEntries']:
        lw.writeLogVerbose(logEntry["controllerName"], logEntry["message"])
    if res.status_code == 102: #This indicates the custom controller is in process and has not yet returned a response.
      #Iterate from 1 to numIntervals
      if counter < (numIntervals+1):
        if source == "output":
          logString = "Custom controller GET is still processing after "+ str(counter*10)+ " seconds. Will continue to retry. "
        else:
          logString = "Custom controller POST is still processing after "+ str(counter*10)+ " seconds. Will continue to retry. "
        lw.writeLogVerbose("acm", logString)
        time.sleep(10)
        counter +=1
        self.getOutputs(myurl, source, counter)
      else:
        if source == "output":
          logString = "ERROR: GET request to custom controller did not return a 200 response even after retrying for "+ str(timeOutMins)+ " minutes. Check you cloud provider portal to make sure there are no orphaned resources.  Also, consider re-running the command again and consider posting a request on our GitHub site for the time out interval to be increased.  "
        else:
          logString = "ERROR: POST request to custom controller did not return a 200 response even after retrying for "+ str(timeOutMins)+ " minutes. Check you cloud provider portal to make sure there are no orphaned resources.  Also, consider re-running the command again and consider posting a request on our GitHub site for the time out interval to be increased.  "
        lw.writeLogVerbose("acm", logString)
        exit(1)

    if res.status_code == 400: #This is where the server replies that the client had an error such as a malformed request.
      logString = "GET 400 Error"
      lw.writeLogVerbose("acm", logString)
      logString = "GET res.json is: "+ str(res.json())
      lw.writeLogVerbose("acm", logString)
      logString = "ERROR: A 400 response was returned by the controller.  Please examine the logs to determine the root cause.  "
      lw.writeLogVerbose("acm", logString)
      exit(1)

    if res.status_code == 200: #This indicates success.
      if source == "output":
        logString = "-------------------- GET res is 200 ok. ------------------------"
        lw.writeLogVerbose("acm", logString)
      if len(res.json()['outputVars']) == 0:
        if counter < (numIntervals+1):
          if source == "output":
            logString = "Custom controller GET is still processing after "+ str(counter*10)+ " seconds. Will continue to retry. "
          else:
            logString = "Custom controller POST is still processing after "+ str(counter*10)+ " seconds. Will continue to retry. "
          lw.writeLogVerbose("acm", logString)
          time.sleep(10)
          counter +=1
          self.getOutputs(myurl, source, counter)
        else:
          if source == "output":
            logString = "ERROR: GET request to custom controller did not return completed response even after retrying for "+ str(timeOutMins)+ " minutes. Check your cloud provider portal to make sure there are no orphaned resources.  Also, consider re-running the command again and consider posting a request on our GitHub site for the time out interval to be increased.  "
          else:
            logString = "ERROR: POST request to custom controller did not return completed response even after retrying for "+ str(timeOutMins)+ " minutes. Check your cloud provider portal to make sure there are no orphaned resources.  Also, consider re-running the command again and consider posting a request on our GitHub site for the time out interval to be increased.  "
          lw.writeLogVerbose("acm", logString)
          exit(1)
      for item in res.json()['outputVars']:
        logString = "item is: "+ str(item)
        lw.writeLogVerbose("acm", logString)
        #quit("0987654321acbdefghijklmnopqrstuvwxyz")
        self.outputVariables.append(item)

    if res.status_code == 500: #This indicates an error from the server.
      logString = "GET 500 Error"
      lw.writeLogVerbose("acm", logString)
      #Iterate from 1 to numIntervals
      if counter < (numIntervals+1):
        logString = "Custom controller received a 500 response from the controller after "+ str(counter*10)+ " seconds. Continuing to retry.  "
        lw.writeLogVerbose("acm", logString)
        time.sleep(10)
        counter +=1
        self.getOutputs(myurl, source, counter)
      else:
        logString = "ERROR: GET request to custom controller did not return a 200 response even after retrying for "+ str(timeOutMins)+ " minutes. Check your cloud provider portal to make sure there are no orphaned resources.  Also, consider re-running the command again and consider posting a request on our GitHub site for the time out interval to be increased.  "
        lw.writeLogVerbose("acm", logString)
        exit(1)
    #quit("zyxwvutsrqponmlkjihgfedcba")
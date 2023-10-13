## Copyright 2023 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

import subprocess
import re
import requests
import base64
import json
import sys 
import os

from command_formatter import command_formatter
from log_writer import log_writer
  
class command_runner:
    
  def __init__(self):  
    pass
   
  ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
  
  #@public
  def getShellJsonResponse(self, cmd,counter=0):  
    lw = log_writer()
    process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
    data = process.stdout
    err = process.stderr
    try:
      if process:
        data, err = process.communicate()
        if process.returncode != 0:
          print("ERROR: The subprocess command returned a non-zero return code: ", process.returncode)
    except AttributeError: #This should handle CompletedpProcess error.  
      pass
    logString = "data string is: " + data
    lw.writeLogVerbose("acm", logString)
    logString = "err is: " + str(err)
    lw.writeLogVerbose("acm", logString)
    logString = "process.returncode is: " + str(process.returncode)
    lw.writeLogVerbose("acm", logString)

    #These next 6 lines added to help diagnose and handle azure latency problem with empty results and exit code 0
    logString = "type(data) is: "+str(type(data))
    lw.writeLogVerbose("acm", logString)
    logString = "type(list(data)) is: "+str(type(list(data)))
    lw.writeLogVerbose("acm", logString)
    logString = "str(data).replace(" ","") is: "+str(data).replace(" ","")
    lw.writeLogVerbose("acm", logString)
    logString = "len(str(data).replace(" ","")) is: "+str(len(str(data).replace(" ","")))
    lw.writeLogVerbose("acm", logString)
    logString = "counter is: "+str(counter)
    lw.writeLogVerbose("acm", logString)

    if process.returncode == 0:
      #These next 20 lines added 24 August to handle azure latency problem with empty results and exit code 0
      if ("az resource list --resource-group" in cmd) and ("--resource-type Microsoft.Compute/images" in cmd) and (len(str(data).replace(" ","")) == 3):
        if counter < 16:
          logString = "Sleeping 30 seconds before running the command a second time in case a latency problem caused the attempt to fail. "
          lw.writeLogVerbose('acm', logString)
          counter +=1 
          logString = "Attempt "+str(counter)+ " out of 15. "
          lw.writeLogVerbose('acm', logString)
          import time
          time.sleep(30)
          data = self.getShellJsonResponse(cmd,counter)
          return data
        else:  
          logString = "Error: " + str(err)
          lw.writeLogVerbose("shell", logString)
          logString = "Error: Return Code is: " + str(process.returncode)
          lw.writeLogVerbose("shell", logString)
          logString = "ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
      else:
        logString = str(data)
        lw.writeLogVerbose("shell", logString)
        decodedData = data #.decode('utf-8')
        return decodedData
    else:
      if counter < 16:
        logString = "Sleeping 30 seconds before running the command a second time in case a latency problem caused the attempt to fail. "
        lw.writeLogVerbose('acm', logString)
        counter +=1 
        logString = "Attempt "+str(counter)+ " out of 15. "
        lw.writeLogVerbose('acm', logString)
        import time
        time.sleep(30)
        data = self.getShellJsonResponse(cmd,counter)
        return data 
      else:   
        if "(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found." in str(err):
          logString = "WARNING: "+"(FeatureNotFound) The feature 'VirtualMachineTemplatePreview' could not be found."
          lw.writeLogVerbose('shell')
          logString = "Continuing because this error message is often benign.  If you encounter downstream problems resulting from this, please report your use case so that we can examine the cause. "
          lw.writeLogVerbose('acm', logString)
          return decodedData
        else:
          logString = "Error: " + str(err)
          lw.writeLogVerbose("shell", logString)
          logString = "Error: Return Code is: " + str(process.returncode)
          lw.writeLogVerbose("shell", logString)
          logString = "ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)

  #@public
  def runShellCommand(self, commandToRun):
    lw = log_writer()
    logString = "commandToRun is: "+commandToRun
    lw.writeLogVerbose("acm", logString)
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    logString = "Immediate return code is: "+str(proc.returncode)
    lw.writeLogVerbose("acm", logString)
    logString = "Immediate stdout is: "+str(proc.stdout)
    lw.writeLogVerbose("acm", logString)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=self.ansi_escape.sub('', thetext)
        logString = decodedline
        lw.writeLogVerbose("shell", logString)
      else:
        data, err = proc.communicate()
        logString = "proc.returncode at end of command run is: "+str(proc.returncode)
        lw.writeLogVerbose("acm", logString)
        if (proc.returncode != 0) and (proc.returncode != None):
          logString = "About to terminate program due to a non-zero return code."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
        break

  #@public
  def runPreOrPostProcessor(self, preOrPost, processorSpecs, operation):
    import config_cliprocessor
    cf = command_formatter()
    lw = log_writer()
    if operation == 'on':
      if ('locationOn' in processorSpecs) and ('commandOn' in processorSpecs):
        location = processorSpecs['locationOn']
        command = processorSpecs['commandOn']
      else: # return without doing anyting because there is no processor present for this case
        return
    elif operation == 'off':
      if ('locationOff' in processorSpecs) and ('commandOff' in processorSpecs):
        location = processorSpecs['locationOff']
        command = processorSpecs['commandOff']
      else: # return without doing anyting because there is no processor present for this case
        return
    fullyQualifiedPathToScript = config_cliprocessor.inputVars.get('userCallingDir')+location
    fullyQualifiedPathToScript = cf.formatPathForOS(fullyQualifiedPathToScript)
    logString = "fullyQualifiedPathToScript is: "+fullyQualifiedPathToScript
    lw.writeLogVerbose('shell', logString)
    if os.path.isfile(fullyQualifiedPathToScript):
      commandToRun = command.replace('$location',fullyQualifiedPathToScript)
      if preOrPost == "pre":
        logString = "preprocessor command is: "+commandToRun
      elif preOrPost == "post":
        logString = "postprocessor command is: "+commandToRun
      else:
        logString = str(preOrPost)+" is not a valid value for preOrPost.  Halting program so this can be fixed where the error originates. "
        lw.writeLogVerbose('shell', logString)
        sys.exit(1)
      lw.writeLogVerbose('shell', logString)
      self.runShellCommand(commandToRun)
    else: 
      logString = "ERROR: "+fullyQualifiedPathToScript+" is not a valid path. "
      lw.writeLogVerbose('shell', logString)
      sys.exit(1)

  #@public
  def getAccountKey(self, commandToRun):
    lw = log_writer()
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, shell=True)
    data = proc.stdout
    err = proc.stderr
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=self.ansi_escape.sub('', thetext)
        lw.writeLogVerbose("shell", decodedline)
        return decodedline
      else:
        data, err = proc.communicate()
        logString = "proc.returncode at end of command run is: "+str(proc.returncode)
        lw.writeLogVerbose("acm", logString)
        if (proc.returncode != 0) and (proc.returncode != None):
          logString = "About to terminate program due to a non-zero return code."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
        break

  #@public
  def checkIfAzInstalled(self, commandToRun, vers):
    lw = log_writer()
    resp = json.loads(self.getShellJsonResponse(commandToRun))
    cliV = resp['azure-cli']
    versParts = vers.split('.')
    cliVParts = cliV.split('.')
    if (int(cliVParts[0]) >= int(versParts[0])) and (int(cliVParts[1]) >= int(versParts[1])):
      logString = 'Dependency is installed.'
      lw.writeLogVerbose("acm", logString)
      return logString
    else:
      logString = "Wrong version of dependency is installed for azure-cli."
      lw.writeLogVerbose("acm", logString)
      return logString

  #@public
  def checkIfAwsInstalled(self, commandToRun, vers):
    lw = log_writer()
    expectedMajorVers = vers.split(".")[0]
    expectedMinorVers = vers.split(".")[1]
    resp = self.getShellJsonResponse(commandToRun)
    print("AWS response is: ", resp)
    if isinstance(resp, str) and (resp.count(" ")>0):
      firstPart = resp.split(" ")[0]
      awsVers = firstPart.split('/')[1] 
      majorVers = awsVers.split(".")[0]
      minorVers = awsVers.split(".")[1]
      if int(expectedMajorVers) < int(majorVers):
        logString = 'Dependency is installed.'
        lw.writeLogVerbose("acm", logString)
        return logString
      elif int(expectedMajorVers) == int(majorVers):
        if int(expectedMinorVers) <= int(minorVers):
          logString = 'Dependency is installed.'
          lw.writeLogVerbose("acm", logString)
          return logString
        else:
          logString = "Wrong version of dependency is installed for aws-cli.  Correct version is NOT installed."
          lw.writeLogVerbose("acm", logString)
          return logString
      else:
        logString = "Wrong version of dependency is installed for aws-cli.  Correct version is NOT installed."
        lw.writeLogVerbose("acm", logString)
        return logString
    else:
      logString = "Dependency is NOT installed for aws-cli."
      lw.writeLogVerbose("acm", logString)
      return logString

  #@public
  def checkIfAzdoInstalled(self, commandToRun, vers):
    lw = log_writer()
    resp = json.loads(self.getShellJsonResponse(commandToRun))
    logString = 'azdo response is: ' + str(resp)
    lw.writeLogVerbose("acm", logString)
    azdoV = resp['extensions']['azure-devops']
    versParts = vers.split('.')
    azdoVParts = azdoV.split('.')
    if (int(azdoVParts[0]) >= int(versParts[0])) and (int(azdoVParts[1]) >= int(versParts[1])):
      logString = 'Dependency is installed.'
      lw.writeLogVerbose("acm", logString)
      return logString
    else:
      logString = "Wrong version of dependency is installed for azure-devops extension of azure-cli."
      lw.writeLogVerbose("acm", logString)
      return logString

  #@public
  def checkIfInstalled(self, commandToRun, vers):
    lw = log_writer()
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    data = proc.stdout
    err = proc.stderr
    match = False
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=self.ansi_escape.sub('', thetext)
        if vers in decodedline:
          match = True
          logString = "Dependency is installed."
          lw.writeLogVerbose("acm", logString)
          return logString
      else:
        data, err = proc.communicate()
        logString = "proc.returncode at end of command run is: "+str(proc.returncode)
        lw.writeLogVerbose("acm", logString)
        if (proc.returncode != 0) and (proc.returncode != None):
          logString = "About to terminate program due to a non-zero return code."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
        break
    logString = 'Dependency is NOT installed.  Please make sure your machine is properly provisioned.'
    lw.writeLogVerbose("acm", logString)
    return logString

  #@public
  def runShellCommandInWorkingDir(self, commandToRun, workingDir):
    lw = log_writer()
    proc = subprocess.Popen( commandToRun,cwd=workingDir, stdout=subprocess.PIPE, shell=True)
    data = proc.stdout
    err = proc.stderr
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=self.ansi_escape.sub('', thetext)
        logString = decodedline
        lw.writeLogVerbose("shell", logString)
      else:
        data, err = proc.communicate()
        logString = "proc.returncode at end of command run is: "+str(proc.returncode)
        lw.writeLogVerbose("acm", logString)
        if (proc.returncode != 0) and (proc.returncode != None):
          logString = "About to terminate program due to a non-zero return code."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
        break

  #@public
  def getShellJsonData(self, cmd, workingDir):
    if "TF_LOG" in os.environ:
      oldTfLog = os.environ["TF_LOG"]
      os.environ["TF_LOG"] = "ERROR"
    process = subprocess.Popen(
        cmd,cwd=workingDir,
        shell=True,
        stdout=subprocess.PIPE)
    data = process.stdout
    err = process.stderr
    try:
      if process:
        data, err = process.communicate()
        if process.returncode != 0:
          print("ERROR: The subprocess command returned a non-zero return code: ", process.returncode)
    except AttributeError: #This should handle CompletedpProcess error.  
      pass
    filename = workingDir + 'my-directory-list.txt'
    try:
      os.remove(filename)
    except OSError:
      pass
    if process.returncode == 0:
      decodedData = data.decode('utf-8')
      if "TF_LOG" in os.environ:
        os.environ["TF_LOG"] = oldTfLog
      return decodedData
    else:
      print("Error: " + str(err))
      print("Error: Return Code is: " + str(process.returncode))
      print("ERROR: Failed to return Json response.  Halting the program so that you can debug the cause of the problem.")
      if "TF_LOG" in os.environ:
        os.environ["TF_LOG"] = oldTfLog
      sys.exit(1)

  #@public
  def getPoolQueueIdApiRequest(self, orgName, projId, qName, azPat):  
    lw = log_writer()
    orgName = orgName.replace('"','')
    orgName = orgName.replace("'","")
    azPat = azPat.replace('"','')
    azPat = azPat.replace("'","")
    #Assemble headers  
    personal_access_token = ":"+azPat
    headers = {}  
    headers['Content-type'] = "application/json"  
    headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))  
    #Assemble the endpoint URL
    #Get the Agent Pool Queues whose name matches the search criteria.  This should only be one queue because name should be a unique key.  
    api_version_p = "5.1-preview.1"
    #GET https://dev.azure.com/{organization}/{project}/_apis/distributedtask/queues?queueName={queueName}&actionFilter={actionFilter}&api-version=5.1-preview.1
    queues_url = ("https://dev.azure.com/%s/%s/_apis/distributedtask/queues?queueName=%s&api-version=%s" % (orgName, projId, qName, api_version_p))
    logString = "-------------------------------------------------------------"
    lw.writeLogVerbose("acm", logString)
    logString = "queues_url is: " + queues_url
    lw.writeLogVerbose("acm", logString)
    #Make the request    
    r = requests.get(queues_url, headers=headers)
    logString = "r.status_code is: " + str(r.status_code)
    lw.writeLogVerbose("acm", logString)
    #Add some better error handling here to handle various response codes.  We are assuming that a 200 response is received in order to continue here.  
    if r.status_code != 200:
      print(r.content)
      logString = "ERROR: getPoolQueueIdApiRequest() returned a non-200 response code.  Halting program so you can debug."
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    myQueuesData = r.json()
    logString = "myQueuesData is: " + str(myQueuesData)
    lw.writeLogVerbose("acm", logString)
    #Using index 0 here because queue_name should be a unique key that brings only one result in this response
    poolQueueId = myQueuesData['value'][0]['id']
    logString = "poolQueueId is: " + str(poolQueueId)
    lw.writeLogVerbose("acm", logString)
    return poolQueueId

  #@public
  def createAzdoServiceEndpointApiRequest(self, data, azdo_organization_name, azPAT):
    lw = log_writer()
    azPAT = azPAT.replace("'","")
    azPAT = azPAT.replace('"','')
    try:
      personal_access_token = ":"+azPAT
      headers = {}
      headers['Content-type'] = "application/json"
      headers['Authorization'] = b'Basic ' + base64.b64encode(personal_access_token.encode('utf-8'))
      api_version = "6.0-preview.4"
      url = ("https://dev.azure.com/%s/_apis/serviceendpoint/endpoints?api-version=%s" % (azdo_organization_name, api_version))
    except Exception as e:
      logString = "ERROR: Attempting to create the azure devops service endpoint triggered the following exception:  "
      lw.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      lw.writeLogVerbose("acm", logString)
      exit(1)
    try:
      r = requests.post(url, data=json.dumps(data), headers=headers)
    except Exception as e:
      logString = "ERROR: Attempting to create the azure devops service endpoint triggered the following exception:  "
      lw.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      lw.writeLogVerbose("acm", logString)
      exit(1)
    try:
      respCode = str(r.status_code)
      logString = "r.status_code is: " + respCode
      lw.writeLogVerbose("acm", logString)
      logString = "r.json() is: " + str(r.json())
      lw.writeLogVerbose("acm", logString)
    except Exception as e:
      logString = "ERROR: Attempting to create the azure devops service endpoint triggered the following exception:  "
      lw.writeLogVerbose("acm", logString)
      logString = "Error {0}".format(str(e.args[0])).encode("utf-8")
      lw.writeLogVerbose("acm", logString)
      logString = str(r.content).format(str(e.args[0])).encode("utf-8")
      lw.writeLogVerbose("acm", logString)
      exit(1)
    return respCode, r.json()

  #@public
  def runShellCommandForTests(self, commandToRun):
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    data = proc.stdout
    err = proc.stderr
    lw = log_writer()
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=self.ansi_escape.sub('', thetext)
        print(decodedline)
      else:
        data, err = proc.communicate()
        logString = "proc.returncode at end of command run is: "+str(proc.returncode)
        lw.writeLogVerbose("acm", logString)
        if (proc.returncode != 0) and (proc.returncode != None):
          logString = "About to terminate program due to a non-zero return code."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
        proc.kill()
        break
    proc.kill()

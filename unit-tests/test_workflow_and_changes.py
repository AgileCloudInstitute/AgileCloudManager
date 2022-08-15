import unittest
import yaml
import pathlib
import platform
import sys
import os

#Run the tests in this file by running the following command in the terminal:
#python -m unittest agile-cloud-manager/unit-tests/test_workflow_and_changes.py

class test_workflow_platform(unittest.TestCase):
  logVerbose = ''

  def addAcmDirToPath(self):
    acmDir = str(pathlib.Path(__file__).parent.resolve().parent.resolve())+'/app'
    acmDir = self.formatPathForOS(acmDir)
    sys.path.insert(0, acmDir)

  def setAcmVariables(self, log_writer, myCliProc, testType):
    # inputsDir is where the key files originate.  These will be sourced before you use ACM
#    if inputType == 'sanitized':
    inputsDir = str(pathlib.Path(__file__).parent.resolve())+'/input-files'
#    elif inputType == 'secret':
#      inputsDir = os.path.expanduser('~') + '/acm/keys/starter/'
#    else:
#      inputsDir = os.path.expanduser('~') + '/acm/keys/'+inputType+'/'
    inputsDir = self.formatPathForOS(inputsDir)
    myCliProc.inputVars['dirOfYamlKeys'] = inputsDir
#    if inputType == 'sanitized':
    myCliProc.inputVars['dirOfOutput'] = inputsDir
#    elif inputType == 'secret':
#      config_cliprocessor.inputVars['dirOfOutput'] = self.formatPathForOS(str(pathlib.Path(inputsDir).parent.resolve())+'/')

    # acmKeysDir is the staging ground that ACM will use to create and destroy transitory key files during operations.
    acmKeysDir = self.getAcmKeysDir()
    acmKeysDir = self.formatPathForOS(acmKeysDir)
#    varsFileAndPath = acmKeysDir+'/keys.tfvars'
#    varsFileAndPath = self.formatPathForOS(varsFileAndPath)
#    userCallingDir = str(os.path.abspath("."))+'\\'
#    userCallingDir = self.formatPathForOS(userCallingDir)
    #Get logsPath
    if platform.system() == 'Windows':
      #putting log into acmKeysDir because this is just a test.
      verboseLogFilePath = acmKeysDir + '/logs'
      verboseLogFilePath = self.formatPathForOS(verboseLogFilePath)
      pathlib.Path(verboseLogFilePath).mkdir(parents=True, exist_ok=True)
    elif platform.system() == 'Linux':
      verboseLogFilePath = '/var/log/acm/'
    yamlFileAndPath = str(pathlib.Path(__file__).parent.resolve())+'/input-files/acm.yaml'
    yamlFileAndPath = self.formatPathForOS(yamlFileAndPath)
    print('yamlFileAndPath is: ', yamlFileAndPath)
    myCliProc.inputVars['yamlInfraConfigFileAndPath'] = yamlFileAndPath
    myCliProc.inputVars['test'] = True
    myCliProc.inputVars['testType'] = testType
    myCliProc.inputVars['verboseLogFilePath'] = verboseLogFilePath
    logVerbose = verboseLogFilePath + "/log-verbose.log"
    self.logVerbose = self.formatPathForOS(logVerbose)
    lw = log_writer()
    lw.replaceLogFile()

  def getAcmKeysDir(self):
    # This is the staging ground where tests will put key files produced during test operations.
    # This is NOT where the keys will be sourced from.
    if platform.system() == 'Windows':
      acmKeysDir = os.path.expanduser("~")+'/acm/testkeys/'
    elif platform.system() == 'Linux':
      acmKeysDir = '/usr/acm/testkeys/'
    if not os.path.exists(acmKeysDir):
      os.makedirs(acmKeysDir, exist_ok=True) 
    return acmKeysDir
  
  def formatPathForOS(self, input):
    if platform.system() == "Windows":
      #First strip down to one \ in each spot.
      input = input.replace('/','\\')
      input = input.replace('\\\\','\\')
      input = input.replace('\\\\\\','\\')
      #Now replace singles with doubles so you get C:\\path\\to\\a\\file with proper escale sequence.
      input = input.replace('\\','\\\\')
    elif platform.system() == "Linux":
      if '\\' in input:
        print('*** trap 1')
      if '\\\\' in input:
        print('*** trap 2')
      input = input.replace('\\','/')
      input = input.replace('//','/')
      input = input.replace('///','/')
    if input.endswith('/n'):
      input = input[:-2] + '\n'
    return input

  def getPlatformConfig(self):
    yamlFileAndPath = str(pathlib.Path(__file__).parent.resolve())+'/input-files/acm.yaml'
    yamlFileAndPath = self.formatPathForOS(yamlFileAndPath)
    print('yamlFileAndPath is: ', yamlFileAndPath)
    with open(yamlFileAndPath) as f:  
      topLevel_dict = yaml.safe_load(f)
    return topLevel_dict

  def checkLogWorkflowOutput(self, numChangeReportsExpected, numChangesExpected):
    import ast
    returnBool = False
    numStartTriggers = 0
#    print('ggg self.logVerbose is: ', self.logVerbose)
#    quit('poiuytrewq')
    with open(self.logVerbose, "r") as f0:
      for line in f0:
        if "...     overallStatus changed from In Process to Completed" in line:
          numStartTriggers += 1
    print('... numStartTriggers is: ', str(numStartTriggers))
    if numStartTriggers != 1:
      quit("ERROR: log file is corrupted.  There can be only one startTrigger line containing the following: '...     overallStatus changed from In Process to Completed' .  Check log_writer.replaceLogFile() to make sure log files are being refreshed properly. ")
    startTrigger = False
    changeReportLines = []
    with open(self.logVerbose, "r") as f1:
      for line in f1:
        if "...     overallStatus changed from In Process to Completed" in line:
          startTrigger = True
        if startTrigger:
          if '{' in line:
            changeReportLines.append(line.replace('[ acm ] ', '').replace('\n', ''))
    print('changeReportLines is: ', str(changeReportLines))
    print('len(changeReportLines) is: ', len(changeReportLines))
    numChanges = 0
    numChangesCompleted = 0
    for changeReport in changeReportLines:
      changeDict = ast.literal_eval(changeReport)
      for change in changeDict['changes']:
        print("change is: ", change)
        numChanges +=1
        if change['changeCompleted'] == True:
          numChangesCompleted += 1
    print('number of changeReports is: ', str(len(changeReportLines)))
    print('expected number of changeReports is: ', str(numChangeReportsExpected))
    print('numChanges is: ', str(numChanges))
    print('expected numChanges is: ', str(numChangesExpected))
    print('numChangesCompleted is: ', str(numChangesCompleted))
    print('expected numChangesCompleted is: ', str(numChangesExpected))
    if (len(changeReportLines)==numChangeReportsExpected) and (numChanges==numChangesExpected) and(numChangesCompleted==numChangesExpected):
      returnBool = True
    print('self.logVerbose is: ', str(self.logVerbose))
    return returnBool


  def test_platformOn(self):
#    self.addAcmDirToPath()
    from app.workflow_platform import workflow_platform
    import app.config_cliprocessor
    from app.log_writer import log_writer
    self.setAcmVariables(log_writer, app.config_cliprocessor, "workflow")
    wfplat1 = workflow_platform() 
    wfplat1.onPlatform()
    numChangeReportsExpected = 54
    numChangesExpected = 80
    returnBool = self.checkLogWorkflowOutput(numChangeReportsExpected, numChangesExpected)
    self.assertTrue(returnBool)

#  def test_platformOff(self):
#    self.addAcmDirToPath() 
#    from workflow_platform import workflow_platform
#    import config_cliprocessor 
#    from log_writer import log_writer
#    self.setAcmVariables(log_writer, config_cliprocessor, "workflow")
#    wfplat2 = workflow_platform()
#    wfplat2.offPlatform()
#    numChangeReportsExpected = 54
#    numChangesExpected = 80
#    returnBool = self.checkLogWorkflowOutput(numChangeReportsExpected, numChangesExpected)
#    self.assertTrue(returnBool)

####Add a test case to validate the force flag
###  def test_platformOffForce(self):
###    self.assertTrue(True)

#  def test_foundationOn(self):
#    self.addAcmDirToPath()
#    from workflow_system import workflow_system
#    import config_cliprocessor 
#    from log_writer import log_writer
#    self.setAcmVariables(log_writer, config_cliprocessor, "workflow")
#    config_cliprocessor.inputVars['systemName'] = "admin"
#    wfsys1 = workflow_system()
#    wfsys1.callOnFoundationDirectly()
#    numChangeReportsExpected = 6
#    numChangesExpected = 8
#    returnBool = self.checkLogWorkflowOutput(numChangeReportsExpected, numChangesExpected)
#    self.assertTrue(returnBool)

#  def test_foundationOff(self):
#    self.addAcmDirToPath()
#    from workflow_system import workflow_system
#    import config_cliprocessor 
#    from log_writer import log_writer
#    self.setAcmVariables(log_writer, config_cliprocessor, "workflow")
#    config_cliprocessor.inputVars['systemName'] = "admin"
#    wfsys1 = workflow_system()
#    wfsys1.callOffFoundationDirectly()
#    numChangeReportsExpected = 6
#    numChangesExpected = 8
#    returnBool = self.checkLogWorkflowOutput(numChangeReportsExpected, numChangesExpected)
#    self.assertTrue(returnBool)

#  def test_servicesOn(self):
#    self.addAcmDirToPath()
#    from workflow_system import workflow_system
#    import config_cliprocessor 
#    from log_writer import log_writer
#    self.setAcmVariables(log_writer, config_cliprocessor, "workflow")
#    config_cliprocessor.inputVars['systemName'] = "admin"
#    wfsys1 = workflow_system()
#    wfsys1.callOnServicesDirectly()
#    numChangeReportsExpected = 16
#    numChangesExpected = 23
#    returnBool = self.checkLogWorkflowOutput(numChangeReportsExpected, numChangesExpected)
#    self.assertTrue(returnBool)

#  def test_servicesOff(self):
#    self.addAcmDirToPath()
#    from workflow_system import workflow_system
#    import config_cliprocessor 
#    from log_writer import log_writer
#    self.setAcmVariables(log_writer, config_cliprocessor, "workflow")
#    config_cliprocessor.inputVars['systemName'] = "admin"
#    wfsys1 = workflow_system()
#    wfsys1.callOffServicesDirectly()
#    numChangeReportsExpected = 16
#    numChangesExpected = 23
#    returnBool = self.checkLogWorkflowOutput(numChangeReportsExpected, numChangesExpected)
#    self.assertTrue(returnBool)

#  def test_serviceTypeOn(self):
#    self.addAcmDirToPath()
#    from workflow_service_type import workflow_service_type
#    import config_cliprocessor 
#    from log_writer import log_writer
#    self.setAcmVariables(log_writer, config_cliprocessor, "workflow")
#    config_cliprocessor.inputVars['systemName'] = "admin"
#    config_cliprocessor.inputVars['serviceType'] = "admin"
#    level = "servicetype"
#    wfSvcTyp1 = workflow_service_type()
#    wfSvcTyp1.callOnServiceDirectly(level)
#    numChangeReportsExpected = 12
#    numChangesExpected = 17
#    returnBool = self.checkLogWorkflowOutput(numChangeReportsExpected, numChangesExpected)
#    self.assertTrue(returnBool)

#  def test_serviceTypeOff(self):
#    self.addAcmDirToPath()
#    from workflow_service_type import workflow_service_type
#    import config_cliprocessor 
#    from log_writer import log_writer
#    self.setAcmVariables(log_writer, config_cliprocessor, "workflow")
#    config_cliprocessor.inputVars['systemName'] = "admin"
#    config_cliprocessor.inputVars['serviceType'] = "admin"
#    level = "servicetype"
#    wfSvcTyp1 = workflow_service_type()
#    wfSvcTyp1.callOffServiceDirectly(level)
#    numChangeReportsExpected = 12
#    numChangesExpected = 17
#    returnBool = self.checkLogWorkflowOutput(numChangeReportsExpected, numChangesExpected)
#    self.assertTrue(returnBool)

#  def test_serviceInstanceOn(self):
#    self.addAcmDirToPath()
#    from workflow_service_type import workflow_service_type
#    import config_cliprocessor 
#    from log_writer import log_writer
#    self.setAcmVariables(log_writer, config_cliprocessor, "workflow")
#    config_cliprocessor.inputVars['systemName'] = "admin"
#    config_cliprocessor.inputVars['serviceType'] = "admin"
#    config_cliprocessor.inputVars['serviceInstance'] = "projectManagement"
#    level = "serviceinstance"
#    wfSvcTyp1 = workflow_service_type()
#    wfSvcTyp1.callOnServiceDirectly(level)
#    numChangeReportsExpected = 10
#    numChangesExpected = 14
#    returnBool = self.checkLogWorkflowOutput(numChangeReportsExpected, numChangesExpected)
#    self.assertTrue(returnBool)

#  def test_serviceInstanceOff(self):
#    self.addAcmDirToPath()
#    from workflow_service_type import workflow_service_type
#    import config_cliprocessor 
#    from log_writer import log_writer
#    self.setAcmVariables(log_writer, config_cliprocessor, "workflow")
#    config_cliprocessor.inputVars['systemName'] = "admin"
#    config_cliprocessor.inputVars['serviceType'] = "admin"
#    config_cliprocessor.inputVars['serviceInstance'] = "projectManagement"
#    level = "serviceinstance"
#    wfSvcTyp1 = workflow_service_type()
#    wfSvcTyp1.callOffServiceDirectly(level)
#    numChangeReportsExpected = 10
#    numChangesExpected = 14
#    returnBool = self.checkLogWorkflowOutput(numChangeReportsExpected, numChangesExpected)
#    self.assertTrue(returnBool)



if __name__ == '__main__':
    unittest.main()

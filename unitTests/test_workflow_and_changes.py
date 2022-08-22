import unittest
import yaml
import pathlib
import platform
import sys
import os

#https://docs.python.org/3/tutorial/modules.html#importing-from-a-package

#Run the tests in this file by running the following command in the terminal:
#python -m unittest AgileCloudManager.unitTests.test_workflow_and_changes
#python -m unittest AgileCloudManager.unitTests.test_controller_arm


class test_workflow_platform(unittest.TestCase):
  logVerbose = ''

  def addAcmDirToPath(self):
    acmDir = str(pathlib.Path(__file__).parent.resolve().parent.resolve())+'/app'
    acmDir = self.formatPathForOS(acmDir)
    sys.path.insert(0, acmDir)

  def setAcmVariables(self, log_writer, myCliProc, testType):
    # inputsDir is where the key files originate.  These will be sourced before you use ACM
    inputsDir = str(pathlib.Path(__file__).parent.resolve())+'/input-files'
    inputsDir = self.formatPathForOS(inputsDir)
    myCliProc.inputVars['dirOfYamlKeys'] = inputsDir
    myCliProc.inputVars['dirOfOutput'] = inputsDir
    # acmKeysDir is the staging ground that ACM will use to create and destroy transitory key files during operations.
    acmKeysDir = self.getAcmKeysDir()
    acmKeysDir = self.formatPathForOS(acmKeysDir)
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
    print('xx yamlFileAndPath is: ', yamlFileAndPath)
    myCliProc.inputVars['yamlInfraConfigFileAndPath'] = yamlFileAndPath
    myCliProc.inputVars['test'] = True
    myCliProc.inputVars['testType'] = testType
    myCliProc.inputVars['verboseLogFilePath'] = verboseLogFilePath
    logVerbose = verboseLogFilePath + "/log-verbose.log"
    self.logVerbose = self.formatPathForOS(logVerbose)
    print("xx myCliProc.inputVars['verboseLogFilePath'] is: ", myCliProc.inputVars['verboseLogFilePath'])
    print('xx self.logVerbose is: ', self.logVerbose)
#    quit('++--55--44++')
#    if os.path.isfile(self.logVerbose):
#      count1 = 0
#      with open(self.logVerbose) as f1:
#        count1 = sum(1 for _ in f1)
#      print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx count1 is: ', count1)
    lw = log_writer()
    lw.replaceLogFile()
#      count2 = 0
#      with open(self.logVerbose) as f2:
#        count2 = sum(1 for _ in f2)
#      print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx count2 is: ', count2)
#      print('self.logVerbose is: ', self.logVerbose)
#      if count1 != count2:
#        quit('---000999888777666555444333222111---')

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
    print('hjk returnBool is: ', returnBool)
    return returnBool


  def test_platformOn(self):
    self.addAcmDirToPath()
    from AgileCloudManager.app.workflow_platform import workflow_platform
    import AgileCloudManager.app.config_cliprocessor
    from AgileCloudManager.app.log_writer import log_writer
#    from workflow_platform import workflow_platform
#    import config_cliprocessor
#    from log_writer import log_writer
#    cliproc.processInputArgs(['AgileCloudManager\\app\\acm.py', 'platform', 'on'])
    self.setAcmVariables(log_writer, AgileCloudManager.app.config_cliprocessor, "workflow")
    wfplat1 = workflow_platform() 
    wfplat1.onPlatform()
    numChangeReportsExpected = 54
    numChangesExpected = 80
    returnBool = self.checkLogWorkflowOutput(numChangeReportsExpected, numChangesExpected)
    print('test returnVal is: ', returnBool)
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

import unittest
import yaml
import subprocess
import pathlib
import platform
import sys

#Run the tests in this file by running the following command in the terminal:
#python -m unittest acm-tests/test_acm.py

class TestCommand(unittest.TestCase):

  def addAcmDirToPath(self):
    acmDir = str(pathlib.Path(__file__).parent.resolve().parent.resolve())+'/agile-cloud-manager'
    acmDir = self.formatPathForOS(acmDir)
    sys.path.insert(0, acmDir)

  def setAcmVariables(self, config_cliprocessor, testType):
    yamlFileAndPath = str(pathlib.Path(__file__).parent.resolve())+'/input-files/acm.yaml'
    yamlFileAndPath = self.formatPathForOS(yamlFileAndPath)
    print('yamlFileAndPath is: ', yamlFileAndPath)
    config_cliprocessor.inputVars['yamlInfraConfigFileAndPath'] = yamlFileAndPath
    config_cliprocessor.inputVars['test'] = True
    config_cliprocessor.inputVars['testType'] = testType



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

  def runWorkflowShellCommand(self, commandToRun):
    proc = subprocess.Popen( commandToRun,cwd=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        pass
      else:
        break
    proc.stdout.close()
    proc.wait()
    import ast
    returnBool = False
    with open(self.logVerbose, "r") as f1:
      last_line = f1.readlines()[-1]
    print('last_line is: ', last_line)
    jones = last_line[last_line.index('{'):]
    jonesDict = ast.literal_eval(jones)
    truesCount = 0
    for change in jonesDict['changes']:
      print("change is: ", change)
      if change['changeCompleted'] == True:
        truesCount += 1
    if (truesCount == len(jonesDict['changes'])) and (len(jonesDict['changes']) > 0):
      returnBool = True
    print("... truesCount is: ", truesCount)
    return returnBool

  #All of the following tests assume that a True for the last command in the changesManifest means true for all operations in the changesManifest.  This should hold true due to the in-process validation within the program itself.
  def test_platformOn(self):
    self.addAcmDirToPath()
    import config_cliprocessor
    self.setAcmVariables(config_cliprocessor, "workflow")
    
#    myCommand = "python acm.py platform on test=workflow"
#    returnBool = self.runWorkflowShellCommand(myCommand)
#    self.assertTrue(returnBool)

  ##Add a valid platformConfig.yaml file to test the following off without force.  If you run the following with the same platformConfig used for the other tests, this test will throw an error because the workflow stops when you try to off protected types without the --force flag.
#  def test_platformOff(self):
#    myCommand = "python acm.py platform off test=workflow"
#    returnBool = self.runWorkflowShellCommand(myCommand)
#    self.assertTrue(returnBool)

#  def test_platformOffForce(self):
#    myCommand = "python acm.py platform off --force test=workflow"
#    returnBool = self.runWorkflowShellCommand(myCommand)
#    self.assertTrue(returnBool)

#  def test_foundationOn(self):
#    myCommand = "python acm.py foundation on test=workflow"
#    returnBool = self.runWorkflowShellCommand(myCommand)
#    self.assertTrue(returnBool)

#  def test_foundationOff(self):
#    myCommand = "python acm.py foundation off test=workflow"
#    returnBool = self.runWorkflowShellCommand(myCommand)
#    self.assertTrue(returnBool)

#  def test_servicesOn(self):
#    myCommand = "python acm.py services on test=workflow"
#    returnBool = self.runWorkflowShellCommand(myCommand)
#    self.assertTrue(returnBool)

#  def test_servicesOff(self):
#    myCommand = "python acm.py services off test=workflow"
#    returnBool = self.runWorkflowShellCommand(myCommand)
#    self.assertTrue(returnBool)

if __name__ == '__main__':
    unittest.main()

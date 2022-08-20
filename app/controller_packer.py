## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    
  
import sys
import subprocess
import re
  
from command_builder import command_builder
from command_formatter import command_formatter
from log_writer import log_writer
  
class controller_packer:
  
  foundationOutput = {}
  ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
  success_packer = ''
  
  def __init__(self):  
    pass
  
  #@public
  def packerCrudOperation(self, operation, systemConfig, image):
    import config_cliprocessor
    lw = log_writer()
    cf = command_formatter()
    cloud = systemConfig.get("cloud")
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    if len(cloud) < 2:
      logString = "ERROR: cloud name not valid.  Add better validation checking to the code. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    #1. First assemble the variables
    templateName = image.get("templateName")
    template_config_file_name = 'empty'
    if templateName.count('/') == 2:
      nameParts = templateName.split("/")
      if (len(nameParts[0]) > 1) and (len(nameParts[1]) >1) and (len(nameParts[2]) > 1):
        relative_path_to_instances = nameParts[0] + '\\' + nameParts[1]
        relative_path_to_instances = cf.formatPathForOS(relative_path_to_instances)
        template_Name = nameParts[2]  
        path_to_application_root = userCallingDir + nameParts[0] + "\\" + nameParts[1] + "\\"
        path_to_application_root = cf.formatPathForOS(path_to_application_root)
        template_config_file_name = userCallingDir + nameParts[0] + '\\packer\\' + template_Name + '.json'
        template_config_file_name = cf.formatPathForOS(template_config_file_name)
        startup_script_file_and_path = userCallingDir + nameParts[0] + '\\scripts\\' + 'fileName'
        startup_script_file_and_path = cf.formatPathForOS(startup_script_file_and_path)
      else:
        logString = 'ERROR: templateName is not valid. '
        lw.writeLogVerbose("acm", logString)
        sys.exit(1)
    else:  
      logString = "Template name is not valid.  Must have only one /.  "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    #3. Then third assemble and run command
    self.assembleAndRunPackerCommand(operation, systemConfig, image, template_config_file_name)
    if self.success_packer == 'true':
      logString = "done with -- " + image.get("instanceName") + " -----------------------------------------------------------------------------"
      lw.writeLogVerbose("acm", logString)
    else:
      logString = "Failed Packer Build.  Stopping program so you can diagnose the problem. "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)

  #@private
  def assembleAndRunPackerCommand(self, operation, systemConfig, image, template_config_file_name):
    import config_cliprocessor
    lw = log_writer()
    commandToRun = 'invalid value must be reset below'
    tool = "packer"
    imageRepoDir = self.getImageRepoDir(image)
    binariesPath = config_cliprocessor.inputVars.get('dependenciesBinariesPath') 
    if operation == 'build':
      #Passing foundationInstanceName into getVarsFragment because we want to use the keys associated with the network foundation when we are attaching anything to the network foundation.
      cb = command_builder()
      varsFrag = cb.getVarsFragment(systemConfig, None, image, image.get('mappedVariables'), tool, self)
      commandToRun = binariesPath + "packer build " + varsFrag + " " + template_config_file_name
    else:
      logString = "Error: Invalid value for operation: " + operation
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)
    logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
    lw.writeLogVerbose("acm", logString)
    lw.writeLogVerbose("acm", logString)
    logString = "commandToRun is: " + commandToRun
    lw.writeLogVerbose("acm", logString)
    logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
    lw.writeLogVerbose("acm", logString)
    lw.writeLogVerbose("acm", logString)
    logString = "imageRepoDir is: " + imageRepoDir
    lw.writeLogVerbose("acm", logString)
    logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
    lw.writeLogVerbose("acm", logString)
#    quit('DEBUG packer command during test.')
    self.runPackerCommand(commandToRun, imageRepoDir)
    if self.success_packer == "false":
      logString = "commandRunner.success_packer is false"
      lw.writeLogVerbose("acm", logString)
      logString = "Halting program inside assembleAndRunPackerCommand() so that you can debug the error that should be stated above in the output.  "
      lw.writeLogVerbose("acm", logString)
      sys.exit(1)

  #@private
  def getImageRepoDir(self, image):
    import config_cliprocessor
    cf = command_formatter()
    #Note:  Here we are assuming a properly formatted input string with the repo name at the left of the first / , and with the template name at the right of the last / , with an optional intermediary directory in between. 
    if image.get('templateName').count('/') == 2:
      relativeTemplateRepo = image.get('templateName').split('/')[0] + '\\' + image.get('templateName').split('/')[1]
    elif image.get('templateName').count('/') == 1:
      relativeTemplateRepo = image.get('templateName').split('/')[0]
    else:
      logString = "ERROR: templateName for an image repository must have either one or two / partitions.  "
      quit(logString)
    userCallingDir = config_cliprocessor.inputVars.get('userCallingDir')
    templateRepoDir = userCallingDir + '\\' + relativeTemplateRepo
    templateRepoDir = cf.formatPathForOS(templateRepoDir)
    return templateRepoDir

  #@private
  def runPackerCommand(self, commandToRun, workingDir):
    lw = log_writer()
    proc = subprocess.Popen( commandToRun,cwd=workingDir,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=self.ansi_escape.sub('', thetext)
        lw.writeLogVerbose("packer", decodedline)
        if "Builds finished. The artifacts of successful builds are" in decodedline:
          self.success_packer="true"
        elif "machine readable:" in decodedline:
          if "error-count" in decodedline:
            logString = "error-count is in decodedline.  "
            lw.writeLogVerbose("acm", logString)
            self.success_packer="false"
      else:
        break

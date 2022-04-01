## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import sys

import config_fileprocessor
import command_builder
import command_runner
import logWriter
import config_cliprocessor

def packerCrudOperation(operation, systemInstanceName, keyDir, typeName, instanceNames, yaml_infra_config_file_and_path):
  foundationInstanceName = config_fileprocessor.getFoundationInstanceName(yaml_infra_config_file_and_path)
  cloud = config_fileprocessor.getCloudName(yaml_infra_config_file_and_path)
  app_parent_path = config_cliprocessor.inputVars.get('app_parent_path')
  module_config_file_and_path = ''
  if len(cloud) < 2:
    logString = "ERROR: cloud name not valid.  Add better validation checking to the code. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
#    logWriter.updateTheTaxonomy(systemInstanceName, None, "imageBuilds", instanceName, "In Process")
    #1. First assemble the variables
  templateName = config_fileprocessor.getImageTemplateName(yaml_infra_config_file_and_path, typeName, instanceName)  
  template_config_file_name = 'empty'
  if templateName.count('/') == 2:
    nameParts = templateName.split("/")
    if (len(nameParts[0]) > 1) and (len(nameParts[1]) >1) and (len(nameParts[2]) > 1):
      relative_path_to_instances = nameParts[0] + '\\' + nameParts[1]
      relative_path_to_instances = command_builder.formatPathForOS(relative_path_to_instances)
      template_Name = nameParts[2]  
      path_to_application_root = app_parent_path + nameParts[0] + "\\" + nameParts[1] + "\\"
      path_to_application_root = command_builder.formatPathForOS(path_to_application_root)
      module_config_file_and_path = app_parent_path + nameParts[0] + '\\variableMaps\\' + template_Name + '.csv'
      module_config_file_and_path = command_builder.formatPathForOS(module_config_file_and_path)
      template_config_file_name = app_parent_path + nameParts[0] + '\\packer\\' + template_Name + '.json'
      template_config_file_name = command_builder.formatPathForOS(template_config_file_name)
      startup_script_file_and_path = app_parent_path + nameParts[0] + '\\scripts\\' + 'fileName'
      startup_script_file_and_path = command_builder.formatPathForOS(startup_script_file_and_path)
    else:
      logString = 'ERROR: templateName is not valid. '
      logWriter.writeLogVerbose("acm", logString)
      sys.exit(1)
  else:  
    logString = "Template name is not valid.  Must have only one /.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  yaml_keys_file_and_path = command_builder.getKeyFileAndPath(keyDir, typeName, cloud)
  #3. Then third assemble and run command
  assembleAndRunPackerCommand(cloud, systemInstanceName, keyDir, templateName, operation, yaml_infra_config_file_and_path, yaml_keys_file_and_path, foundationInstanceName, instanceName, typeName, module_config_file_and_path, template_config_file_name, startup_script_file_and_path)
#    logWriter.updateTheTaxonomy(systemInstanceName, None, "imageBuilds", instanceName, "Completed")
  if command_runner.success_packer == 'true':
    logString = "done with -- " + imageTypeName + " -----------------------------------------------------------------------------"
    logWriter.writeLogVerbose("acm", logString)
  else:
    logString = "Failed Packer Build.  Stopping program so you can diagnose the problem. "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)

#def assembleAndRunCommand(cloud, systemInstanceName, keyDir, template_Name, operation, yaml_infra_config_file_and_path, foundationInstanceName, parentInstanceName, instanceName, destinationCallInstance, typeName, module_config_file_and_path):
#  configAndSecretsPath = config_cliprocessor.inputVars.get('configAndSecretsPath')
#  dirOfConfig = configAndSecretsPath + "vars\\config\\" + cloud + "\\"
#  moduleConfigFileAndPath = module_config_file_and_path
#  commandToRun = 'invalid value must be reset below'
#  tool = "terraform"
#  org = config_fileprocessor.getFirstLevelValue(yaml_infra_config_file_and_path, "organization")
#  binariesPath = config_cliprocessor.inputVars.get('dependenciesBinariesPath') 
#  if operation == 'off':
#    #Passing foundationInstanceName into getVarsFragment because we want to use the keys associated with the network foundation when we are attaching anything to the network foundation.
#    varsFrag = command_builder.getVarsFragment(tool, keyDir, yaml_infra_config_file_and_path, moduleConfigFileAndPath, cloud, instanceName, parentInstanceName, instanceName, org)
#    commandToRun = binariesPath + "terraform destroy -auto-approve" + varsFrag
#  elif operation == 'on':
#    #Passing foundationInstanceName into getVarsFragment because we want to use the keys associated with the network foundation when we are attaching anything to the network foundation.
#    varsFrag = command_builder.getVarsFragment(tool, keyDir, yaml_infra_config_file_and_path, moduleConfigFileAndPath, cloud, instanceName, parentInstanceName, instanceName, org)
#    commandToRun = binariesPath + "terraform apply -auto-approve -parallelism=1 " + varsFrag
#  elif operation == 'output':
#    commandToRun = binariesPath + 'terraform output'
#  else:
#    logString = "Error: Invalid value for operation: " + operation
#    logWriter.writeLogVerbose("acm", logString)
#    sys.exit(1)
#  logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
#  logWriter.writeLogVerbose("acm", logString)
#  logWriter.writeLogVerbose("acm", logString)
#  logString = "commandToRun is: " + commandToRun
#  logWriter.writeLogVerbose("acm", logString)
#  logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
#  logWriter.writeLogVerbose("acm", logString)
#  logWriter.writeLogVerbose("acm", logString)
#  if systemInstanceName == "admin":
#    import traceback
#    traceback.print_stack()
#  command_runner.runTerraformCommand(commandToRun, destinationCallInstance)

def assembleAndRunPackerCommand(cloud, systemInstanceName, keyDir, template_Name, operation, yaml_infra_config_file_and_path, yaml_keys_file_and_path, foundationInstanceName, instanceName, typeName, moduleConfigFileAndPath, template_config_file_name, startup_script_file_and_path):
  commandToRun = 'invalid value must be reset below'
  tool = "packer"
  imageRepoDir = config_fileprocessor.getImageRepoDir(yaml_infra_config_file_and_path, template_Name)
  binariesPath = config_cliprocessor.inputVars.get('dependenciesBinariesPath') 
  org = config_fileprocessor.getFirstLevelValue(yaml_infra_config_file_and_path, "organization")
  if operation == 'build':
    #Passing foundationInstanceName into getVarsFragment because we want to use the keys associated with the network foundation when we are attaching anything to the network foundation.
    varsFrag = command_builder.getVarsFragment(tool, keyDir, yaml_infra_config_file_and_path, moduleConfigFileAndPath, cloud, foundationInstanceName, None, instanceName, org)
    commandToRun = binariesPath + "packer build " + varsFrag + " " + template_config_file_name
  else:
    logString = "Error: Invalid value for operation: " + operation
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)
  logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
  logWriter.writeLogVerbose("acm", logString)
  logWriter.writeLogVerbose("acm", logString)
  logString = "commandToRun is: " + commandToRun
  logWriter.writeLogVerbose("acm", logString)
  logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
  logWriter.writeLogVerbose("acm", logString)
  logWriter.writeLogVerbose("acm", logString)
  logString = "imageRepoDir is: " + imageRepoDir
  logWriter.writeLogVerbose("acm", logString)
  logString = "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
  logWriter.writeLogVerbose("acm", logString)
#  quit("BREAKPOINT to debug packer command. ")
  command_runner.runPackerCommand(commandToRun, imageRepoDir)
  if command_runner.success_packer == "false":
    logString = "commandRunner.success_packer is false"
    logWriter.writeLogVerbose("acm", logString)
    logString = "Halting program inside assembleAndRunPackerCommand() so that you can debug the error that should be stated above in the output.  "
    logWriter.writeLogVerbose("acm", logString)
    sys.exit(1)

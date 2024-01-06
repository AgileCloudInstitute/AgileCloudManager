## Copyright 2024 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

import os
import sys

from controller_custom import controller_custom
from controller_packer import controller_packer
from controller_cf import controller_cf
from log_writer import log_writer
from command_formatter import command_formatter

class controller_image:
  
  imageIsAvailable = False
  
  def __init__(self):  
    pass
  
  #@public     
  def buildImages(self, systemConfig, keyDir):
    lw = log_writer()
    cfmtr = command_formatter()
    app_parent_path = os.path.dirname(os.path.realpath("..\\")) + '\\'
    app_parent_path = cfmtr.formatPathForOS(app_parent_path)
    operation = 'on'
    ###Next Build The Images
    if "images" in systemConfig.get("foundation").keys():
      for image in systemConfig.get("foundation").get("images"):
        instanceTool = image.get("controller")
        if instanceTool == 'packer':
          operation = 'build'
          cp = controller_packer()
          cp.packerCrudOperation(operation, systemConfig, image)
        elif instanceTool == 'cloudformation':
          ccf = controller_cf()
          ccf.buildCloudFormationImage(systemConfig, image, keyDir)
        elif instanceTool.startswith('$customController.'):
          controllerPath = instanceTool.replace("$customController.","")
          controllerCommand = image.get("controllerCommand")
          mappedVariables = image.get("mappedVariables")
          c_cust = controller_custom()
          c_cust.runCustomController('on', systemConfig, controllerPath, controllerCommand, mappedVariables, 'images', image)
        elif instanceTool.startswith('$customControllerAPI.'):
          controllerPath = instanceTool.replace("$customControllerAPI.","")
          mappedVariables = image.get("mappedVariables")
          c_cust = controller_custom()
          c_cust.runCustomControllerAPI('on', systemConfig, controllerPath, mappedVariables, 'images', image)
        else:
          logString = "Your config file specified an image build tool not supported: "+instanceTool+" . Halting program so you can check your configuration."
          lw.writeLogVerbose("acm", logString)
          sys.exit(1)
 
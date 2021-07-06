## Copyright 2021 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import os
from distutils.dir_util import copy_tree
from pathlib import Path
import shutil 


def runSetup():
  app_parent_path = os.path.dirname(os.path.realpath("..\\"))
  from_path = app_parent_path+"\\agile-cloud-manager"+"\\"+"move-to-directory-outside-app-path\\"
  dest_path = app_parent_path+"\\config-outside-acm-path\\"
  #Create destination directory if it does not already exist 
  Path(dest_path).mkdir(parents=True, exist_ok=True)
  #Copy config and secret templates outside app path before they can be safely populated
  copy_tree(from_path, dest_path)
  commandRunner.runShellCommandInWorkingDir("dir", app_parent_path)
#The next 2 lines are here for placekeeping.  make sure to move them to the appropriate place.
  addExteensionCommand = 'az extension add --name azure-devops'
  commandRunner.runShellCommand(addExteensionCommand)


def undoSetup():
  app_parent_path = os.path.dirname(os.path.realpath("..\\"))
  dest_path = app_parent_path+"\\config-outside-acm-path\\"
  try:
    shutil.rmtree(dest_path, ignore_errors=True)
  except FileNotFoundError:
    print("The config-outside-acm-path directory does not exist.  It may have already been deleted.")
  commandRunner.runShellCommandInWorkingDir("dir", app_parent_path)
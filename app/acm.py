## Copyright 2022 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    

import config_cliprocessor as cliproc
from workflow_platform import workflow_platform
from workflow_system import workflow_system
from workflow_service_type import workflow_service_type
from workflow_setup import workflow_setup
from log_writer import log_writer
from config_validator import config_validator
  
import sys
  
inputArgs=sys.argv

def runInfraCommands():
  wfsys = workflow_system()
  wfpf = workflow_platform()
  wfst = workflow_service_type()
  lw = log_writer()
  cv = config_validator()
  ws = workflow_setup()

  lw.replaceLogFile()

  if cliproc.domain == 'setup':
    if cliproc.command == 'on':
      ws.runSetup()
    elif cliproc.command == 'off':
      ws.undoSetup()

  #Validating config after setup is completed because setup creates the config location
  if (cliproc.domain == 'platform') or (cliproc.domain == 'foundation') or (cliproc.domain == 'services') or (cliproc.domain == 'serviceType') or (cliproc.domain == 'serviceInstance'):
    cv.processAcmConfig()

  if cliproc.domain == 'platform':
    if cliproc.command == 'on':
      wfpf.onPlatform()
    elif cliproc.command == 'off': 
      wfpf.offPlatform()

  elif cliproc.domain == 'foundation':
    if cliproc.command == 'on':
      wfsys.callOnFoundationDirectly()
    elif cliproc.command == 'off':
      wfsys.callOffFoundationDirectly()

  elif cliproc.domain == 'services':
    if cliproc.command == 'on':
      wfsys.callOnServicesDirectly()
    elif cliproc.command == 'off':
      wfsys.callOffServicesDirectly()

  elif cliproc.domain == 'serviceType':
    if cliproc.command == 'on':
      wfst.callOnServiceDirectly('servicetype')
    elif cliproc.command == 'off':
      wfst.callOffServiceDirectly('servicetype')

  elif cliproc.domain == 'serviceInstance':
    if cliproc.command == 'on':
      wfst.callOnServiceDirectly('serviceinstance')
    elif cliproc.command == 'off':
      wfst.callOffServiceDirectly('serviceinstance')

  sys.exit(0)

##############################################################################
### Deploy Platform By Calling The Functions
##############################################################################

cliproc.processInputArgs(inputArgs)
runInfraCommands()

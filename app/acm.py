## Copyright 2023 Agile Cloud Institute (AgileCloudInstitute.io) as described in LICENSE.txt distributed with this repository.
## Start at https://github.com/AgileCloudInstitute/AgileCloudManager    

import config_cliprocessor as cliproc
from workflow_appliance import workflow_appliance
from workflow_system import workflow_system
from workflow_service_type import workflow_service_type
from workflow_setup import workflow_setup
from log_writer import log_writer
from config_validator import config_validator
    
import sys
    
inputArgs=sys.argv  

def runInfraCommands():
  wfsys = workflow_system()
  wfpf = workflow_appliance()
  wfst = workflow_service_type()
  lw = log_writer()
  cv = config_validator()
  ws = workflow_setup()
 
  if (cliproc.domain != 'unittest') and (cliproc.domain != 'version') :
    lw.replaceLogFile()

  if cliproc.domain == 'version':
    print(cliproc.inputVars.get('acmVersion'))

  if cliproc.domain == 'setup':
    if cliproc.command == 'on':
      ws.runSetup()
    elif cliproc.command == 'off':
      ws.undoSetup() 
 
  #Validating config after setup is completed because setup creates the config location
  if (cliproc.domain == 'appliance') or (cliproc.domain == 'foundation') or (cliproc.domain == 'services') or (cliproc.domain == 'serviceType') or (cliproc.domain == 'serviceInstance'):
    print("inside acm.py, about to call cv.processAcmConfig()")
    cv.processAcmConfig()

  if cliproc.domain == 'appliance':
    if cliproc.command == 'on':
      wfpf.onAppliance()
    elif cliproc.command == 'off': 
      wfpf.offAppliance()

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
      print("in acm.py, about to wfst.callOnServiceDirectly()")
      wfst.callOnServiceDirectly('servicetype')
    elif cliproc.command == 'off':
      wfst.callOffServiceDirectly('servicetype')

  elif cliproc.domain == 'serviceInstance':
    if cliproc.command == 'on':
      wfst.callOnServiceDirectly('serviceinstance')
    elif cliproc.command == 'off':
      wfst.callOffServiceDirectly('serviceinstance')

  if cliproc.domain != 'unittest' :
    sys.exit(0)

##############################################################################
### Deploy appliance By Calling The Functions
##############################################################################

cliproc.processInputArgs(inputArgs) 

runInfraCommands()
